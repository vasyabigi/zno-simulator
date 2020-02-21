import logging

from os import path
from flask import Flask, request, Response

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

from viberbot.api.viber_requests import (
    ViberConversationStartedRequest,
    ViberFailedRequest,
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberUnsubscribedRequest,
)

from constants import QUESTION_BUTTON

from response_utils import (
    get_conversation_started_response,
    get_question_response,
    get_explanation_response,
    get_answer_response,
    check_answer_response,
)

logging.basicConfig(level=logging.INFO, style="{")
logger = logging.getLogger("viber_bot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

CURRENT_PATH = path.dirname(path.realpath(__file__))


def get_token(subject="test"):
    with open(path.join(CURRENT_PATH, "config", f"{subject}.token")) as token:
        return token.read()


subject = ["ukr"]
app = Flask(__name__)
viber = Api(BotConfiguration(name="ЗНО бот", avatar="", auth_token=get_token()))


@app.route("/set-webhook", methods=["GET"])
def register_webhook():
    event_types = [
        "subscribed",
        "unsubscribed",
        "message",
        "conversation_started",
    ]

    request_subject = request.args["subject"]

    if request_subject:
        subject.insert(0, request_subject)

        global viber
        viber = Api(
            BotConfiguration(
                name="ЗНО бот", avatar="", auth_token=get_token(request_subject)
            )
        )

        logger.info(f"Set subject: {request_subject}")

    viber.set_webhook(request.args["url"], event_types)
    logger.info(f"Webhook set to: {request.args['url']}")

    return Response(status=200)


@app.route("/", methods=["POST"])
def incoming():
    logger.debug(f"Received request. Post data: {request.get_data()}")

    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(
        request.get_data(), request.headers.get("X-Viber-Content-Signature")
    ):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data().decode("utf8"))

    if isinstance(viber_request, ViberMessageRequest):
        response_message = []

        if viber_request.message.text == "get_question":
            viber_response = get_question_response(
                viber_request, subject[0], response_message
            )

        elif viber_request.message.text == "get_explanation":
            viber_response = get_explanation_response(viber_request, subject[0])

        elif viber_request.message.text == "get_answer":
            viber_response = get_answer_response(viber_request)

        else:
            viber_response = check_answer_response(viber_request)

        viber_response.keyboard["Buttons"].append(QUESTION_BUTTON)

        response_message.append(viber_response.message)

        viber.send_messages(viber_request.sender.id, response_message)

    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber_response = get_conversation_started_response(viber_request)

        viber.send_messages(viber_request.user.id, [viber_response.message])

    elif isinstance(viber_request, ViberSubscribedRequest):
        logger.warn(f"User {viber_request.user_id} subscribed!")

    elif isinstance(viber_request, ViberUnsubscribedRequest):
        logger.warn(f"User {viber_request.user_id} unsubscribed!")

    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(f"Client failed receiving message. Failure: {viber_request}!")

    return Response(status=200)


def main():
    app.run(host="localhost", port=8443, debug=True)


if __name__ == "__main__":
    main()


# viber://pa?chatURI=test_zno_ukr_bot
# http://localhost:8443/set-webhook?subject=&url=
