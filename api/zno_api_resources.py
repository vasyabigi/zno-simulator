import json

import falcon

from zno_services import QuestionsService


class QuestionsResource():

    """Get questions via QuestionsService"""

    def on_get(self, req, resp):
        """Return question by given question_id. Return random question if question_id = 0."""
        question = QuestionsService.load_random_question()
        filtered_question = {'id': question['id'],
                             'content': question['content'],
                             'choices': [{'id': choice['id'], 'content': choice['content']}
                                         for choice in question['choices']],
                             'image': question['image']}
        resp.media = filtered_question
        resp.status = falcon.HTTP_200


class AnswersResource():

    """Submit answers and check it via QuestionsService"""

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: verify input, maybe via swagger
        choices = req.media.get('choices', [])
        question = QuestionsService.load_question_by_id(question_id)
        resp.media = {"is_correct": QuestionsService.check_answers(question, choices),
                      "choices": question['choices'],
                      "explanation": question.get('explanation')}
        resp.status = falcon.HTTP_200
