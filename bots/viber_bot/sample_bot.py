from flask import Flask, request, Response

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

import time
import logging
import sched
import threading

from viberbot.api.messages import (
    TextMessage,
    ContactMessage,
    PictureMessage,
    VideoMessage
)

from viberbot.api.messages.data_types.contact import Contact


# creation of text message
text_message = TextMessage(text="sample text message!")

# creation of contact message
contact = Contact(name="Viber user", phone_number="0123456789")
contact_message = ContactMessage(contact=contact)

# creation of picture message
picture_message = PictureMessage(text="Check this", media="https://beetroot.academy/wp-content/uploads/BA_Logo_PNG-transparency-1.png")

# creation of video message
video_message = VideoMessage(media="https://cdn.jpg.wtf/futurico/c2/78/1538121190-c278ad895b8b05f4326657938b3cb64c.mp4", size=4324)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

viber = Api(BotConfiguration(
  name='testznoukrbot',
  avatar='http://viber.com/avatar.jpg',
  auth_token='4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62'
))

app = Flask(__name__)

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))

    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data().decode('utf8'))

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        viber.send_messages(viber_request.sender.id, [
            contact_message # message
        ])
    elif isinstance(viber_request, ViberConversationStartedRequest) \
            or isinstance(viber_request, ViberSubscribedRequest) \
            or isinstance(viber_request, ViberUnsubscribedRequest):
        viber.send_messages(viber_request.sender.id, [
            TextMessage(None, None, viber_request.get_event_type())
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)


def set_webhook(viber):
    event_types = [
        "delivered",
        "seen",
        "failed",
        "subscribed",
        "unsubscribed",
        "conversation_started"
    ]

    viber.set_webhook('https://zserhii.pythonanywhere.com/viber-bot/', event_types)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8443, debug=True)

    # scheduler = sched.scheduler(time.time, time.sleep)
    # scheduler.enter(5, 1, set_webhook, (viber,))

    # t = threading.Thread(target=scheduler.run)
    # t.start()

    # context = ('mycert.pem', 'mycert.pem') 

    # app.run(host='127.0.0.1', port=8443, debug=True, ssl_context=context)
