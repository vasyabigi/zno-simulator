def render_question(is_verified=False, given_answer=None, is_explained=False):
    print("QUESTION CONTENT")
    render_choices(is_verified=is_verified)

    if given_answer:
        render_your_choice(given_answer)

    if not is_verified:
        render_actions()

    if is_explained:
        render_explanation()


def render_choices(is_verified=False):
    if is_verified:
        print("VERIFIED CHOICES")
    else:
        print("CHOICES")


def render_actions():
    print("SELECT: A, Б, В, Г")


def render_your_choice(answer):
    is_correct = "CORRECT" if is_answer_correct(answer) else "WRONG"
    print(f"YOUR {is_correct} CHOICE: {answer}")


def render_explanation():
    print("EXPLANATION")


def is_answer_correct(choice):
    return choice == "В"


def apply_send_answer(data):
    is_correct = is_answer_correct(data["choice"])

    if is_correct:
        render_question(is_verified=True, given_answer=data["choice"])
    else:
        render_question(is_verified=False, given_answer=data["choice"])


def apply_show_correct_answer(data):
    render_question(is_verified=True)


def apply_show_explanation(data):
    render_question(is_verified=True, is_explained=True)


SUPPORTED_ACTIONS = {
    "ans": apply_send_answer,
    "cor": apply_show_correct_answer,
    "exp": apply_show_explanation,
}


def handle_action(data):
    apply_action = SUPPORTED_ACTIONS[data["action"]]
    apply_action(data)


if __name__ == "__main__":
    render_question()
    print()
    handle_action({"action": "answer", "choice": "A"})
    handle_action({"action": "answer", "choice": "Б"})
    handle_action({"action": "answer", "choice": "В"})
    handle_action({"action": "correct"})
    handle_action({"action": "explanation"})
