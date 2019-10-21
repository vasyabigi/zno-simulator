import falcon

import logger
from zno_services import QuestionsService, QuestionNotFoundError, SUPPORTED_SUBJECTS_CODES


log = logger.getLogger('zno_api')


class QuestionsResource():

    """Get questions via QuestionsService"""

    def on_get(self, req, resp, question_id):
        """Return question by given question_id. Return random question if question_id = random."""
        subject = req.get_param('subject')

        if subject and subject not in SUPPORTED_SUBJECTS_CODES:
            raise falcon.HTTPBadRequest("Subject is not supported")

        try:
            question = QuestionsService.load_random_question(subject=subject) if question_id == 'random' \
                else QuestionsService.load_question_by_id(question_id)

        except QuestionNotFoundError:
            resp.media = {'statusCode': 404,
                          'message': f'Question with id "{question_id}" not found.'}
            resp.status = falcon.HTTP_404

        else:
            resp.media = {'id': question['id'],
                          'content': question['content'],
                          'image': question['image'],
                          # 'explanation': question['explanation'],
                          'choices': [{'id': choice['id'], 'content': choice['content']}
                                      for choice in question['choices']]}
            resp.status = falcon.HTTP_200
            log.debug('Loaded question, id: %s', resp.media['id'])


class AnswersResource():

    """Submit answers and check it via QuestionsService"""

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: verify input, maybe via swagger
        choices = req.media.get('choices', [])
        try:
            question = QuestionsService.load_question_by_id(question_id)

        except QuestionNotFoundError:
            resp.media = {'statusCode': 404,
                          'message': f'Question with id "{question_id}" not found.'}
            resp.status = falcon.HTTP_404

        else:
            resp.media = {'id': question['id'],
                          'content': question['content'],
                          'image': question['image'],
                          'is_correct': QuestionsService.check_answers(question, choices),
                          'choices': question['choices'],
                          'explanation': question.get('explanation')}
            resp.status = falcon.HTTP_200
            log.debug('Submitted answer, question id: %s', question_id)
