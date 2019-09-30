import json
import asyncio

from .scrapper import get_osvita_ua_questions
from .converter import QuestionConverter


async def main():
    raw_questions = await get_osvita_ua_questions()
    converted_questions = QuestionConverter.bulk_to_internal(raw_questions)

    with open("questions.json", "w") as f:
        json.dump(converted_questions, f)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
