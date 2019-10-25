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
    return (get_inline_button(letter, {'action': 'ans',
                                       'c_id': choice['id'],  # choice id
                                       'q_id': question.q_id,  # question id
                                       })
            for letter, choice in zip(question.choices_letters, question.choices)
            )


def get_inline_button(text, callback_data):
    return InlineKeyboardButton(
        text,
        callback_data=json.dumps(callback_data),
        parse_mode=ParseMode.MARKDOWN,
    )


def handle_start(update, context):
    """Displaying the starting message when bot starts."""
    markup = ReplyKeyboardMarkup(
        keyboard=[[f'{QUESTION_BOOKS} {QUESTION}']],
        resize_keyboard=True
    )
    update.message.reply_text(
        GREETING_STR,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )


def get_subject_code(context):
    # TODO: Fix the subject getter
    for key, value in config.telegram_tokens.items():
        if value == context.bot.token:
            return key


def render_answer(update, answer, given_answer=False, is_verified=False, is_explained=False):
    question_str = answer.content
    choices_str = answer.choices_str(verified=is_verified)
    data = json.loads(update.callback_query.data)
    msg_str = ''
    markup = None

    if is_explained:
        msg_str = answer.correct_answer_str + answer.explanation

    if is_verified and not is_explained:
        markup = render_show_explanation(update, data, answer)
        msg_str = answer.correct_answer_str

    # if given_answer:
    #     markup, msg_str = render_user_choice(update, data, answer)

    if given_answer:
        msg_str = answer.selected_choice_str(data['c_id'])

        if answer.is_correct:
            markup = render_show_explanation(update, data, answer)
        else:
            markup = render_choice_buttons(data, answer)

    # avoid redundant update in case of the same wrong choice
    msg_text = f'{question_str} {choices_str} {msg_str}'
    if msg_text.strip() in (update.callback_query.message.text_markdown,
                            update.callback_query.message.caption_markdown):
        return

    if answer.image:
        update.callback_query.edit_message_caption(
            caption=msg_text,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        update.callback_query.edit_message_text(
            text=msg_text,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )


def render_choice_buttons(data, answer):
    markup = InlineKeyboardMarkup([
        list(
            get_choices_buttons(answer)
        ),
        [
            get_inline_button(SHOW_ANSWER, {**data, **{'action': 'cor'}})
        ],
    ])
    return markup


def render_show_explanation(update, data, answer):
    markup = None
    if answer.has_explanation:
        markup = InlineKeyboardMarkup.from_button(
            get_inline_button(EXPLANATION_STR, {**data,
                                                **{'action': 'exp'},
                                                **{'m_id': update.effective_message.message_id}
                                                }
                              )
        )
    return markup


def apply_send_answer(update):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    is_correct = answer.is_correct

    if is_correct:
        render_answer(update, answer, given_answer=True, is_verified=True)
    else:
        render_answer(update, answer, given_answer=True, is_verified=False)


def apply_show_correct_answer(update):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    render_answer(update, answer, given_answer=False, is_verified=True)


def apply_show_explanation(update):
    data = json.loads(update.callback_query.data)

    answer = post_answer(data['q_id'], data['c_id'])
    # TODO we still have 'c_id', shoud we show both correct answer and user's answer?
    render_answer(update, answer, is_verified=True, is_explained=True)


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
    apply_action(update)


def handle_get(update, context):
    """Send user a question and answers options keyboard."""
    subject = get_subject_code(context)
    question = get_question(subject=subject)
    markup = InlineKeyboardMarkup.from_row(get_choices_buttons(question))
    if question.image:
        update.message.reply_photo(
            photo=question.image,
            caption=question.content + question.choices_str,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            question.content + question.choices_str,
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
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


def configure_telegram(subject='ukr'):
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
    updater = configure_telegram()

    # Start the Bot
    updater.start_polling()

    logger.info('Bot has been started and waiting for messages...')
    # Run the bot until the user presses Ctrl-C
    # or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
