import requests
import json

QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"


def get_question(subject):
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/random?subject={subject}")
    get_dict_with_question = json.loads(get_all_page.content)
    return get_dict_with_question
