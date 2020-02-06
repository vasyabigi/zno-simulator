from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import time
import logging
import sched
import threading

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
app = Flask(__name__)
viber = Api(
    BotConfiguration(
        name="Example from Beetroot",
        avatar="https://images.unsplash.com/photo-1566487097168-e91a4f38bee2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80",
        auth_token="4b06e1adaee7d102-894f265bf82a4a6a-182b92de2f9e38ee",
    )
)


@app.route("/", methods=["POST"])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    viber_request = viber.parse_request(request.get_data().decode("utf8"))
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        viber.send_messages(viber_request.sender.id, [message])
    elif (
        isinstance(viber_request, ViberConversationStartedRequest)
        or isinstance(viber_request, ViberSubscribedRequest)
        or isinstance(viber_request, ViberUnsubscribedRequest)
    ):
        viber.send_messages(
            viber_request.sender.id,
            [TextMessage(None, None, viber_request.get_event_type())],
        )
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(
            "client failed receiving message. failure: {0}".format(viber_request)
        )
    return Response(status=200)


@app.route("/set-webhook", methods=["GET"])
def register_webhook():
    viber.set_webhook(request.args["url"])
    logger.info(f"Webhook set to: {request.args['url']}")
    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
