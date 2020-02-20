import copy
import json

from viberbot.api.messages import TextMessage, PictureMessage

# from amplitude import log_event

from constants import (
    IMAGE_URL,
    THUMBNAIL_URL,
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
    get_subject_code,
)


class ViberResponseTextMessage:
    def __init__(self, request, keyboard=None, min_api_version=4):
        if hasattr(request, "message"):
            self.tracking_data = request.message.tracking_data
            self.text = request.message.text
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
    def __init__(self, request, question_id, keyboard=None, min_api_version=4):
        super().__init__(request, keyboard, min_api_version)

        self.question_id = question_id

    @property
    def message(self):
        return PictureMessage(
            tracking_data=self.tracking_data,
            keyboard=self.keyboard,
            text=self.text,
            media=IMAGE_URL.format(id=self.question_id),
            thumbnail=THUMBNAIL_URL.format(id=self.question_id),
            min_api_version=self.min_api_version,
        )


def get_conversation_started_response(bot, request):
    if request.user:
        user_name = request.user.name
    else:
        user_name = ANONYMOUS_USER

    if request.subscribed:
        subscribed_status = SUBSCRIBED_GREETING.format(name=user_name)
    else:
        subscribed_status = NOT_SUBSCRIBED_GREETING.format(
            name=user_name, button_name=QUESTION_STR
        )

    response = ViberResponseTextMessage(request)

    response.text = subscribed_status

    response.keyboard["Buttons"].append(QUESTION_BUTTON)

    return response


# @log_event("get_random_question")
def get_question_response(bot, request, response_message):
    subject = get_subject_code(bot)
    question = get_question(subject)

    if question.image and question.content:
        response_message.append(
            PictureMessage(
                media=IMAGE_URL.format(id=question.id),
                thumbnail=THUMBNAIL_URL.format(id=question.id),
            )
        )

    if question.image and not question.content:
        response = ViberResponsePictureMessage(request, question.id)

        response.text = f"{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}"
    else:
        response = ViberResponseTextMessage(request)

        response.text = question.text

    response.tracking_data = question.id
    response.keyboard["Buttons"].extend(question.buttons)

    return response


# @log_event("show_explanation")
def get_explanation_response(bot, request):
    subject = get_subject_code(bot)
    response = ViberResponseTextMessage(request)

    question = get_question_by_id(subject, response.tracking_data)

    response.text = question.explanation_text

    return response


# @log_event("show_correct_answer")
def get_answer_response(bot, request):
    response = ViberResponseTextMessage(request)

    answer = get_answer(response.tracking_data)

    response.text = answer.correct_answer_text

    return response


# @log_event("send_answer", keys=["is_correct"])
def get_answer_result(bot, request):
    response = ViberResponseTextMessage(request)

    user_answer = json.loads(response.text)

    question_id = user_answer["question_id"]
    choice_id = user_answer["choice_id"]

    return get_answer(question_id, choice_id)


def check_answer_response(bot, request):
    answer = get_answer_result(bot, request)

    response = ViberResponseTextMessage(request)

    if answer.is_correct:
        if answer.has_explanation:
            response.keyboard["Buttons"].append(EXPLANATION_BUTTON)
    else:
        response.keyboard["Buttons"].append(ANSWER_BUTTON)

    response.text = answer.user_answer_text(answer.choice_id)

    return response
