import re
import string
import uuid

import html2text
import lxml.html.clean as clean
from bs4 import BeautifulSoup

cleaner = clean.Cleaner(
    safe_attrs_only=True, safe_attrs=frozenset(), remove_tags=["em"]
)

markdown = html2text.HTML2Text()

QUESTION_TYPE_URL_TO_KIND = {
    "/dovidka/viditestiv/1/": "single-choice",
    "/dovidka/viditestiv/5/": "multiple-choice",
}

SUPPORTED_QUESTION_TYPES = ("single-choice",)


class QuestionConverter:
    def __init__(self, index, raw_question):
        self.index = index
        self.raw_question = raw_question
        self.content_get = BeautifulSoup(raw_question["content_get"], "html.parser")
        self.content_post = BeautifulSoup(raw_question["content_post"], "html.parser")

    def to_internal(self):
        return {
            "id": self.index,
            "subject": self.raw_question["subject"],
            "exam": self.raw_question["exam"],
            "kind": self.get_question_kind(),
            "choices": self.get_choices(),
            "content": self.get_content(),
            "explanation": self.get_explanation(),
        }

    @staticmethod
    def bulk_to_internal(raw_questions):
        """
        Converts raw html questions from osvita.ua to well-formatted json structure.

        """
        questions = []

        for index, raw_question in enumerate(raw_questions):
            question_converter = QuestionConverter(index, raw_question)

            if not question_converter.is_valid():
                continue

            questions.append(question_converter.to_internal())

        print(f"Converted {len(questions)}/{len(raw_questions)} questions.")

        return questions

    @staticmethod
    def soup_to_markdown(soup):
        """
        Converts beautiful soup html into the markdown format.

        """
        output = markdown.handle(cleaner.clean_html(str(soup)))

        if output.startswith("\n\n"):
            output = output[2:]

        if output.endswith("\n\n"):
            output = output[:-2]

        p = re.compile(r"[^n](\\n)[^\\]")
        return p.sub(' ', output)

    def is_valid(self):
        """
        Checks if question is valid for our internal use-cases.
        Currently, we're supporing single-choice questions with limitted length only.

        """
        return self.get_question_kind() in SUPPORTED_QUESTION_TYPES

    def get_question_kind(self):
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
            letter = self.soup_to_markdown(
                dom_choice.find("span", attrs={"class": "q-number"}).extract()
            )

            choices.append(
                {
                    "id": index,
                    "content": f"*{letter}*: {self.soup_to_markdown(dom_choice)}",
                    "is_correct": "ok" in dom_answers[index].attrs["class"],
                }
            )

        if not dom_choices:
            for index, dom_answer in enumerate(dom_answers):
                choices.append(
                    {
                        "id": index,
                        "content": string.ascii_uppercase[index],
                        "is_correct": "ok" in dom_answers[index].attrs["class"],
                    }
                )

        return choices

    def get_content(self):
        return self.soup_to_markdown(
            self.content_post.find("div", attrs={"class": "q-txt"})
        )

    def get_explanation(self):
        return self.soup_to_markdown(
            self.content_post.find("div", attrs={"class": "explanation"})
        )
