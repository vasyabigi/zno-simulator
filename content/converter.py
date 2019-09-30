import string
import uuid

from bs4 import BeautifulSoup

QUESTION_TYPE_URL_TO_KIND = {
    "/dovidka/viditestiv/1/": "single-choice",
    "/dovidka/viditestiv/5/": "multiple-choice",
}

SUPPORTED_QUESTION_TYPES = ("single-choice",)


def raw_to_internal(raw_questions):
    questions = []

    for raw_question in raw_questions:
        question_converter = QuestionConverter(raw_question)

        if not question_converter.is_valid():
            continue

        questions.append(question_converter.to_internal())

    print(f"Converted {len(questions)}/{len(raw_questions)} questions.")

    return questions


class QuestionConverter:
    def __init__(self, raw_question):
        self.raw_question = raw_question
        self.content_get = BeautifulSoup(raw_question["content_get"], "html.parser")
        self.content_post = BeautifulSoup(raw_question["content_post"], "html.parser")

    def to_internal(self):
        return {
            "id": str(uuid.uuid4()),
            "subject": self.raw_question["subject"],
            "exam": self.raw_question["exam"],
            "kind": self.get_kind(),
            "choices": self.get_choices(),
            "content": self.get_content(),
            "explanation": self.get_explanation(),
        }

    def is_valid(self):
        return self.get_kind() in SUPPORTED_QUESTION_TYPES

    def get_kind(self):
        links = self.content_get.find_all("a")

        if not links:
            return

        type_url = links[-1].attrs["href"]
        return QUESTION_TYPE_URL_TO_KIND.get(type_url)

    def get_choices(self):
        dom_choices = self.content_post.find_all("div", attrs={"class": "q-item"})
        dom_answers = self.content_post.find_all("span", attrs={"class": "q-ans"})

        choices = []

        for index, dom_choice in enumerate(dom_choices):
            choices.append(
                {
                    "id": str(uuid.uuid4()),
                    "content": str(dom_choice),
                    "is_correct": "ok" in dom_answers[index].attrs["class"],
                }
            )

        if not dom_choices:
            for index, dom_answer in enumerate(dom_answers):
                choices.append(
                    {
                        "id": str(uuid.uuid4()),
                        "content": string.ascii_uppercase[index],
                        "is_correct": "ok" in dom_answers[index].attrs["class"],
                    }
                )

        return choices

    def get_content(self):
        return str(self.content_post.find("div", attrs={"class": "q-txt"}))

    def get_explanation(self):
        return str(self.content_post.find("div", attrs={"class": "explanation"}))
