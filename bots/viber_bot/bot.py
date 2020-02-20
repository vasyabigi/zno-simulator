import json
import logging

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

import config

from constants import (
    BOT_NAME,
    BOT_AVATAR,
    QUESTION_BUTTON,
)

from response_utils import (
    ViberResponseTextMessage,
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


def configure_viber(subject="ukr"):
    return Api(
        BotConfiguration(
            name=BOT_NAME, avatar=BOT_AVATAR, auth_token=config.viber_tokens[subject]
        )
    )


def viber_response(viber, request_data, request_headers_signature):
    logger.debug(f"Received request. Post data: {request_data}")

    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request_data, request_headers_signature):
        return Response(status=403)

    bot_request = viber.parse_request(request_data.decode("utf8"))

    if isinstance(bot_request, ViberMessageRequest):
        response_message = []

        if bot_request.message.text == "get_question":
            bot_response = get_question_response(viber, bot_request, response_message)

        elif bot_request.message.text == "get_explanation":
            bot_response = get_explanation_response(viber, bot_request)

        elif bot_request.message.text == "get_answer":
            bot_response = get_answer_response(viber, bot_request)

        else:
            bot_response = ViberResponseTextMessage(bot_request)

            try:
                user_answer = json.loads(bot_response.text)

                if "choice_id" in user_answer:
                    bot_response = check_answer_response(viber, bot_request)
                else:
                    bot_response.text = "Невідома команда:\n" + bot_response.text
            except json.JSONDecodeError:
                bot_response.text = "Невідома команда:\n" + bot_response.text

        bot_response.keyboard["Buttons"].append(QUESTION_BUTTON)

        response_message.append(bot_response.message)

        viber.send_messages(bot_request.sender.id, response_message)

    elif isinstance(bot_request, ViberConversationStartedRequest):
        bot_response = get_conversation_started_response(viber, bot_request)

        viber.send_messages(bot_request.user.id, [bot_response.message])

    elif isinstance(bot_request, ViberSubscribedRequest):
        logger.warn(f"User {bot_request.user_id} subscribed!")

    elif isinstance(bot_request, ViberUnsubscribedRequest):
        logger.warn(f"User {bot_request.user_id} unsubscribed!")

    elif isinstance(bot_request, ViberFailedRequest):
        logger.warn(f"Client failed receiving message. Failure: {bot_request}!")

    return Response(status=200)


app = Flask(__name__)
viber = configure_viber()


@app.route("/set-webhook", methods=["GET"])
def register_webhook():
    subject = request.args["subject"]
    url = request.args["url"]

    if subject:
        global viber
        viber = configure_viber(subject)

        logger.info(f"Set subject: {subject}")

    try:
        viber.set_webhook(url, config.event_types)

        logger.info(f"Webhook set to: {url}")
    except Exception as e:
        logger.info(f"Webhook error with {url}: {e}")

    return Response(status=200)


@app.route("/", methods=["POST"])
def incoming():
    return viber_response(
        viber, request.get_data(), request.headers.get("X-Viber-Content-Signature")
    )


def main():
    app.run(host="localhost", port=8443, debug=True)


if __name__ == "__main__":
    main()


# viber://pa?chatURI=zno_mathematics_bot
# http://localhost:8443/set-webhook?subject=ukr&url=
# http://localhost:8443/set-webhook?subject=ukr&url=https://b51297c8.ngrok.io
