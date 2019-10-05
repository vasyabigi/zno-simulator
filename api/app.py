import json
import falcon
import sentry_sdk

import logger

from sentry_sdk.integrations.falcon import FalconIntegration

from zno_api_resources import QuestionsResource, AnswersResource


sentry_sdk.init(dsn="https://068e491992e74a3dbd3a5ac0d0b0039c@sentry.io/1769079",
                integrations=[FalconIntegration()])


def handle_404(req, resp):
    """Handle any request if there is no matching resource."""
    resp.status = falcon.HTTP_404
    resp.body = 'Not found'


class HealthCheckResource:
    def on_get(self, request, response):
        body = {'data': {'status': 'ok'}}
        response.body = json.dumps(body)


application = falcon.API()
application.add_route('/questions/random', QuestionsResource())
application.add_route('/questions/{question_id}/answers', AnswersResource())
application.add_route('/healthcheck', HealthCheckResource())
application.add_sink(handle_404, '')

log = logger.getLogger('root')
log.info('ZNO API is running')
