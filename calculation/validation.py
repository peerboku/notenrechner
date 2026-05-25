_RESTRICTED = {1.0, 3.0, 5.0}


def validate_weights(
    weight_exams: float,
    weight_oral: float,
    weight_homework: float,
    weight_quizzes: float,
) -> bool:
    total = weight_exams + weight_oral + weight_homework + weight_quizzes
    return abs(total - 100.0) < 0.01


def validate_grade_value(value: float, category: str) -> bool:
    if category in ("exams", "oral"):
        return 1.0 <= value <= 5.0
    if category in ("homework", "quizzes"):
        return float(value) in _RESTRICTED
    return False
