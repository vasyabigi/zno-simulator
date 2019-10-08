import os
import json
import random

import pymongo
import requests


class QuestionNotFoundError(Exception):
    """Custom exception should be raised when question with given id is not found."""
    pass


class QuestionsService:
    """Class designed for questions manipulations: load, check answers, etc."""

    @staticmethod
    def load_random_question():
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['zno_questions']
        # TODO: receive subject argument and use it instead of hardcode
        collection = db['ua_lang_and_literature']
        return collection.aggregate([{ '$sample': { 'size': 1 } }]).next()

    @staticmethod
    def load_question_by_id(q_id):
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['zno_questions']
        # TODO: receive subject argument and use it instead of hardcode
        collection = db['ua_lang_and_literature']
        try:
            return collection.find({ '_id': int(q_id)}).next()
        except StopIteration:
            raise QuestionNotFoundError

    @staticmethod
    def check_answers(question, user_choices):
        correct_choices = [
            choice["id"] for choice in question["choices"] if choice["is_correct"]
        ]
        return sorted(correct_choices) == sorted(user_choices)
