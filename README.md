ZNO Simulator project
=======================

This project consists of 3 parts:
* [RESTful API](/api_service) - serves the ZNO quiz APIs;
* [Landing page](/landing_page_service) - serves the landing page of ZNO bots;
* [Telegram Bot](/bots/telegram_bot) - client to process ZNO API for Telegram bot;
* [Zno Parser](/zno_parser) - scrape, parse, and convert ZNO questions from zno.osvita.ua.

Dive into each of them to get more details.


### Code Style

To ensure a standardized code style we use the formatter [black](https://github.com/ambv/black).

If you want to automatically format your code on every commit, you can use [pre-commit](https://pre-commit.com/).
Just install it via `pip install pre-commit` and execute `pre-commit install` in the root folder.
This will add a hook to the repository, which reformats files on every commit.

If you want to set it up manually, install black via `pip install black`.
To reformat files execute
```
black .
```
