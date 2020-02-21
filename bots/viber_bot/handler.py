import json
import logging
import config
import os

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from bot import configure_viber, viber_response

sentry_sdk.init(
    dsn=config.sentry_dsn,
    environment=config.stage,
    integrations=[AwsLambdaIntegration()],
)

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps("ok"),
}
ERROR_RESPONSE = {"statusCode": 500, "body": json.dumps("Oops, something went wrong!")}


def webhook(event, context):
    """
    Runs the Viber webhook.

    """
    logger.info("Event: {}".format(event))

    subject = event["pathParameters"].get("subject")
    viber = configure_viber(subject)

    if event.get("httpMethod") == "POST" and event.get("body"):
        logger.info("Message received")

        viber_response(
            viber,
            json.loads(event.get("body")),
            event.get("headers").get("X-Viber-Content-Signature"),
        )

        logger.info("Message sent")

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Viber bot webhook.
    """
    logger.info("Event: {}".format(event))

    subject = event["pathParameters"].get("subject")
    viber = configure_viber(subject)

    url = "https://{host}/{stage}/{subject}/".format(
        host=event.get("headers").get("Host"),
        stage=event.get("requestContext").get("stage"),
        subject=event["pathParameters"].get("subject"),
    )

    try:
        webhook = viber.set_webhook(url, config.event_types)

        logger.info(f"Webhook set to: {url}")
    except Exception as e:
        webhook = None

        logger.info(f"Webhook error with {url}: {e}")

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE
