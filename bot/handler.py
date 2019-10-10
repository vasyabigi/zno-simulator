import json
import telegram
import logging
import config

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from bot import configure_telegram

sentry_sdk.init(
    dsn=config.sentry_dsn,
    integrations=[AwsLambdaIntegration()]
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
    Runs the Telegram webhook.

    """
    bot_updater = configure_telegram()
    logger.info("Event: {}".format(event))

    if event.get("httpMethod") == "POST" and event.get("body"):
        logger.info("Message received")
        update = telegram.Update.de_json(json.loads(event.get("body")), bot_updater.bot)
        bot_updater.dispatcher.process_update(update)
        logger.info("Message sent")

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """
    logger.info("Event: {}".format(event))
    bot_updater = configure_telegram()
    url = "https://{}/{}/".format(
        event.get("headers").get("Host"), event.get("requestContext").get("stage")
    )
    webhook = bot_updater.bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE