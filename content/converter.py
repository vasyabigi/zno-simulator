import string

import tomd
import lxml.html.clean as clean
from bs4 import BeautifulSoup

cleaner = clean.Cleaner(
    safe_attrs_only=True, safe_attrs=frozenset(), remove_tags=["em", "a"]
)

QUESTION_TYPE_URL_TO_KIND = {
    "/dovidka/viditestiv/1/": "single-choice",
    "/dovidka/viditestiv/5/": "multiple-choice",
}

MAX_TEXT_LENGTH = 3600

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
        soup_txt = cleaner.clean_html(str(soup).replace("\n", ""))
        html = f"<p>{soup_txt}</p>" if "</p>" not in soup_txt else soup_txt
        output = tomd.convert(html)
        output = output.strip("\n").strip(" ")
        output = output.replace("<br>", "\n")
        return output

    def is_valid(self):
        """
        Checks if question is valid for our internal use-cases.
        Currently, we're supporing single-choice questions with limitted length only.

        """
        is_supported = self.get_question_kind() in SUPPORTED_QUESTION_TYPES
        is_too_long = (
            len(self.get_content()) > MAX_TEXT_LENGTH
            or len(self.get_explanation()) > MAX_TEXT_LENGTH
        )

        return is_supported and not is_too_long

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
        explanation = self.content_post.find("div", attrs={"class": "explanation"})

        if not explanation:
            return ""

        return self.soup_to_markdown(explanation)
