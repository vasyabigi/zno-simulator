# sethook

import requests
import json

# тут ваш токен полученный в начале #п.2
auth_token = "4b046ebf8327d166-6c30cb81186707f9-7693e8a5eb135f62"
hook = "https://chatapi.viber.com:443/pa/set_webhook"
headers = {"X-Viber-Auth-Token": auth_token}


sen = dict()

sen['url'] = 'https://f2fec829.ngrok.io/'
sen['event_types'] = [
        "unsubscribed",
        "conversation_started",
        "message",
        "seen",
        "delivered",
    ]

# sen - это body запроса для отправки к backend серверов viber
# seen, delivered - можно убрать, но иногда маркетологи хотят знать,
# сколько и кто именно  принял и почитал ваших сообщений,  можете оставить)

r = requests.post(hook, json.dumps(sen), headers=headers)
# r - это пост запрос составленный по требованиям viber

print(r.json())
# в ответном print мы должны увидеть "status_message":"ok" - и это значит,
#  что вебхук установлен
