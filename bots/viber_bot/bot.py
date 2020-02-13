import json
import copy
import logging

from os import path
from flask import Flask, request, Response

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from viberbot.api.messages import (
    TextMessage,
    PictureMessage,
    RichMediaMessage,
)

from api_utils import get_question, get_question_by_id, get_answer

from constants import (
    QUESTION_BUTTON,
    ANSWER_BUTTON,
    EXPLANATION_BUTTON,
    EMPTY_KEYBOARD,
    get_empty_keyboard,
)

logging.basicConfig(level=logging.INFO, style="{")
logger = logging.getLogger("viber_bot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

CURRENT_PATH = path.dirname(path.realpath(__file__))

with open(path.join(CURRENT_PATH, "config", "ukr.token")) as token:
    TOKEN = token.read()

viber = Api(
    BotConfiguration(
        name="ЗНО бот",
        avatar="https://visti.rovno.ua/img/650/do-uvahi-rivnenskikh-shkolyariv-rozpochalasya-rees20200108_9177.jpg",
        auth_token=TOKEN,
    )
)

app = Flask(__name__)


@app.route("/set-webhook", methods=["GET"])
def register_webhook():
    viber.set_webhook(request.args["url"])
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
        request_message = viber_request.message
        request_text = request_message.text
        request_tracking = request_message.tracking_data
        response = None
        message = []

        keyboard = get_empty_keyboard()

        if request_text == "get_question":
            question = get_question("ukr")

            if question.image:
                message.append(PictureMessage(media=question.image))

            keyboard["Buttons"].extend(question.buttons)

            request_tracking = question.id
            response = question.text
        elif request_text == "get_explanation":
            question = get_question_by_id("ukr", request_tracking)

            response = question.explanation_text
        elif request_text == "get_answer":
            answer = get_answer(request_tracking)

            response = answer.correct_answer_text
        else:
            try:
                user_answer = json.loads(request_text)

                if "choice_id" in user_answer:
                    question_id = user_answer["question_id"]
                    choice_id = user_answer["choice_id"]

                    answer = get_answer(question_id, choice_id)

                    if answer.is_correct:
                        if answer.has_explanation:
                            keyboard["Buttons"].append(EXPLANATION_BUTTON)
                    else:
                        keyboard["Buttons"].append(ANSWER_BUTTON)

                    response = answer.user_answer_text(choice_id)
                else:
                    response = "Невідома команда:\n" + request_text
            except json.JSONDecodeError:
                response = "Невідома команда:\n" + request_text

        keyboard["Buttons"].append(QUESTION_BUTTON)

        message.append(
            TextMessage(
                tracking_data=request_tracking,
                text=response,
                keyboard=keyboard,
                min_api_version=4,
            )
        )

        viber.send_messages(viber_request.sender.id, message)
    elif (
        isinstance(viber_request, ViberConversationStartedRequest)
        or isinstance(viber_request, ViberSubscribedRequest)
        or isinstance(viber_request, ViberUnsubscribedRequest)
    ):
        # AttributeError: 'ViberConversationStartedRequest' object has no attribute 'sender'
        viber.send_messages(
            viber_request.sender.id,
            [TextMessage(None, None, viber_request.get_event_type())],
        )
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(
            "Client failed receiving message. Failure: {0}".format(viber_request)
        )

    return Response(status=200)


def main():
    app.run(host="localhost", port=8443, debug=True)


# viber://pa?chatURI=test_zno_ukr_bot
# http://localhost:8443/set-webhook?url=


if __name__ == "__main__":
    main()
