from urllib.parse import urljoin

import config

QUESTION_URL = urljoin(config.api_root, '/questions/{id}')
ANSWER_URL = urljoin(config.api_root, '/questions/{id}/answers')
CHECK_MARK_BUTTON = '✅'
CHECK_MARK_BLACK = '✔'
CROSS_MARK = '❌'
CROSS_MARK_BLACK = '✖'
QUESTION_MARK = '❓'
BOOK = '📖'
INDEX_POINTING_RIGHT = '👉'
YOUR_CHOICE_B = '*Ви обрали:*'
CHOICES_AVAILABLE_B = '*Варіанти відповідей:*'
CORRECT_ANSWER_B = '*Правильна відповідь:*'

START = 'старт'
HELP = 'допомога'
QUESTION = 'питання'
GREETING_STR = f'Привіт! Напишіть *{QUESTION}* щоб отримати нове питання!'
HELP_STR = f'Напишіть *{QUESTION}* щоб отримати нове питання.'
EXPLANATION_STR = f'{BOOK} Пояснення'
QUESTION_BOOKS = '📚'
FACEPALM = '🤦‍♂️'
SORRY_ERROR = f'{FACEPALM} Виникла помилка... Спробуйте ще раз, ми вже прикладаємо подорожник.'
SHOW_ANSWER = f'{CHECK_MARK_BUTTON} Показати правильну відповідь'

CORRECT_CHOICE_STR = '- Ваша відповідь правильна!'
INCORRECT_CHOICE_STR = '- Ви помилились.'
