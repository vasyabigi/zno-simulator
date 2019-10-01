API provides following endpoints:

GET /questions/random - get random question

Example:

    ```
    $ curl <zno_simulator_api_host>/questions/random
    {"id": 1, "content": "Ultimate Question of Life, the Universe, and Everything", "choices": [{"id": 1, "content": "42"}, {"id": 2, "content": "24"}], "image": "http://<zno_simulator_api_host>/images/1.png"}
    ```

POST /questions/{question_id}/answers - submit answer and get check whether answer is correct

Examples:
    ```
    $ curl -X POST <zno_simulator_api_host>/questions/1/answers -H "Content-Type: application/json" -d'{"choices": [1]}'
    {"is_correct": true, choices: [{"id": 1, "content": "42", "is_correct": true}, {"id": 2, "content": "24", "is_correct": false}], "explanation": "42 - answer which is given by enormous computer in the fantasy world of Douglas Adams in his book \"Hitchhiker's\ guide to the Galaxy""}
    ```

Start API service by executing following command (first, cd to "api" directory):

$ gunicorn app
