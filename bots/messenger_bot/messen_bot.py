from flask import Flask, request
import random
from pymessenger import Button
from pymessenger.bot import Bot
import requests
import json

QUESTIONS_API_ROOT = "http://zno-dev.eu-central-1.elasticbeanstalk.com/questions"
ACCESS_TOKEN = "EAAG04ZBRoPIgBANzttbQKz7EvNec8ZCbDKoNpbYNToZCoZCdr3eUPaoRUjHva5zJ0KWHtE4ZBZCoXuCaM662CFAxX3OWKYiDlccH8whdEaaVlOxvXlYljqRtUJ0gqiSgbYIPzpXfUJ6hYTTrRtHqZCSCCXQVC0vnvS4SC1U19C1DY2VFrV2oyQwZCHoZAbptZCaWoZD"
VERIFY_TOKEN = "TOKEN11111"

bot = Bot(ACCESS_TOKEN)
app = Flask(__name__)


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
                if message.get("postback"):
                    response_sent_text = (
                        f"your answer is {message['postback']['payload']}"
                    )
                    recipient_id = message["sender"]["id"]
                    send_message(recipient_id, response_sent_text)
                elif message.get("message"):
                    # определяем ID, чтобы знать куда отправлять ответ
                    recipient_id = message["sender"]["id"]
                    if message["message"].get("text"):
                        if message["message"]["text"] == "st":
                            send_message(recipient_id, get_question()[0])
                            for item in get_question()[1]:
                                buttons = [
                                    {
                                        "type": "postback",
                                        "payload": str(item["is_correct"]),
                                        "title": item["id"] + 1,
                                    }
                                ]
                                bot.send_button_message(
                                    recipient_id, item["content"], buttons
                                )
                        else:
                            response_sent_text = get_message()
                            send_message(recipient_id, response_sent_text)
                    # если пользователь отправил GIF, фото, видео и любой не текстовый объект
                    if message["message"].get("attachments"):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
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
    """Отправляет пользователю текстовое сообщение в соответствии с параметром response."""
    bot.send_text_message(recipient_id, response)
    return "success"


def get_message():
    """Отправляет случайные сообщения пользователю."""
    sample_responses = [
        "Потрясающе!",
        "Я вами горжусь!",
        "Продолжайте в том же духе!",
        "Лучшее, что я когда-либо видел!",
    ]
    return random.choice(sample_responses)


def get_question(subject="ukr"):
    get_all_page = requests.get(f"{QUESTIONS_API_ROOT}/random?subject={subject}")
    get_dict_with_question = json.loads(get_all_page.content)
    question_with_choices = []
    question_with_choices.append(get_dict_with_question["content"])
    question_with_choices.append(get_dict_with_question["choices"])
    return question_with_choices


if __name__ == "__main__":
    app.run(debug=True)
