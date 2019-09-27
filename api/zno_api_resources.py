import json

import falcon


class HomeResource():

    """Home page resource."""

    def on_get(self, req, resp):
        # TODO: load home page from template or load Swagger docs here
        home_page = """<h1>ZNO API docs</h1>

        <h3>Available endpoints:</h3>

        <table>
          <tr>
            <td>
              GET
            </td>
            <td>
              /question/id
            </td>
            <td>
              - get question by id or random if id is 0
            </td>
          </tr>
          <tr>
            <td>
              POST
            </td>
            <td>
              /question/id
            </td>
            <td>
              - submit answer for question with given id
            </td>
          </tr>
        </table>
        """
        resp.body = home_page
        resp.content_type = falcon.MEDIA_HTML
        resp.status = falcon.HTTP_200


class QuestionsResource():

    """Question resource, provide questions and submit answers."""

    def on_get(self, req, resp, question_id):
        """Return question by given question_id. Return random question if question_id = 0."""
        # TODO: get question from external source (file, db, etc.)
        resp.body = json.dumps('Dumb question')
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, question_id):
        """Submit answer for given question_id. Verify answer and return result."""
        # TODO: submit and verify answer
        resp.body = json.dumps('Answer submitted')
        resp.status = falcon.HTTP_200
