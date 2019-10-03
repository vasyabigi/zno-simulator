import falcon
import rollbar
import sentry_sdk

import logger

from zno_api_resources import QuestionsResource, AnswersResource


rollbar.init('08d5e546f6874ba08d066c0aaf357fce')
sentry_sdk.init("https://068e491992e74a3dbd3a5ac0d0b0039c@sentry.io/1769079")


def handle_404(req, resp):
    """Handle any request if there is no matching resource."""
    resp.status = falcon.HTTP_404
    resp.body = 'Not found'


application = falcon.API()
application.add_route('/questions/random', QuestionsResource())
application.add_route('/questions/{question_id}/answers', AnswersResource())
application.add_sink(handle_404, '')

log = logger.getLogger('root')
log.info('ZNO API is running')
