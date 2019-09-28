# -*- coding: utf-8 -*-
import json

import requests
from bs4 import BeautifulSoup


API_BASE = "https://zno.osvita.ua/"

SUPPORTED_SUBJECTS = [u"Українська мова і література"]


def osvita_to_json():
    response = requests.get(API_BASE)
    soup = BeautifulSoup(response.content, "html.parser")

    questions = []

    for index, subject_data in enumerate(soup.find_all(attrs={"class": "test-item"})):
        subject_title = subject_data.text.replace("\n", "")

        if subject_title not in SUPPORTED_SUBJECTS:
            continue

        subject_href = subject_data.attrs["href"]
        response = requests.get("{}{}".format(API_BASE, subject_href))

        subject_soup = BeautifulSoup(response.content, "html.parser")

        print(u"Subject: {}".format(subject_title))

        for index, exam_data in enumerate(
            subject_soup.find_all("li", attrs={"class": "test-item"})
        ):
            exam_href = exam_data.find("a").attrs["href"]
            exam_title = exam_data.find_all("a")[0].text.replace("\n", "")

            if exam_title.startswith(u"Всі запитання"):
                continue

            print(u"Exam: {}".format(exam_title))

            response_get = requests.get("{}{}".format(API_BASE, exam_href))
            exam_content_soup = BeautifulSoup(response_get.content, "html.parser")

            zno_test_id = [i for i in filter(None, exam_href.split("/"))][-1]
            response_post = requests.post(
                "{}users/znotest/highload/".format(API_BASE),
                data={"do": "send_all_serdata", "znotest": zno_test_id},
            )

            exam_post_content = json.loads(response_post.content)["result"]["quest"]
            exam_post_content_soup = BeautifulSoup(exam_post_content, "html.parser")

            for index, question_get_content in enumerate(
                exam_content_soup.find_all("div", attrs={"class": "task-card"})
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

            print("Parsed {} questions.".format(index + 1))

    return questions
