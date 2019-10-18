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
    def load_random_question(subject="ukr"):
        question_id = random.choice(QUESTIONS[subject])
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

SUBJECT_UKR = "ukr"
SUBJECT_MATH = "math"
SUBJECT_HIS = "his"
SUBJECT_GEO = "geo"
SUBJECT_BIO = "bio"
SUBJECT_PHYS = "phys"
SUBJECT_CHEM = "chem"
SUPPORTED_SUBJECTS_CODES = [
    SUBJECT_UKR,
    SUBJECT_MATH,
    SUBJECT_HIS,
    SUBJECT_GEO,
    SUBJECT_BIO,
    SUBJECT_PHYS,
    SUBJECT_CHEM,
]

QUESTIONS = {}
QUESTIONS_MAP = {}

for code in SUPPORTED_SUBJECTS_CODES:
    QUESTIONS[code] = [q["id"] for q in QUESTIONS_FROM_SERVER if q["subject"] == code]

QUESTIONS_MAP = {q["id"]: q for q in QUESTIONS_FROM_SERVER}
