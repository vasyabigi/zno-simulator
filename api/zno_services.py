import os
import json
import random

import requests

IS_FETCH_REQUIRED = os.environ.get("IS_FETCH_REQUIRED", False)
QUESTIONS_URL = (
    "https://much-better-adventures.s3.eu-central-1.amazonaws.com/questions.json"
)


class QuestionNotFoundError(Exception):
    """Custom exception should be raised when question with given id is not found."""
    pass


class QuestionsService:
    """Class designed for questions manipulations: load, check answers, etc."""

    @staticmethod
    def load_questions():
        if not IS_FETCH_REQUIRED:
            with open("questions.json", "r") as f:
                return json.loads(f.read())

        response = requests.get(QUESTIONS_URL)
        return json.loads(response.content)

    @staticmethod
    def load_random_question():
        question_id = random.choice(QUESTIONS)
        question_data = QUESTIONS_MAP[question_id]
        return question_data

    @staticmethod
    def load_question_by_id(q_id):
        try:
            return QUESTIONS_MAP[int(q_id)]
        except (KeyError, ValueError):
            raise QuestionNotFoundError

    @staticmethod
    def check_answers(question, user_choices):
        correct_choices = [
            choice["id"] for choice in question["choices"] if choice["is_correct"]
        ]
        return sorted(correct_choices) == sorted(user_choices)


QUESTIONS_FROM_SERVER = QuestionsService.load_questions()
QUESTIONS = [q["id"] for q in QUESTIONS_FROM_SERVER]
QUESTIONS_MAP = {q["id"]: q for q in QUESTIONS_FROM_SERVER}
