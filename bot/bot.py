import json
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
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
from api_utils import get_question, post_answer
from constants import (START, EXPLANATION_STR, QUESTION, QUESTION_BOOKS, GREETING_STR, HELP,
                       SORRY_ERROR, SHOW_ANSWER, HELP_STR)

logging.basicConfig(level=logging.INFO, style='{')
logger = logging.getLogger('zno_bot_ukrainian')


def get_choices_buttons(question):
    return (get_inline_button(letter, {
        'a': 'try',
        'c_id': choice['id'],  # choice id
        'q_id': question.q_id,  # question id
    })
        for letter, choice in zip(question.choices_letters, question.choices))


def get_inline_button(text, callback_data):
    return InlineKeyboardButton(
        text,
        callback_data=json.dumps(callback_data),
        parse_mode=ParseMode.MARKDOWN,
    )


def apply_show_explanation(update):
    """Handle 'explain' button click."""
    callback_data = json.loads(update.callback_query.data)
    answer = post_answer(callback_data['q_id'], callback_data['c_id'])

    logger.info('User {} - {} got explanation for question {}'.format(
        update._effective_user.id,
        update._effective_user.name,
        callback_data['q_id']
    ))

    query = update.callback_query
    query.bot.edit_message_text(
        text=answer.explanation(query.message.text_markdown),
        chat_id=query.message.chat_id,
        message_id=callback_data['m_id'],
        parse_mode=ParseMode.MARKDOWN
    )


def apply_show_correct_answer(update):
    """Handle 'show correct answer' button click."""
    callback_data = json.loads(update.callback_query.data)
    answer = post_answer(callback_data["q_id"], callback_data["c_id"])

    logger.info('User {} - {} got answer for question {}'.format(
        update._effective_user.id,
        update._effective_user.name,
        callback_data['q_id']
    ))

    reply_markup = None
    if answer.has_explanation():
        reply_markup = InlineKeyboardMarkup.from_button(
            get_inline_button(EXPLANATION_STR, callback_data={**callback_data, **{'a': 'exp'}})
        )

    query = update.callback_query
    query.bot.edit_message_text(
        text=answer.get_verified_answer(query.message.text_markdown),
        reply_markup=reply_markup,
        chat_id=query.message.chat_id,
        message_id=callback_data['m_id'],
        parse_mode=ParseMode.MARKDOWN
    )


def apply_send_answer(update):
    callback_data = json.loads(update.callback_query.data)
    answer = post_answer(callback_data["q_id"], callback_data["c_id"])

    if answer.is_correct:
        correct_answer_response(update, callback_data, answer)

    else:
        incorrect_answer_response(update, callback_data, answer)


def correct_answer_response(update, callback_data, answer):
    query = update.callback_query
    logger.info('User {} - {} got correct choice {} for question {}'.format(
        update._effective_user.id,
        update._effective_user.name,
        callback_data['c_id'],
        callback_data['q_id']
    ))
    message_text = answer.get_verified_question(
        query.message.text_markdown,
        callback_data['c_id']
    )
    callback_data.update({
        'a': 'exp',
        'm_id': update.effective_message.message_id
    })
    reply_markup = None
    if answer.has_explanation():
        reply_markup = InlineKeyboardMarkup.from_button(
            get_inline_button(EXPLANATION_STR, callback_data)
        )
    update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def incorrect_answer_response(update, callback_data, answer):
    query = update.callback_query
    logger.info('User {} - {} got incorrect choice {} for question {}'.format(
        update._effective_user.id,
        update._effective_user.name,
        callback_data['c_id'],
        callback_data['q_id'],
    ))

    message_text = answer.get_selected_choice(
        query.message.text_markdown,
        callback_data['c_id']
    )
    # avoid redundant update in case of the same wrong choice
    if message_text == query.message.text_markdown:
        return

    callback_data.update({
        'a': 'try',
        'm_id': update.effective_message.message_id
    })

    reply_markup = InlineKeyboardMarkup(
        [
            list(
                get_choices_buttons(get_question(question_id=callback_data['q_id']))
            ),
            [
                get_inline_button(SHOW_ANSWER, {**callback_data, **{'a': 'ans'}})
            ],
        ]
    )
    update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


SUPPORTED_ACTIONS = {
    'try': apply_send_answer,
    'ans': apply_show_correct_answer,
    'exp': apply_show_explanation,
}


def handle_button(update, context):
    """Handle button click."""
    callback_data = json.loads(update.callback_query.data)
    # Select action:
    apply_action = SUPPORTED_ACTIONS[callback_data['a']]
    # Apply action:
    apply_action(update)


def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    logger.info('Started chat %s with user {} - {}',
                update._effective_chat.id,
                update._effective_user.id,
                update._effective_user.name
                )

    markup = ReplyKeyboardMarkup(
        keyboard=[[f'{QUESTION_BOOKS} {QUESTION}']],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=GREETING_STR,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )


def get_subject_code(context):
    # TODO: Fix the subject getter
    for key, value in config.telegram_tokens.items():
        if value == context.bot.token:
            return key


def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    subject = get_subject_code(context)
    question = get_question(subject=subject)

    logger.info('User {} - {} got question {}'.format(
        update._effective_user.id,
        update._effective_user.name,
        question.q_id
    ))

    reply_markup = InlineKeyboardMarkup.from_row(
        get_choices_buttons(question)
    )
    update.message.reply_text(
        question.get_string(),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


def handle_help(update, context):
    """Show short help message with list of available commands."""
    logger.info('User {} - {} got help'.format(
        update._effective_user.id,
        update._effective_user.name
    ))
    update.message.reply_text(
        HELP_STR,
        parse_mode=ParseMode.MARKDOWN
    )


def handle_error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update {} caused error {}'.format(update, context.error))
    chat_id = context.effective_chat.id if hasattr(context, 'effective_chat') \
        else update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=SORRY_ERROR,
        parse_mode=ParseMode.MARKDOWN
    )


def configure_telegram(subject):
    updater = Updater(config.telegram_tokens[subject], use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', handle_start))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(f'^({START})$'), handle_start))

    updater.dispatcher.add_handler(CommandHandler('get', handle_get))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.regex(f'^(?i)(.+)?({QUESTION})(.+)?$'), handle_get)
    )

    updater.dispatcher.add_handler(CommandHandler('help', handle_help))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(f'^({HELP})$'), handle_help))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_button))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_start))
    updater.dispatcher.add_error_handler(handle_error)
    return updater


def main():
    updater = configure_telegram('ukr')

    # Start the Bot
    updater.start_polling()

    logger.info('Bot has been started and waiting for messages...')
    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
