import falcon
import logger

from services import QuestionsService, QuestionNotFoundError, SUPPORTED_SUBJECTS_CODES
from serializers import serialize_question


log = logger.getLogger("zno_api")


class RandomQuestionResource:
    def on_get(self, req, resp):
        subject = req.get_param("subject")
        q_format = req.get_param("format", default="markdown")

        if not subject or subject not in SUPPORTED_SUBJECTS_CODES:
            raise falcon.HTTPBadRequest("Subject is not supported")

        question = QuestionsService.load_random_question(subject=subject)
        resp.media = serialize_question(question, q_format)
        resp.status = falcon.HTTP_200


class QuestionsResource:
    """Get questions via QuestionsService"""

    def on_get(self, req, resp, question_id):
        q_format = req.get_param("format", default="markdown")
        try:
            question = QuestionsService.load_question_by_id(question_id)
        except QuestionNotFoundError:
            resp.media = {
                "statusCode": 404,
                "message": f'Question with id "{question_id}" not found.',
            }
            resp.status = falcon.HTTP_404

        else:
            resp.media = serialize_question(question, q_format)
            resp.status = falcon.HTTP_200
            log.debug("Loaded question, id: %s", resp.media["id"])


class AnswersResource:
    """Submit answers and check it via QuestionsService"""

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: verify input, maybe via swagger
        choices = req.media.get("choices", [])
        q_format = req.get_param("format", default="markdown")

        try:
            question = QuestionsService.load_question_by_id(question_id)
        except QuestionNotFoundError:
            resp.media = {
                "statusCode": 404,
                "message": f'Question with id "{question_id}" not found.',
            }
            resp.status = falcon.HTTP_404

        else:
            question_data = serialize_question(question, q_format)
            question_data["is_correct"] = QuestionsService.check_answers(
                question, choices
            )

            resp.media = question_data
            resp.status = falcon.HTTP_200
            log.debug("Submitted answer, question id: %s", question_id)
