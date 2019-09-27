import falcon

from zno_api_resources import HomeResource, QuestionsResource


def handle_404(req, resp):
    """Handle any request if there is no matching resource."""
    resp.status = falcon.HTTP_404
    resp.body = 'Not found'


application = falcon.API()
application.add_route('/', HomeResource())
application.add_route('/questions/{question_id}', QuestionsResource())
application.add_sink(handle_404, '')
