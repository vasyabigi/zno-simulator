import json

import falcon

from zno_services import QuestionsService


class QuestionsResource():

    """Get questions via QuestionsService"""

    def on_get(self, req, resp, question_id):
        """Return question by given question_id. Return random question if question_id = 0."""
        question = QuestionsService.load_question(question_id)
        # remove field "is_correct" from choices
        for choice in question['choices']:
            del choice['is_correct']
        resp.body = json.dumps(QuestionsService.load_question(question_id))
        resp.status = falcon.HTTP_200


class AnswersResource():

    """Submit answers and check it via QuestionsService"""

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: verify input, maybe via swagger
        choices = req.media.get('choices', [])
        resp.body = json.dumps(QuestionsService.check_answers(question_id, choices))
        resp.status = falcon.HTTP_200
