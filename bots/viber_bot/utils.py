from requests import get
import json

URL_WITH_QUESTION = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions/random?subject=ukr"


def get_question():
    get_all_page = get(URL_WITH_QUESTION)
    page_text = json.loads(get_all_page.content)
    return page_text
