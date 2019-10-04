import json
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from telegram.parsemode import ParseMode

import config
from api_utils import get_random_question, post_answer

EXPLANATION_STR = "Пояснення"
GREETING_STR = "Привіт! Напишіть /get щоб отримати питання!"
HELP_STR = "Напишіть /get щоб отримати питання."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    reply_keyboard = [["/get"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=GREETING_STR,
        reply_markup=markup
    )


def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    context.user_data.clear()

    question = get_random_question()
    keyboard = [
        [
            InlineKeyboardButton(
                letter,
                callback_data=question.choice_json(choice),
                parse_mode=ParseMode.MARKDOWN,
            )
            for letter, choice in zip(question.choices_letters, question.choices)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        question.question_str,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def get_explanation(query, answer):
    """Handle 'explain' button click."""
    query.edit_message_text(
        text=answer.explanation(query),
        parse_mode=ParseMode.MARKDOWN
    )


def handle_button(update, context):
    """Handle button click."""
    query = update.callback_query
    callback_data = json.loads(query.data)

    # checking if we have 'explain' button hit
    if context.user_data.get("answer"):
        get_explanation(query, context.user_data.pop("answer"))
        return

    answer = post_answer(callback_data["q_id"], callback_data["c_id"])

    context.user_data["answer"] = answer
    keyboard = [
        [
            InlineKeyboardButton(
                EXPLANATION_STR,
                callback_data=json.dumps(callback_data),
                parse_mode=ParseMode.MARKDOWN,
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=answer.marked_question_str(query, callback_data),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def handle_help(update, context):
    """Show short help message with list of available commands."""
    update.message.reply_text(HELP_STR)


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

    logger.info("Bot has been started and waiting for messages...")
    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
