import lxml.html as lxml_html
import lxml.html.clean as clean
import tomd
from bs4 import BeautifulSoup

from .scrapper import SUBJECTS_TO_CODES


cleaner = clean.Cleaner(
    safe_attrs_only=True, safe_attrs=frozenset(), remove_tags=["em", "a", "sup", "div"]
)

QUESTION_TYPE_URL_TO_KIND = {
    "/dovidka/viditestiv/1/": "single-choice",
    "/dovidka/viditestiv/5/": "multiple-choice",
}

FORMAT_TYPES = {

}

UA_LETTERS = "АБВГДЕЄЖЗ"

MAX_TEXT_LENGTH = 3600

SUPPORTED_QUESTION_TYPES = ("single-choice",)


class QuestionConverter:
    def __init__(self, index, raw_question, format='markdown'):
        self.index = index
        self.raw_question = raw_question
        self.content_get = BeautifulSoup(raw_question["content_get"], "html.parser")
        self.content_post = BeautifulSoup(raw_question["content_post"], "html.parser")
        self.formatter = {
            'html': self.soup_to_html,
            'markdown': self.soup_to_markdown,
            'raw': self.soup_to_raw_text
        }.get(format)

    def to_internal(self):
        # Extract image from the content
        image = self.get_image()

        return {
            "id": self.index,
            "subject": self.get_subject(),
            "exam": self.raw_question["exam"],
            "kind": self.get_question_kind(),
            "choices": self.get_choices(),
            "content": self.get_content(),
            "explanation": self.get_explanation(),
            "image": image,
        }

    @staticmethod
    def bulk_to_internal(raw_questions, format='raw'):
        """
        Converts raw html questions from osvita.ua to well-formatted json structure.

        """
        questions = []
        per_subject = {}
        for index, raw_question in enumerate(raw_questions):
            question_converter = QuestionConverter(index, raw_question, format=format)

            if not question_converter.is_valid():
                continue

            data = question_converter.to_internal()
            questions.append(data)

            per_subject.setdefault(data["subject"], 0)
            per_subject[data["subject"]] += 1

        for subject, value in per_subject.items():
            print(f"Converted {value} {subject} questions.")

        return questions

    @staticmethod
    def soup_to_html(soup, letter=False):
        soup_txt = cleaner.clean_html(str(soup).replace("\n", ""))
        output = soup_txt.strip("\n").strip(" ")
        output = output.replace("<br>", "\n")
        if letter:
            output = f'<strong>{output}</strong>'

        return output

    @staticmethod
    def soup_to_raw_text(soup, **kwargs):
        """
        Converts beautiful soup html into the raw text with no tags.

        """
        soup_txt = cleaner.clean_html(str(soup).replace("\n", ""))
        html_document = lxml_html.document_fromstring(soup_txt)
        output = html_document.text_content()

        return output

    @staticmethod
    def soup_to_markdown(soup, letter=False):
        """
        Converts beautiful soup html into the markdown format.

        """
        soup_txt = cleaner.clean_html(str(soup).replace("\n", ""))
        html = f"<p>{soup_txt}</p>" if "</p>" not in soup_txt else soup_txt
        output = tomd.convert(html)
        output = output.strip("\n").strip(" ")
        output = output.replace("<br>", "\n")
        if letter:
            output = f'*{output}*'

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

        too_many_images = len(self.content_post.find_all("img")) > 1

        return is_supported and not is_too_long and not too_many_images

    def get_question_kind(self):
        links = self.content_get.find_all("a")

        if not links:
            return

        type_url = links[-1].attrs["href"]
        return QUESTION_TYPE_URL_TO_KIND.get(type_url)

    def get_subject(self):
        return SUBJECTS_TO_CODES[self.raw_question["subject"]]

    def get_image(self):
        images = self.content_post.find("div", attrs={"class": "q-txt"}).find_all("img")

        if len(images) == 1:
            images[0].extract()
            return f"https://zno.osvita.ua{images[0].attrs['src']}"

    def get_choices(self):
        dom_choices = self.content_post.find_all("div", attrs={"class": "q-item"})
        dom_answers = self.content_post.find_all("span", attrs={"class": "q-ans"})

        choices = []

        for index, dom_choice in enumerate(dom_choices):
            letter = self.formatter(
                dom_choice.find("span", attrs={"class": "q-number"}).extract(),
                letter=True
            )

            choices.append(
                {
                    "id": index,
                    "content": f"{letter}: {self.formatter(dom_choice)}",
                    "is_correct": "ok" in dom_answers[index].attrs["class"],
                }
            )

        if not dom_choices:
            for index, dom_answer in enumerate(dom_answers):
                choices.append(
                    {
                        "id": index,
                        "content": UA_LETTERS[index],
                        "is_correct": "ok" in dom_answers[index].attrs["class"],
                    }
                )

        return choices

    def get_content(self):
        return self.formatter(
            self.content_post.find("div", attrs={"class": "q-txt"})
        )

    def get_explanation(self):
        explanation = self.content_post.find("div", attrs={"class": "explanation"})

        if not explanation:
            return ""

        return self.formatter(explanation)
