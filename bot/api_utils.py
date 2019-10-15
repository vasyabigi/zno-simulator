import json
import logging

import requests

from constants import (QUESTION_URL, ANSWER_URL, CHECK_MARK_BUTTON, CHECK_MARK_BLACK, CROSS_MARK,
                       CROSS_MARK_BLACK, QUESTION_MARK, INDEX_POINTING_RIGHT, BOOK,
                       CHOICES_AVAILABLE_B, YOUR_CHOICE_B, CORRECT_ANSWER_B)

logger = logging.getLogger(__name__)


def get_question(question_id=None, subject=None):
    """Get question from API."""
    q_id = question_id or 'random'
    logger.debug(f'Getting question from {QUESTION_URL.format(id=q_id)}')
    # TODO handle server status != 200
    api_response = requests.get(f'{QUESTION_URL.format(id=q_id)}?subject={subject}')
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

    @property
    def choices_letters(self):
        return [
            f'{choice["content"].split(":")[0].strip("*")}'
            for choice in self.choices
        ]

    def get_string(self):
        choices_str = '\n'.join(
            f'- {choice["content"]}' for choice in self.choices
        )
        return f'{QUESTION_MARK} {self.question["content"]}\n\n{INDEX_POINTING_RIGHT} ' \
               f'{CHOICES_AVAILABLE_B}\n{choices_str}'


class TelegramAnswer:
    """Class for handling api answer formatting for telegram message."""

    def __init__(self, answer_data):
        self.answer = json.loads(answer_data)

    def has_explanation(self):
        # TBD: Remove None from parsed content
        return self.answer['explanation'] and self.answer['explanation'] != 'None'

    def explanation(self, text_markdown):
        return f'{text_markdown}\n\n{BOOK} {self.answer["explanation"]}'

    @property
    def is_correct(self):
        return self.answer['is_correct']

    def get_selected_choice(self, message_text, selected_choice_id):
        """Get user choice with correct/incorrect mark."""
        selected_choice = self.selected_choice_str(selected_choice_id)
        message_text = message_text.split(f'\n\n{CROSS_MARK}')[0]
        return (
            f'{message_text}\n\n{self.get_mark()} {self._get_user_choice(selected_choice)}'
        )

    @staticmethod
    def _get_user_choice(selected_choice):
        return f'{YOUR_CHOICE_B} {selected_choice}'

    def selected_choice_str(self, selected_choice_id):
        [selected_choice] = [
            choice['content']
            for choice in self.answer['choices']
            if choice['id'] == selected_choice_id
        ]
        return selected_choice

    def get_verified_question(self, message_text, selected_choice_id):
        """Get question with marked choices and marked user answer."""
        question = self._extract_question_str(message_text)
        choices_string = self._get_marked_choices_str()

        selected_choice = self.selected_choice_str(selected_choice_id)
        return (
            f'{question}{CHOICES_AVAILABLE_B}\n{choices_string}\n\n{self.get_mark()} '
            f'{self._get_user_choice(selected_choice)}'
        )

    def _get_marked_choices_str(self):
        choices_string = '\n'.join(
            f'{self.get_black_mark(choice)} {choice["content"]}'
            for choice in self.answer["choices"]
        )
        return choices_string

    def get_verified_answer(self, message_text):
        """Get question with marked choices and correct answer."""
        question = self._extract_question_str(message_text)
        choices_string = self._get_marked_choices_str()
        [correct_choice] = [
            choice['content']
            for choice in self.answer['choices']
            if choice['is_correct'] is True
        ]
        return (
            f'{question}{CHOICES_AVAILABLE_B}\n{choices_string}\n\n{CHECK_MARK_BUTTON} '
            f'{CORRECT_ANSWER_B} {correct_choice}'
        )

    @staticmethod
    def _extract_question_str(message_text):
        question = message_text.split(f'{CHOICES_AVAILABLE_B}')[0]
        return question

    def get_mark(self):
        return CHECK_MARK_BUTTON if self.is_correct is True else CROSS_MARK

    @staticmethod
    def get_black_mark(choice):
        return CHECK_MARK_BLACK if choice['is_correct'] is True else CROSS_MARK_BLACK
