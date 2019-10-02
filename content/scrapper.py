import json
import time
import asyncio
from itertools import chain
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from .config import API_BASE, SHOULD_SCRAPE_OSVITA_UA

API_EXAM_TEST_URL = urljoin(API_BASE, "users/znotest/highload/")

SUPPORTED_SUBJECTS = ["Українська мова і література"]


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def post(session, url, data):
    async with session.post(url, data=data) as response:
        return await response.text()


async def parse_osvita_ua_questions():
    print(f"START: ({time.strftime('%X')})")

    subject_questions = []
    async with aiohttp.ClientSession() as session:
        response_content = await fetch(session, API_BASE)
        soup = BeautifulSoup(response_content, "html.parser")

        for subject_data in soup.find_all(attrs={"class": "test-item"}):
            subject_questions.append(await parse_subject(session, subject_data))

    print(f"END: ({time.strftime('%X')})")

    return list(chain(*subject_questions))


async def parse_subject(session, subject_data):
    subject_title = subject_data.text.replace("\n", "")

    if subject_title not in SUPPORTED_SUBJECTS:
        return []

    subject_href = subject_data.attrs["href"]
    response_content = await fetch(session, f"{API_BASE}{subject_href}")

    subject_soup = BeautifulSoup(response_content, "html.parser")
    print(f"Subject: {subject_title}")

    tasks = []
    for exam_data in subject_soup.find_all("li", attrs={"class": "test-item"}):
        tasks.append(parse_exam_questions(session, exam_data, subject_title))

    exams_questions = await asyncio.gather(*tasks)

    return list(chain(*exams_questions))


async def parse_exam_questions(session, exam_data, subject_title):
    questions = []

    exam_href = exam_data.find("a").attrs["href"]
    exam_title = exam_data.find_all("a")[0].text.replace("\n", "")
    zno_test_id = [i for i in filter(None, exam_href.split("/"))][-1]

    if exam_title.startswith("Всі запитання"):
        return

    print(f"Started ({time.strftime('%X')}): {exam_title}")

    tasks = [
        fetch(session, f"{API_BASE}{exam_href}"),
        post(
            session,
            API_EXAM_TEST_URL,
            data={"do": "send_all_serdata", "znotest": zno_test_id},
        ),
    ]

    response_get_content, response_post_content = await asyncio.gather(*tasks)

    exam_content_soup = BeautifulSoup(response_get_content, "html.parser")
    exam_post_content = json.loads(response_post_content)["result"]["quest"]
    exam_post_content_soup = BeautifulSoup(exam_post_content, "html.parser")

    for question_get_content in exam_content_soup.find_all(
        "div", attrs={"class": "task-card"}
    ):
        question_id = question_get_content.attrs["id"]
        question_post_content = exam_post_content_soup.find(
            "div", attrs={"id": question_id}
        )

        questions.append(
            {
                "subject": subject_title,
                "exam": exam_title,
                "content_get": str(question_get_content),
                "content_post": str(question_post_content),
            }
        )

    print(f"Finished ({time.strftime('%X')}): {exam_title}")

    # Save questions to local folder
    with open("raw_questions.json", "w") as f:
        json.dump(questions, f)

    return questions


async def get_osvita_ua_questions():
    if not SHOULD_SCRAPE_OSVITA_UA:
        with open("raw_questions.json", "r") as f:
            return json.loads(f.read())

    return await parse_osvita_ua_questions()
