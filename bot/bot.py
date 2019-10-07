import json
import logging
from functools import wraps

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ChatAction
)
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

EXPLANATION_STR = "📖 Пояснення"
QUESTION_STR = "питання"
QUESTION_BOOKS = '📚'
GREETING_STR = f"Привіт! Напишіть *{QUESTION_STR}* щоб отримати нове питання!"
HELP_STR = f"Напишіть *{QUESTION_STR}* щоб отримати нове питання."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id,
            action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


@send_typing_action
def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    reply_keyboard = [[f'{QUESTION_BOOKS} {QUESTION_STR}']]
    markup = ReplyKeyboardMarkup(
        reply_keyboard,
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=GREETING_STR,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )


@send_typing_action
def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    context.user_data.clear()

    question = get_random_question()
    context.user_data['q_id'] = question.q_id
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


def get_explanation(query, answer, message_id):
    """Handle 'explain' button click."""
    query.bot.edit_message_text(
        text=answer.explanation(query),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        parse_mode=ParseMode.MARKDOWN
    )


def handle_button(update, context):
    """Handle button click."""
    query = update.callback_query
    callback_data = json.loads(query.data)

    answer = post_answer(callback_data["q_id"], callback_data["c_id"])

    # checking if we have 'explain' button hit
    if callback_data.get('m_id'):
        get_explanation(query, answer, callback_data['m_id'])
        return

    message_id = update.effective_message.message_id
    callback_data.update({'m_id': message_id})
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
    update.message.reply_text(
        HELP_STR,
        parse_mode=ParseMode.MARKDOWN
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", handle_start))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("^(старт)$"), handle_start))

    updater.dispatcher.add_handler(CommandHandler("get", handle_get))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("^(?i).+(питання)?.+$"), handle_get))

    updater.dispatcher.add_handler(CommandHandler("help", handle_help))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex("^(допомога)$"), handle_help))
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
