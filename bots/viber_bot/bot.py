import json
import logging

from os import path
from flask import Flask, request, Response

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from viberbot.api.messages import (
    TextMessage,
    PictureMessage,
    VideoMessage,
    RichMediaMessage,
)

logging.basicConfig(level=logging.INFO, style="{")
logger = logging.getLogger("viber_bot")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

CURRENT_PATH = path.dirname(path.realpath(__file__))

with open(path.join(CURRENT_PATH, ".token")) as token:
    TOKEN = token.read()

viber = Api(
    BotConfiguration(
        name="ЗНО бот (Українська мова)",
        avatar="https://visti.rovno.ua/img/650/do-uvahi-rivnenskikh-shkolyariv-rozpochalasya-rees20200108_9177.jpg",
        auth_token=TOKEN,
    )
)

app = Flask(__name__)


@app.route("/set-webhook", methods=["GET"])
def register_webhook():
    viber.set_webhook(request.args["url"])
    logger.info(f"Webhook set to: {request.args['url']}")
    return Response(status=200)


@app.route("/", methods=["POST"])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(
        request.get_data(), request.headers.get("X-Viber-Content-Signature")
    ):
        return Response(status=403)

    keyboard = {
        # "BgColor": "#FFFFFF",  # фон навколо кнопки
        "Type": "keyboard",
        # "InputFieldState": "hidden",  # приховує поле вводу
        "tracking_data": "general_keyboard",
        "Buttons": [
            {
                "Columns": 4,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "reply",
                # повідомлення, яке буде відправлено на сервер після натиснення відповідної кнопки
                "ActionBody": "get_question",
                # "ReplyType": "message",  # невідоме призначення
                # "BgColor": "#e6f5ff",  # фон кнопки
                "Text": '📚 <font color="Red"><b>ПИТАННЯ</b></font>',
                "TextSize": "large",
                "TextHAlign": "left",
                "TextVAlign": "center",
                "Image": "https://beetroot.academy/wp-content/uploads/BA_Logo_PNG-transparency-1.png",
            },
            {
                "Columns": 1,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "reply",
                # повідомлення, яке буде відправлено на сервер після натиснення відповідної кнопки
                "ActionBody": "get_help",
                # "ReplyType": "message",  # невідоме призначення
                # "BgColor": "#e6f5ff",  # фон кнопки
                "Text": "<b>?</b>",
                "TextOpacity": 60,
            },
            {
                "Columns": 1,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "BgMediaType": "gif",  # picture|gif, default - picture
                "BgMedia": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif",
                "BgLoop": True,  # циклічне повторення gif
                "ActionType": "open-url",  # reply|open-url|location-picker|share-phone|none, default - reply
                "ActionBody": "https://ru.wikipedia.org/wiki/GIF",
                # Possible tags: <b>|<i>|<u>|<br>|<s>|<font size=”N”> N between 12 and 32|<font color=”#7F00FF”>, double quotes in JSON should be escaped.
                "Text": '<font color="White">Текст</font>',
                "TextSize": "large",  # small|regular|large, default - regular
                "TextHAlign": "left",  # top|middle|bottom, default - middle
                "TextVAlign": "center",  # left|center|right, default - center
                "TextPaddings": [12, 12, 12, 12],  # per padding 0..12
                "Image": "https://beetroot.academy/wp-content/uploads/BA_Logo_PNG-transparency-1.png",
            },  # See more: https://viber.github.io/docs/tools/keyboards/
        ],
    }

    question = {
        # "BgColor": "#FFFFFF",  # фон навколо кнопки
        "Type": "rich_media",
        # "InputFieldState": "hidden",  # приховує поле вводу
        "tracking_data": "general_keyboard",
        "min_api_version": 4,
        "BgColor": "#FFFFFF",
        "Buttons": [
            {  # Question Text
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 2,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "❓ Уривок «Коло хати мати-зозуля кує мені розлуку. Довго-довго, не один десяток років буде проводжати мене мати, дивлячись крізь сльози з молитвами на зорях вечірніх і ранішніх, щоб не взяла мене ні куля, ні шабля, ні наклеп лихий» узятий із твору",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Answer Caption
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "👉 <b>Варіанти відповідей:<b>",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Choice 1
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "- <b>А</b>: «Три зозулі з поклоном» Григора Тютюнника",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Choice 2
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "- <b>Б</b>: «Зачарована Десна» Олександра Довженка",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Choice 3
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "- <b>В</b>: «Марія» Уласа Самчука",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Choice 4
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "- <b>Г</b>: «Тигролови» Івана Багряного",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {  # Choice 5
                "Columns": 6,  # ширина кнопки, максимум - 6
                "Rows": 1,  # висота кнопки, максимум - 2
                "ActionType": "none",
                "ActionBody": "none",
                "Text": "- <b>Д</b>: «Я (Романтика)» Миколи Хвильового",
                "TextHAlign": "left",
                "TextVAlign": "top",
            },
            {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": "choice_1",
                "BgColor": "#EEEEEE",
                "Text": "<b>А</b>",
            },
            {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": "choice_2",
                "BgColor": "#EEEEEE",
                "Text": "<b>Б</b>",
            },
            {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": "choice_3",
                "BgColor": "#EEEEEE",
                "Text": "<b>В</b>",
            },
            {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": "choice_4",
                "BgColor": "#EEEEEE",
                "Text": "<b>Г</b>",
            },
            {
                "Columns": 1,
                "Rows": 1,
                "ActionType": "reply",
                "ActionBody": "choice_5",
                "BgColor": "#EEEEEE",
                "Text": "<b>Д</b>",
            },
        ],
    }

    # q1 = {
    #     "receiver": "nsId6t9MWy3mq09RAeXiug==",
    #     "type": "rich_media",
    #     "min_api_version": 2,
    #     "rich_media": {
    #         "Type": "rich_media",
    #         "ButtonsGroupColumns": 6,
    #         "ButtonsGroupRows": 7,
    #         "BgColor": "#FFFFFF",
    #         "Buttons": [
    #             {
    #                 "Columns": 6,
    #                 "Rows": 3,
    #                 "ActionType": "open-url",
    #                 "ActionBody": "https://www.google.com",
    #                 "Image": "http://html-test:8080/myweb/guy/assets/imageRMsmall2.png"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 2,
    #                 "Text": "<font color=#323232><b>Headphones with Microphone, On-ear Wired earphones</b></font><font color=#777777><br>Sound Intone </font><font color=#6fc133>$17.99</font>",
    #                 "ActionType": "open-url",
    #                 "ActionBody": "https://www.google.com",
    #                 "TextSize": "medium",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "left"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 1,
    #                 "ActionType": "reply",
    #                 "ActionBody": "https://www.google.com",
    #                 "Text": "<font color=#ffffff>Buy</font>",
    #                 "TextSize": "large",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "middle",
    #                 "Image": "https://s14.postimg.org/4mmt4rw1t/Button.png"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 1,
    #                 "ActionType": "reply",
    #                 "ActionBody": "https://www.google.com",
    #                 "Text": "<font color=#8367db>MORE DETAILS</font>",
    #                 "TextSize": "small",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "middle"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 3,
    #                 "ActionType": "open-url",
    #                 "ActionBody": "https://www.google.com",
    #                 "Image": "https://s16.postimg.org/wi8jx20wl/image_RMsmall2.png"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 2,
    #                 "Text": "<font color=#323232><b>Hanes Men's Humor Graphic T-Shirt</b></font><font color=#777777><br>Hanes</font><font color=#6fc133>$10.99</font>",
    #                 "ActionType": "open-url",
    #                 "ActionBody": "https://www.google.com",
    #                 "TextSize": "medium",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "left"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 1,
    #                 "ActionType": "reply",
    #                 "ActionBody": "https://www.google.com",
    #                 "Text": "<font color=#ffffff>Buy</font>",
    #                 "TextSize": "large",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "middle",
    #                 "Image": "https://s14.postimg.org/4mmt4rw1t/Button.png"
    #             },
    #             {
    #                 "Columns": 6,
    #                 "Rows": 1,
    #                 "ActionType": "reply",
    #                 "ActionBody": "https://www.google.com",
    #                 "Text": "<font color=#8367db>MORE DETAILS</font>",
    #                 "TextSize": "small",
    #                 "TextVAlign": "middle",
    #                 "TextHAlign": "middle"
    #             }
    #         ]
    #     }
    # }

    viber_request = viber.parse_request(request.get_data().decode("utf8"))

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        text = message.text
        text_message = ""

        if text == "get_question":
            text_message = "Нове запитання"
        elif text == "get_help":
            text_message = "Вам допоможуть"
        else:
            text_message = text

        viber.send_messages(
            viber_request.sender.id,
            [
                RichMediaMessage(
                    rich_media=question, alt_text="SAMPLE_ALT_TEXT", min_api_version=4,
                ),
                TextMessage(text=text_message, keyboard=keyboard, min_api_version=4,),
            ],
        )
    elif (
        isinstance(viber_request, ViberConversationStartedRequest)
        or isinstance(viber_request, ViberSubscribedRequest)
        or isinstance(viber_request, ViberUnsubscribedRequest)
    ):
        viber.send_messages(
            viber_request.sender.id,
            [TextMessage(None, None, viber_request.get_event_type())],
        )
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(
            "client failed receiving message. failure: {0}".format(viber_request)
        )

    return Response(status=200)


def main():
    app.run(host="0.0.0.0", port=8443, debug=True)


# http://0.0.0.0:8443/set-webhook?url=https://___.ngrok.io/

if __name__ == "__main__":
    main()
