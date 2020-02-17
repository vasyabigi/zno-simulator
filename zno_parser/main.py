import json
import asyncio

from zno_parser.scrapper import get_osvita_ua_questions
from zno_parser.converter import QuestionConverter


async def main():
    raw_questions = await get_osvita_ua_questions()
    for format in ('html', 'markdown', 'raw'):
        converted_questions = QuestionConverter.bulk_to_internal(raw_questions)

        with open(f"questions_{format}.json", "w") as f:
            json.dump(converted_questions, f)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
