import json

from constants import (
    QUESTION_MARK,
    CHOICES_AVAILABLE_B,
    CHECK_MARK_BUTTON,
    CORRECT_ANSWER_B,
    YOUR_CHOICE_B,
    INDEX_POINTING_RIGHT,
    CROSS_MARK,
    CORRECT_CHOICE_STR,
    INCORRECT_CHOICE_STR,
    BOOK,
)


class Choice:
    def __init__(self, choice):
        self.id = choice["id"]
        self.content = choice["content"]
        self.is_correct = choice["is_correct"]

        item = choice["content"].split(":", 1)

        self.key = item[0]  # item[0].replace("*", "").lower()

        if len(item) > 1:
            self.value = item[1].strip()
        else:
            self.value = ""

    @property
    def text(self):
        key = self.key + ":"

        return key + " " + self.value  # + " (" + str(self.is_correct) + ")"


class Choices(list):
    def __init__(self, choices):
        super().__init__(choices)

        for index, item in enumerate(self):
            self[index] = Choice(item)

    @property
    def text(self):
        choices = ""

        for choice in self:
            choices += choice.text + "\n"

        return choices

    def get_keys(self):
        result = []

        for choice in self:
            result.append(choice.key)

        return tuple(result)


class Question:
    def __init__(self, question):
        self.id = question["id"]
        self.choices = Choices(question["choices"])
        self.content = question["content"]
        self.image = question["image"]
        self.explanation = question["explanation"]

    @property
    def text(self):
        return f"{QUESTION_MARK} {self.content}?\n\n{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}\n{self.choices.text}"

    @property
    def choices_text(self):
        return f"{INDEX_POINTING_RIGHT} {CHOICES_AVAILABLE_B}\n{self.choices.text}"

    @property
    def explanation_text(self):
        return f"{BOOK} {self.explanation}"

    @property
    def buttons(self):
        buttons = []

        for choice in self.choices:
            button = {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": json.dumps(
                    {
                        "question_id": self.id,
                        "choice_id": choice.id,
                        "is_correct": choice.is_correct,
                    }
                ),
                # "BgColor": "#EEEEEE",
                "Text": "<b>" + choice.key + "</b>",
            }

            buttons.append(button)

        return buttons


class Answer:
    def __init__(self, answer_response, choice_id=None):
        self.answer = json.loads(answer_response)

        self.question_id = self.answer["id"]
        self.choice_id = choice_id
        self.choices = Choices(self.answer["choices"])
        self.is_correct = self.answer["is_correct"]

    @property
    def has_explanation(self):
        if self.answer["explanation"]:
            result = True
        else:
            result = False

        return result

    @property
    def correct_answer_text(self):
        result = ""

        for choice in self.choices:
            if choice.is_correct:
                result = choice.content
                break

        return f"\n\n{CHECK_MARK_BUTTON} {CORRECT_ANSWER_B}\n\n{result}"

    def user_answer_text(self, user_choice_id):
        user_answer = None

        for choice in self.choices:
            if choice.id == user_choice_id:
                user_answer = choice
                break

        if self.is_correct:
            result = f"{CHECK_MARK_BUTTON} {YOUR_CHOICE_B}\n\n{user_answer.content}\n\n{CHECK_MARK_BUTTON} {CORRECT_CHOICE_STR}"
        else:
            result = f"{CROSS_MARK} {YOUR_CHOICE_B}\n\n{user_answer.content}\n\n{CROSS_MARK} {INCORRECT_CHOICE_STR}"

        return result
