import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

import config

logger = logging.getLogger(__name__)

# I know it looks stupid but it works
CHECK_MARK_BUTTON = "✅"
CHECK_MARK_BLACK = "✔"
CROSS_MARK = "❌"
CROSS_MARK_BLACK = "✖"


def _get_api_question():
    """Get question from API."""
    return {
        "id": 1,
        "content": "На перший склад падає наголос у всіх словах, ОКРІМ",
        "choices": [
            {"id": 1, "content": "причіп"},
            {"id": 2, "content": "косий"},
            {"id": 3, "content": "жалюзі"},
            {"id": 4, "content": "випадок"},
        ],
    }


def _post_api_answer(choise_id):
    """Post chosen answer and get the response with details."""
    logger.info("send POST body: {choices: [id]}")
    return {
        "id": 1,
        "is_correct": True if choise_id == "3" else False,
        "choices": [
            {"id": 1, "content": "причіп", "is_correct": False},
            {"id": 2, "content": "косий", "is_correct": False},
            {"id": 3, "content": "жалюзі", "is_correct": True},
            {"id": 4, "content": "випадок", "is_correct": False},
        ],
        "explanation": "\n\n*ТЕМА: Орфоепія. Наголос, наголошені й ненаголошені склади.*\n\n"
        "Завдання перевіряє рівень ваших орфоепічних навичок.\n\n"
        "У подібних завданнях зовнішнього незалежного оцінювання завжди пропонують"
        "поширені слова, у яких часто трапляються помилки в наголошуванні. У 2018 році"
        "вперше учасникам ЗНО було рекомендовано перелік слів з наголосами. Цей"
        "своєрідний словник розміщено на сайті УЦОЯО в Програмі ЗНО.\n\n"
        "Правильно наголошені слова треба вимовляти так: пр *И* чіп, ,к *О* сий, в *И*"
        "падок, жалюз *І*.\n\n*Відповідь – В.*\n\n",
    }


def start(update, context):
    """Displaying the starting message when bot starts."""
    reply_keyboard = [["/get"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Привіт! Напиши /get щоб отримати питання!",
        reply_markup=markup,
    )


def get(update, context):
    """Send user a question and answers options keyboard."""
    question = _get_api_question()
    choices_string = "\n".join(f"- {q['content']}" for q in question["choices"])
    keyboard = [
        [InlineKeyboardButton(choice["content"], callback_data=choice["id"])]
        for choice in question["choices"]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        question["content"] + "\n\n" + choices_string,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


def button(update, context):
    """Handle button click."""
    query = update.callback_query
    answer = _post_api_answer(query.data)

    question = query.message.text.split("\n\n")[0]
    choices_list_marked = [
        f"{CHECK_MARK_BLACK if q['is_correct'] is True else CROSS_MARK_BLACK} {q['content']}"
        for q in answer["choices"]
    ]
    choices_string = "\n".join(choices_list_marked)
    mark = CHECK_MARK_BUTTON if answer["is_correct"] is True else CROSS_MARK
    [selected] = [
        choice["content"]
        for choice in answer["choices"]
        if choice["id"] == int(query.data)
    ]

    query.edit_message_text(
        text=f"{question}\n\n{choices_string}\n\n{mark} _Обрана відповідь: {selected}_",
        parse_mode="Markdown",
    )
    context.bot.send_message(
        text=answer["explanation"], chat_id=query.message.chat_id, parse_mode="Markdown"
    )


def help(update, context):
    """Show short help message with list of available commands."""
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("get", get))
    updater.dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, start))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
