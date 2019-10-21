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
    return [get_inline_button(letter, {
                                'action': 'ans',
                                'c_id': choice['id'],  # choice id
                                'q_id': question.q_id,  # question id
                            })
            for letter, choice in zip(question.choices_letters, question.choices)]


def get_inline_button(text, callback_data):
    return InlineKeyboardButton(
        text,
        callback_data=json.dumps(callback_data),
        parse_mode=ParseMode.MARKDOWN,
    )


def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    logger.info('Started chat {} with user {} - {}',
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


def render_question(update, context, question, is_verified=False, given_answer=None, is_explained=False):
    question_str = f'{question.content}'
    choices_str = question.choices_str(verified=is_verified)

    if given_answer:
        # render_user_choice(given_answer)
        data = json.loads(update.callback_query.data)
        answ_str = 'Correct' if question.is_correct else 'Incorrect'
        msg_text = f'{question_str} {choices_str} \n{answ_str} \n{question.selected_choice_str(given_answer)} \n try again'
        markup = InlineKeyboardMarkup(
            [
                list(
                    get_choices_buttons(question)
                ),
                [
                    get_inline_button(SHOW_ANSWER, {**data, **{'action': 'cor'}})
                ],
            ]
        )
        update.callback_query.edit_message_text(text=msg_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        # if correct: explanation button
        return

    if not is_verified:
        msg_text = f'{question_str} {choices_str}'
        markup = InlineKeyboardMarkup.from_row(get_choices_buttons(question))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=msg_text,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        )

    if is_explained:
        # render_explanation()
        msg_text = f'{question_str} {choices_str} {question.explanation}'
        update.callback_query.edit_message_text(
            text=msg_text,
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN,
        )

    if is_verified and not is_explained:
        # render_show_explanation()
        data = json.loads(update.callback_query.data)

        msg_text = f'{question_str} {choices_str}'
        data.update({
            'action': 'exp',
            'm_id': update.effective_message.message_id
        })
        reply_markup = None
        if question.has_explanation():
            reply_markup = InlineKeyboardMarkup.from_button(
                get_inline_button(EXPLANATION_STR, data)
            )
        update.callback_query.edit_message_text(
            text=msg_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )


def apply_send_answer(update, context):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    is_correct = answer.is_correct

    if is_correct:
        render_question(update, context, answer, is_verified=True, given_answer=data["c_id"])
    else:
        render_question(update, context, answer, is_verified=False, given_answer=data["c_id"])


def apply_show_correct_answer(update, context):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    render_question(update, context, answer, is_verified=True)


def apply_show_explanation(update, context):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    render_question(update, context, answer, is_verified=True, is_explained=True)


SUPPORTED_ACTIONS = {
    'ans': apply_send_answer,
    'cor': apply_show_correct_answer,
    'exp': apply_show_explanation,
}


def handle_button(update, context):
    """Handle button click."""
    callback_data = json.loads(update.callback_query.data)
    # Select action:
    apply_action = SUPPORTED_ACTIONS[callback_data['action']]
    # Apply action:
    apply_action(update, context)


def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    subject = get_subject_code(context)
    question = get_question(subject='ukr')

    render_question(update, context, question)


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


def configure_telegram(subject='ukr'):
    updater = Updater('868338601:AAHan9WVG5cBLx7gFn1_1GLyS4qMEo4XEjA', use_context=True)
    # updater = Updater(config.telegram_tokens[subject], use_context=True)

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
    # updater.dispatcher.add_error_handler(handle_error)
    return updater


def main():
    updater = configure_telegram()

    # Start the Bot
    updater.start_polling()

    logger.info('Bot has been started and waiting for messages...')
    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
