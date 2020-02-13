import copy
from urllib.parse import urljoin

QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"
QUESTION_URL = urljoin(QUESTIONS_API_ROOT, "/questions/{id}")
ANSWER_URL = urljoin(QUESTIONS_API_ROOT, "/questions/{id}/answers")
CHECK_MARK_BUTTON = "✅"
CHECK_MARK_BLACK = "✔"
CROSS_MARK = "❌"
CROSS_MARK_BLACK = "✖"
QUESTION_MARK = "❓"
BOOK = "📖"
INDEX_POINTING_RIGHT = "👉"
YOUR_CHOICE_B = "Ви обрали:"
CHOICES_AVAILABLE_B = "Варіанти відповідей:"
CORRECT_ANSWER_B = "Правильна відповідь:"

START = "старт"
HELP = "допомога"
QUESTION = "питання"
GREETING_STR = f'Привіт! Напишіть "{QUESTION}" щоб отримати нове питання!'
HELP_STR = f'Напишіть "{QUESTION}" щоб отримати нове питання.'
EXPLANATION_STR = f"{BOOK} Пояснення"
QUESTION_BOOKS = "📚"
FACEPALM = "🤦‍♂️"
SORRY_ERROR = (
    f"{FACEPALM} Виникла помилка... Спробуйте ще раз, ми вже прикладаємо подорожник."
)
SHOW_ANSWER = f"{CHECK_MARK_BUTTON} Показати правильну відповідь"

CORRECT_CHOICE_STR = "- Ваша відповідь правильна!"
INCORRECT_CHOICE_STR = "- Ви помилились."

EMPTY_ACTION_BODY = {
    "operation": None,
    "question_id": None,
    "answer": None,
    "explanation": None,
    "attempt": 0,
}

EMPTY_KEYBOARD = {
    # "BgColor": "#FFFFFF",  # фон навколо кнопки
    "Type": "keyboard",
    "InputFieldState": "hidden",  # приховує поле вводу
    "Tracking_Data": "general_keyboard",
    "Buttons": [],
}

QUESTION_BUTTON = {
    "Columns": 6,
    "Rows": 1,
    "ActionType": "reply",
    "ActionBody": "get_question",
    # "BgColor": "#e6f5ff",
    "Text": f'{QUESTION_BOOKS} <font color="Black"><b>{str(QUESTION).title()}</b></font>',
}

ANSWER_BUTTON = {
    "Columns": 6,
    "Rows": 1,
    "ActionType": "reply",
    "ActionBody": "get_answer",
    # "BgColor": "#e6f5ff",
    "Text": f'<font color="Black"><b>{SHOW_ANSWER}</b></font>',
}

EXPLANATION_BUTTON = {
    "Columns": 6,
    "Rows": 1,
    "ActionType": "reply",
    "ActionBody": "get_explanation",
    # "BgColor": "#e6f5ff",
    "Text": f'<font color="Black"><b>{EXPLANATION_STR}</b></font>',
}  # See more: https://viber.github.io/docs/tools/keyboards/


def get_empty_keyboard():
    return copy.deepcopy(EMPTY_KEYBOARD)
