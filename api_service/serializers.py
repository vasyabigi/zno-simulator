def serialize_question(question_data):
    return {
        "id": question_data["id"],
        "content": question_data["content"],
        "image": question_data["image"],
        "explanation": question_data["explanation"],
        "choices": [
            {
                "id": choice["id"],
                "content": choice["content"],
                "is_correct": choice["is_correct"],
            }
            for choice in question_data["choices"]
        ],
    }
