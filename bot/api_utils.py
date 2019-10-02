import json
import logging
from urllib.parse import urljoin

import requests

import config

logger = logging.getLogger(__name__)

QUESTION_URL = urljoin(config.api_root, "/questions/random")
ANSWER_URL = urljoin(config.api_root, "/questions/{id}/answers")

CHECK_MARK_BUTTON = "✅"
CHECK_MARK_BLACK = "✔"
CROSS_MARK = "❌"
CROSS_MARK_BLACK = "✖"


def get_random_question():
    """Get question from API."""
    logger.debug(f"Getting question from {QUESTION_URL}")
    # TODO handle server status != 200
    api_response = requests.get(QUESTION_URL)
    logger.debug(
        f"API response {api_response.status_code} received: {api_response.content}"
    )
    return TelegramQuestion(api_response.content)


def post_answer(question_id, choice_id):
    """Post chosen answer and get the response with details."""
    logger.debug(
        f"Sending answer {choice_id} for question {question_id} to {ANSWER_URL}"
    )
    # TODO handle server status != 200
    api_response = requests.post(
        ANSWER_URL.format(id=question_id), json={"choices": [choice_id]}
    )
    logger.debug(
        f"API response {api_response.status_code} received: {api_response.content}"
    )
    return TelegramAnswer(api_response.content)


class TelegramQuestion:
    """Class for handling api question for telegram message."""

    def __init__(self, question_data):
        self.question = json.loads(question_data)
        self.choices = self.question["choices"]

    def question_str(self):
        choices_str = "\n".join(
            "- {}".format(choice["content"].strip("\n"))
            for choice in self.choices
        )
        # TODO: remove strip after api update
        return self.question["content"].strip("\n") + "\n\n" + choices_str

    def choice_json(self, choice):
        return json.dumps({"c_id": choice["id"], "q_id": self.question["id"]})


class TelegramAnswer:
    """Class for handling api answer formatting for telegram message."""

    def __init__(self, answer_data):
        self.answer = json.loads(answer_data)

    @property
    def explanation(self):
        # TODO: remove strip
        return (
            self.answer["explanation"]
            if self.answer["explanation"].strip("\n") != "None"
            else "ъуъ!"
        )

    def marked_question_str(self, query, callback_data):
        # FIXME: investigate better way to separate question and choices
        question = "\n\n".join(query.message.text.split("\n\n")[0:-1])
        # TODO: remove strip after api update
        choices_string = "\n".join(
            "{mark} {choice}".format(
                mark=self.get_black_mark(choice), choice=choice["content"].strip("\n")
            )
            for choice in self.answer["choices"]
        )

        [selected_choice] = [
            choice["content"]
            for choice in self.answer["choices"]
            if choice["id"] == callback_data["c_id"]
        ]
        return (
            f"{question}\n\n{choices_string}\n\n{self.get_mark(self.answer)} "
            f"_Ви обрали: {selected_choice}_"
        )

    @staticmethod
    def get_mark(answer):
        return CHECK_MARK_BUTTON if answer["is_correct"] is True else CROSS_MARK

    @staticmethod
    def get_black_mark(choice):
        return CHECK_MARK_BLACK if choice["is_correct"] is True else CROSS_MARK_BLACK
