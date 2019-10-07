import falcon

import logger
from zno_services import QuestionsService


log = logger.getLogger('zno_api')


class QuestionsResource():

    """Get questions via QuestionsService"""

    def on_get(self, req, resp, question_id):
        """Return question by given question_id. Return random question if question_id = random."""
        question = QuestionsService.load_random_question() if question_id == 'random' \
            else QuestionsService.load_question_by_id(int(question_id))
        resp.media = {'id': question['id'],
                      'content': question['content'],
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
        question = QuestionsService.load_question_by_id(int(question_id))
        resp.media = {'is_correct': QuestionsService.check_answers(question, choices),
                      'choices': question['choices'],
                      'explanation': question.get('explanation')}
        resp.status = falcon.HTTP_200
        log.debug('Submitted answer, question id: %s', question_id)
