## Viber bot for zno simulator

### Install requirements:
```
pip install -r requirements.txt
```

### Запуск локального середовища:
1. Запустити локальний веб-сервер ```python bot.py```.
2. Активувати за допомогою [Ngrok](https://ngrok.com/) ```./ngrok http <Port>``` тунель між локальним веб-вервером і зовнішнім сайтом з підтримкою SSL. 
3. Зареєструвати веб-хук ```http://localhost:<Port>/set-webhook?url=<ssl_url>```, де ```<ssl_url>``` - посилання з логу Ngrok.