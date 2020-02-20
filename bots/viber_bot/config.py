import os
import json

# Set development variables as default values
viber_tokens = json.loads(
    os.getenv(
        "VIBER_TOKENS",
        '{"ukr": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","math": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","his": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","geo": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","bio": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","phys": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62","chem": "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62"}',
    )
)
api_root = os.getenv("API_ROOT", "http://zno-dev.eu-central-1.elasticbeanstalk.com")
sentry_dsn = os.getenv("SENTRY_DSN", None)
stage = os.getenv("STAGE")
amplitude_api_key = os.getenv("AMPLITUDE_API_KEY", None)

event_types = [
    "subscribed",
    "unsubscribed",
    "message",
    "conversation_started",
]
