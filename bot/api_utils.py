import json
import logging

import requests

from constants import (QUESTION_URL, ANSWER_URL, CHECK_MARK_BUTTON, CHECK_MARK_BLACK, CROSS_MARK,
                       CROSS_MARK_BLACK, QUESTION_MARK, INDEX_POINTING_RIGHT, BOOK,
                       CHOICES_AVAILABLE_B)

logger = logging.getLogger(__name__)


def get_question(question_id=None, subject=None):
    """Get question from API."""
    q_id = question_id or 'random'
    logger.debug(f'Getting question from {QUESTION_URL.format(id=q_id)}')

    # TODO Refactor the url getter
    url = QUESTION_URL.format(id=q_id)
    if subject:
        url += f'?subject={subject}'

    api_response = requests.get(url)

    logger.debug(
        f'API response {api_response.status_code} received: {api_response.content}'
    )
    return TelegramQuestion(api_response.content)


def post_answer(question_id, choice_id):
    """Post chosen answer and get the response with details."""
    logger.debug(
        f'Sending answer {choice_id} for question {question_id} to {ANSWER_URL}'
    )
    # TODO handle server status != 200
    api_response = requests.post(
        ANSWER_URL.format(id=question_id), json={'choices': [choice_id]}
    )
    logger.debug(
        f'API response {api_response.status_code} received: {api_response.content}'
    )
    return TelegramAnswer(api_response.content)


class TelegramQuestion:
    """Class for handling api question for telegram message."""

    def __init__(self, question_data):
        self.question = json.loads(question_data)
        self.q_id = self.question['id']
        self.choices = self.question['choices']
        self.image = self.question.get('image')

    @property
    def choices_letters(self):
        return [
            f'{choice["content"].split(":")[0].strip("*")}'
            for choice in self.choices
        ]

    @property
    def content(self):
        return f'{QUESTION_MARK} {self.question["content"]}\n\n'

    def choices_str(self):
        choices_str = '\n'.join(
            f'- {choice["content"]}' for choice in self.choices
        )
        return f'{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}\n{choices_str}'


class TelegramAnswer:
    """Class for handling api answer formatting for telegram message."""

    def __init__(self, answer_data):
        self.answer = json.loads(answer_data)
        self.is_correct = self.answer['is_correct']
        self.q_id = self.answer['id']
        self.choices = self.answer['choices']
        self.image = self.answer.get('image')

    @property
    def choices_letters(self):
        return [
            f'{choice["content"].split(":")[0].strip("*")}'
            for choice in self.choices
        ]

    @property
    def content(self):
        return f'{QUESTION_MARK} {self.answer["content"]}\n\n'

    def choices_str(self, verified=False):
        if verified:
            choices_str = self._get_marked_choices_str()
        else:
            choices_str = '\n'.join(
                f'- {choice["content"]}' for choice in self.choices
            )
        return f'{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}\n{choices_str}'

    @property
    def has_explanation(self):
        # TBD: Remove None from parsed content
        return True if self.answer['explanation'] else False

    @property
    def explanation(self):
        return f'\n\n{BOOK} {self.answer["explanation"]}'

    def selected_choice_str(self, selected_choice_id):
        [selected_choice] = [
            choice['content']
            for choice in self.answer['choices']
            if choice['id'] == selected_choice_id
        ]
        return selected_choice

    def _get_marked_choices_str(self):
        choices_string = '\n'.join(
            f'{self.get_black_mark(choice)} {choice["content"]}'
            for choice in self.answer["choices"]
        )
        return choices_string

    @property
    def mark(self):
        return CHECK_MARK_BUTTON if self.is_correct is True else CROSS_MARK

    @staticmethod
    def get_black_mark(choice):
        return CHECK_MARK_BLACK if choice['is_correct'] is True else CROSS_MARK_BLACK
