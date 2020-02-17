from flask import Flask, request
from pymessenger import Button
from pymessenger.bot import Bot
import requests
import json

QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"
ACCESS_TOKEN = "EAAG04ZBRoPIgBANzttbQKz7EvNec8ZCbDKoNpbYNToZCoZCdr3eUPaoRUjHva5zJ0KWHtE4ZBZCoXuCaM662CFAxX3OWKYiDlccH8whdEaaVlOxvXlYljqRtUJ0gqiSgbYIPzpXfUJ6hYTTrRtHqZCSCCXQVC0vnvS4SC1U19C1DY2VFrV2oyQwZCHoZAbptZCaWoZD"
VERIFY_TOKEN = "TOKEN11111"

bot = Bot(ACCESS_TOKEN)
app = Flask(__name__)


BUTTONS = [
    {"type": "postback", "payload": "question", "title": "question"},
    {"type": "postback", "payload": "exit", "title": "exit"},
]


@app.route("/", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        # до того как позволить людям отправлять что-либо боту, Facebook проверяет маркер,
        # подтверждающий, что все запросы, получаемые ботом, приходят из Facebook
        token_sent = request.args["hub.verify_token"]
        return verify_fb_token(token_sent)
    # если запрос не был GET, это был POST-запрос и мы обрабатываем запрос пользователя
    else:
        # получаем сообщение, отправленное пользователем боту
        output = request.get_json()
        for event in output["entry"]:
            messaging = event["messaging"]
            for message in messaging:
                recipient_id = message["sender"]["id"]
                print(message)
                if message.get("postback"):
                    if message["postback"]["payload"] == "question":
                        send_message(recipient_id, get_question_str())
                        list_of_buttons = []
                        for item in get_question_list()[1]:
                            list_of_buttons.append(
                                {
                                    "content_type": "text",
                                    "title": item["id"] + 1,
                                    "payload": item["is_correct"],
                                }
                            )
                        bot.send_message(
                            recipient_id=recipient_id,
                            message={
                                "text": "Choices:",
                                "quick_replies": list_of_buttons,
                            },
                        )
                    elif message["postback"]["payload"] == "exit":
                        send_message(recipient_id, "You are the best!!!")
                        break
                if message.get("message"):
                    if message["message"].get("text"):
                        if message["message"]["text"] == "St":
                            send_message(recipient_id, get_question_str())
                            list_of_buttons = []
                            for item in get_question_list()[1]:
                                list_of_buttons.append(
                                    {
                                        "content_type": "text",
                                        "title": item["id"] + 1,
                                        "payload": item["is_correct"],
                                    }
                                )
                            bot.send_message(
                                recipient_id=recipient_id,
                                message={
                                    "text": "Choices:",
                                    "quick_replies": list_of_buttons,
                                },
                            )
                        else:
                            bot.send_button_message(recipient_id, "choices:", BUTTONS)
                    if message["message"].get("attachments"):
                        pass
                        # response_sent_nontext = get_message()
                        # send_message(recipient_id, response_sent_nontext)
        return "Message Processed"
    return "Hello World!"


def verify_fb_token(token_sent):
    """Сверяет токен, отправленный фейсбуком, с имеющимся у вас.
    При соответствии позволяет осуществить запрос, в обратном случае выдает ошибку."""
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    else:
        return "Invalid verification token"


def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"


def get_question_list(subject="ukr"):
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/random?subject={subject}")
    get_dict_with_question = json.loads(get_all_page.content)
    question_with_choices = []
    question_with_choices.append(get_dict_with_question["content"])
    question_with_choices.append(get_dict_with_question["choices"])
    return question_with_choices


def get_question_str(subject="ukr"):
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/random?subject={subject}")
    get_dict_with_question = json.loads(get_all_page.content)
    question_with_choices = ""
    question_with_choices += get_dict_with_question["content"] + "\n"
    for item in get_dict_with_question["choices"]:
        question_with_choices += item["content"] + "\n"
    return question_with_choices


if __name__ == "__main__":
    app.run(debug=True)
