import copy
import json

from viberbot.api.messages import TextMessage, PictureMessage

from constants import (
    QUESTION_STR,
    INDEX_POINTING_RIGHT,
    CHOICES_AVAILABLE_B,
    ANONYMOUS_USER,
    SUBSCRIBED_GREETING,
    NOT_SUBSCRIBED_GREETING,
    QUESTION_BUTTON,
    ANSWER_BUTTON,
    EXPLANATION_BUTTON,
    EMPTY_KEYBOARD,
)

from api_utils import (
    get_question,
    get_question_by_id,
    get_answer,
)


class ViberResponseTextMessage:
    def __init__(self, viber_request, keyboard=None, min_api_version=4):
        if hasattr(viber_request, "message"):
            self.tracking_data = viber_request.message.tracking_data
            self.text = viber_request.message.text
        else:
            self.tracking_data = None
            self.text = None

        self.min_api_version = min_api_version

        if keyboard:
            self.keyboard = keyboard
        else:
            self.keyboard = copy.deepcopy(EMPTY_KEYBOARD)

    @property
    def message(self):
        return TextMessage(
            tracking_data=self.tracking_data,
            keyboard=self.keyboard,
            text=self.text,
            min_api_version=self.min_api_version,
        )


class ViberResponsePictureMessage(ViberResponseTextMessage):
    def __init__(self, viber_request, media, keyboard=None, min_api_version=4):
        super().__init__(viber_request, keyboard, min_api_version)

        self.media = media

    @property
    def message(self):
        return PictureMessage(
            tracking_data=self.tracking_data,
            keyboard=self.keyboard,
            text=self.text,
            media=self.media,
            min_api_version=self.min_api_version,
        )


def get_conversation_started_response(viber_request):
    if viber_request.user:
        user_name = viber_request.user.name
    else:
        user_name = ANONYMOUS_USER

    if viber_request.subscribed:
        subscribed_status = SUBSCRIBED_GREETING.format(name=user_name)
    else:
        subscribed_status = NOT_SUBSCRIBED_GREETING.format(
            name=user_name, button_name=QUESTION_STR
        )

    viber_response = ViberResponseTextMessage(viber_request)

    viber_response.text = subscribed_status

    viber_response.keyboard["Buttons"].append(QUESTION_BUTTON)

    return viber_response


def get_question_response(viber_request, subject, response_message):
    question = get_question(subject)

    if question.image and question.content:
        response_message.append(PictureMessage(media=question.image))

    if question.image and not question.content:
        viber_response = ViberResponsePictureMessage(viber_request, question.image)

        viber_response.text = f"{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}"
    else:
        viber_response = ViberResponseTextMessage(viber_request)

        viber_response.text = question.text

    viber_response.tracking_data = question.id
    viber_response.keyboard["Buttons"].extend(question.buttons)

    return viber_response


def get_explanation_response(viber_request, subject):
    viber_response = ViberResponseTextMessage(viber_request)

    question = get_question_by_id(subject, viber_response.tracking_data)

    viber_response.text = question.explanation_text

    return viber_response


def get_answer_response(viber_request):
    viber_response = ViberResponseTextMessage(viber_request)

    answer = get_answer(viber_response.tracking_data)

    viber_response.text = answer.correct_answer_text

    return viber_response


def check_answer_response(viber_request):
    viber_response = ViberResponseTextMessage(viber_request)

    try:
        user_answer = json.loads(viber_response.text)

        if "choice_id" in user_answer:
            question_id = user_answer["question_id"]
            choice_id = user_answer["choice_id"]

            answer = get_answer(question_id, choice_id)

            if answer.is_correct:
                if answer.has_explanation:
                    viber_response.keyboard["Buttons"].append(EXPLANATION_BUTTON)
            else:
                viber_response.keyboard["Buttons"].append(ANSWER_BUTTON)

            viber_response.text = answer.user_answer_text(choice_id)
        else:
            viber_response.text = "Невідома команда:\n" + viber_response.text
    except json.JSONDecodeError:
        viber_response.text = "Невідома команда:\n" + viber_response.text

    return viber_response
