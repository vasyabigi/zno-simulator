class QuestionsService():

    """Class designed for questions manipulations: load, check answers, etc."""

    @staticmethod
    def load_question(question_id):
        # TODO: get question from external source (file, db, etc.)
        # just dummy question to test api and bot
        question = {"id": 1,
                    "content": "Ultimate Question of Life, the Universe, and Everything",
                    "choices": [{"id": 1, "content": "42", "is_correct": True},
                                {"id": 2, "content": "24", "is_correct": False}],
                    "image": "http://localhost:8000/images/1.png"}
        return question

    @classmethod
    def check_answers(cls, question_id, user_choices):
        question = cls.load_question(question_id)
        correct_choices = [choice['id'] for choice in question['choices'] if choice['is_correct']]
        return sorted(correct_choices) == sorted(user_choices)
