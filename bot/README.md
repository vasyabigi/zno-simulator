## Telegram bot for zno simulator

install requirements:
```
pip install -r requirements.txt
```

run bot locally:
```
python3 main.py
```

Now you can open and test it out at 
[znosimulatorbot](https://t.me/znosimulatorbot)

TODO:
- [x] replace api calls mocks with real ones
- [x] add bot 'about' description:
> Телеграм-бот для підготовки до ЗНО.
- [x] add bot 'description' message: 
>Телеграм-бот для підготовки до ЗНО. Отримуйте запитання та пояснення до відповідей - перевірте свої знання. 
>Натисніть “Start” для початку.
- [X] show explanation on button click
- [ ] improve logging
- [ ] cyrillic text on `get` inline button(s) 
- [ ] update formatting after scraper fix
- [ ] add docker container
- [ ] rewrite using serverless 

IMPROVEMENTS:
- [ ] keep user statistics for session
- [ ] support subjects selection 