import falcon
import rollbar
import sentry_sdk

import logger
from zno_services import QuestionsService


log = logger.getLogger('zno_api')


class QuestionsResource():

    """Get questions via QuestionsService"""


    def on_get(self, req, resp):
        """Return question by given question_id. Return random question if question_id = 0."""
        try:
            question = QuestionsService.load_random_question()

            rollbar.report_message('Loaded question: %s' % str(question))
            resp.media = {'id': question['id'],
                          'content': question['content'],
                          'choices': [{'id': choice['id'], 'content': choice['content']}
                                      for choice in question['choices']]}
            resp.status = falcon.HTTP_200
            log.debug('Loaded question, id: %s', resp.media['id'])

        except Exception as exc:
            log.exception(exc)
            rollbar.report_exc_info()
            sentry_sdk.capture_exception(exc)
            resp.media = {'code': 500, 'message': 'Не вдалося завантажити питання. Спробуйте, будь ласка, пізніше.'}
            resp.status = falcon.HTTP_500


class AnswersResource():

    """Submit answers and check it via QuestionsService"""

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: verify input, maybe via swagger
        choices = req.media.get('choices', [])
        try:
            question = QuestionsService.load_question_by_id(question_id)
            resp.media = {'is_correct': QuestionsService.check_answers(question, choices),
                          'choices': question['choices'],
                          'explanation': question.get('explanation')}
            resp.status = falcon.HTTP_200
            log.debug('Submitted answer, questionid: %s', question_id)

        except Exception as exc:
            log.exception(exc)
            rollbar.report_exc_info()
            sentry_sdk.capture_exception(exc)
            resp.media = {'code': 500, 'message': 'Не вдалося надіслати відповідь. Спробуйте, будь ласка, пізніше.'}
            resp.status = falcon.HTTP_500
