import json
import logging

import requests
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
    logger.debug(f"Getting question from {config.get_question_url}")
    api_response = requests.get(config.get_question_url)
    logger.debug(
        f"API response {api_response.status_code} received: {api_response.content}"
    )
    return json.loads(api_response.content)


def _post_api_answer(question_id, choice_id):
    """Post chosen answer and get the response with details."""
    logger.debug(f"Sending answer to {config.post_answer_url}")
    api_response = requests.post(
        config.post_answer_url.format(id=question_id), json={"choices": [choice_id]}
    )
    logger.debug(
        f"API response {api_response.status_code} received: {api_response.content}"
    )
    return json.loads(api_response.content)


def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    reply_keyboard = [["/get"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Привіт! Напиши /get щоб отримати питання!",
        reply_markup=markup,
    )


def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    question = _get_api_question()
    keyboard = [
        [
            InlineKeyboardButton(
                choice["content"],
                callback_data=_get_choice_json(question, choice),
                parse_mode="Markdown",
            )
        ]
        for choice in question["choices"]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        _get_question_str(question), reply_markup=reply_markup, parse_mode="Markdown"
    )


def _get_choice_json(question, choice):
    return json.dumps({"c_id": choice["id"], "q_id": question["id"]})


def _get_question_str(question):
    choices_str = "\n".join(
        "- {}".format(choice["content"].strip("\n")) for choice in question["choices"]
    )
    # TODO: remove strip after api update
    return question["content"].strip("\n") + "\n\n" + choices_str


def _get_updated_question_str(query, answer, callback_data):
    # FIXME: investigate better way to separate question and choices
    question = "\n\n".join(query.message.text.split("\n\n")[0:-1])
    # TODO: remove strip after api update
    choices_string = "\n".join(
        "{mark} {choice}".format(
            mark=_get_black_mark(choice), choice=choice["content"].strip("\n")
        )
        for choice in answer["choices"]
    )

    [selected_choice] = [
        choice["content"]
        for choice in answer["choices"]
        if choice["id"] == callback_data["c_id"]
    ]
    return (
        f"{question}\n\n{choices_string}\n\n{_get_mark(answer)} "
        f"_Ви обрали: {selected_choice}_"
    )


def _get_mark(answer):
    return CHECK_MARK_BUTTON if answer["is_correct"] is True else CROSS_MARK


def _get_black_mark(choice):
    return CHECK_MARK_BLACK if choice["is_correct"] is True else CROSS_MARK_BLACK


def handle_button(update, context):
    """Handle button click."""
    query = update.callback_query
    callback_data = json.loads(query.data)
    answer = _post_api_answer(callback_data["q_id"], callback_data["c_id"])

    query.edit_message_text(
        text=_get_updated_question_str(query, answer, callback_data),
        parse_mode="Markdown",
    )
    context.bot.send_message(
        text=answer["explanation"], chat_id=query.message.chat_id, parse_mode="Markdown"
    )


def handle_help(update, context):
    """Show short help message with list of available commands."""
    update.message.reply_text("Напишіть /get щоб отримати питання.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", handle_start))
    updater.dispatcher.add_handler(CommandHandler("get", handle_get))
    updater.dispatcher.add_handler(CommandHandler("help", handle_help))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_start))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
