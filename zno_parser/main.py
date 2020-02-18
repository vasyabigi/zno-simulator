import asyncio
import json

from zno_parser.config import Formats
from zno_parser.converter import QuestionConverter
from zno_parser.scrapper import get_osvita_ua_questions


async def main():
    raw_questions = await get_osvita_ua_questions()
    for format in [f.value for f in Formats]:
        converted_questions = QuestionConverter.bulk_to_internal(raw_questions, format)

        with open(f"questions_{format}.json", "w") as f:
            json.dump(converted_questions, f)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
