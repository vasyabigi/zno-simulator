import json
import requests

from api_utils import get_subject_code
from functools import wraps

from config import amplitude_api_key


API_ROOT = "https://api.amplitude.com/2/httpapi"


class AmplitudeLogger:
    def __init__(self, api_key):
        self.api_key = api_key

    def track(self, event_data):
        if not self.api_key:
            return

        headers = {"Content-Type": "application/json", "Accept": "*/*"}
        event_data = {"api_key": self.api_key, "events": [event_data]}
        requests.post(API_ROOT, data=json.dumps(event_data), headers=headers)


logger = AmplitudeLogger(amplitude_api_key)


def log_event(event_name, keys=None):
    """
    Log events in Amplitude to analyze key usage metrics about our users.

    """

    def log_event_decorator(func):
        @wraps(func)
        def wrapper(update, context):
            result = func(update, context)

            event_properties = {
                "platform": "telegram",
                "subject": get_subject_code(context),
            }

            if keys:
                for key in keys:
                    event_properties[key] = getattr(result, key)

            telegram_user = update._effective_user.to_dict()

            logger.track(
                {
                    "user_id": telegram_user["id"],
                    "event_type": event_name,
                    "user_properties": {
                        "name": f"{telegram_user.get('first_name')} {telegram_user.get('last_name')}",
                        "language_code": telegram_user.get("language_code"),
                    },
                    "event_properties": event_properties,
                }
            )

        return wrapper

    return log_event_decorator
