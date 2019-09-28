import json

from .scrapper import osvita_to_json
from .converter import raw_to_internal


def main():
    raw_questions = osvita_to_json()

    with open("raw_questions.json", "w") as f:
        json.dump(raw_questions, f)

    converted_questions = raw_to_internal(raw_questions)
    with open("questions.json", "w") as f:
        json.dump(converted_questions, f)

    print("Done, bro!")


if __name__ == "__main__":
    main()
