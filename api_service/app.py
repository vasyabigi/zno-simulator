import os
import json
import falcon
import sentry_sdk
import logger

from sentry_sdk.integrations.falcon import FalconIntegration
from falcon_cors import CORS

from api_resources import QuestionsResource, AnswersResource, RandomQuestionResource


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("STAGE"),
    integrations=[FalconIntegration()],
)


def handle_404(req, resp):
    """Handle any request if there is no matching resource."""
    resp.status = falcon.HTTP_404
    resp.body = "Not found"


class HealthCheckResource:
    def on_get(self, request, response):
        body = {"data": {"status": "ok"}}
        response.body = json.dumps(body)


cors = CORS(allow_all_origins=True)
application = falcon.API(middleware=[cors.middleware])
application.add_route("/questions/random", RandomQuestionResource())
application.add_route("/questions/{question_id}", QuestionsResource())
application.add_route("/questions/{question_id}/answers", AnswersResource())
application.add_route("/", HealthCheckResource())
application.add_sink(handle_404, "")

log = logger.getLogger("root")
log.info("ZNO API is running")
