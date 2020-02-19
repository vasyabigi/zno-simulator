import requests
import json

from constants import (
    QUESTIONS_API_ROOT,
    ANSWER_URL,
)

from question import Question, Answer


def get_question(subject):
    question_json = requests.get(
        f"{QUESTIONS_API_ROOT}/random?subject={subject}&format=raw"
    )
    question_dict = json.loads(question_json.content)

    return Question(question_dict)


def get_question_by_id(subject, id):
    question_json = requests.get(f"{QUESTIONS_API_ROOT}/{id}?subject={subject}")
    question_dict = json.loads(question_json.content)

    return Question(question_dict)


def get_answer(question_id, choice_id=0):
    answer_response = requests.post(
        ANSWER_URL.format(id=question_id), json={"choices": [choice_id]}
    )

    return Answer(answer_response.content)
