class QuestionsService():

    """Class designed for questions manipulations: load, check answers, etc."""

    @staticmethod
    def load_random_question():
        # TODO: get question from external source (file, db, etc.)
        # just dummy question to test api and bot
        question = {"id": 1,
                    "content": "Ultimate Question of Life, the Universe, and Everything",
                    "choices": [{"id": 1, "content": "42", "is_correct": True},
                                {"id": 2, "content": "24", "is_correct": False}],
                    "image": "http://localhost:8000/images/1.png",
                    "explanation": "42 - answer which is given by enormous computer in the fantasy world of " \
                                   "Douglas Adams in his book \"Hitchhiker's\ guide to the Galaxy"}
        return question

    @staticmethod
    def load_question_by_id(question_id):
        # TODO: get question from external source (file, db, etc.)
        # just dummy question to test api and bot
        question = {"id": 1,
                    "content": "Ultimate Question of Life, the Universe, and Everything",
                    "choices": [{"id": 1, "content": "42", "is_correct": True},
                                {"id": 2, "content": "24", "is_correct": False}],
                    "image": "http://localhost:8000/images/1.png",
                    "explanation": "42 - answer which is given by enormous computer in the fantasy world of " \
                                   "Douglas Adams in his book \"Hitchhiker's\ guide to the Galaxy"}
        return question

    @staticmethod
    def check_answers(question, user_choices):
        correct_choices = [choice['id'] for choice in question['choices'] if choice['is_correct']]
        return sorted(correct_choices) == sorted(user_choices)
