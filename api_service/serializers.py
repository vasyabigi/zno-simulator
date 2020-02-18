from enum import Enum

import markdown2


class Formats(Enum):
    HTML = "html"
    RAW = "raw"
    MARKDOWN = "markdown"


def markdown_to_html(text):
    return markdown2.markdown(text)


def markdown_to_raw(text):
    # TODO: improve method to deal with all markdown characters
    return text.replace("*", "")


def serialize_question(question_data, serialization_format):
    formatter = {
        Formats.HTML.value: markdown_to_html,
        Formats.MARKDOWN.value: lambda x: x,
        Formats.RAW.value: markdown_to_raw,
    }.get(serialization_format)

    return {
        "id": question_data["id"],
        "content": formatter(question_data["content"]),
        "image": question_data["image"],
        "explanation": formatter(question_data["explanation"]),
        "choices": [
            {
                "id": choice["id"],
                "content": formatter(choice["content"]),
                "is_correct": choice["is_correct"],
            }
            for choice in question_data["choices"]
        ],
    }
