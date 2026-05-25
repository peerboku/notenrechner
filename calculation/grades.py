from database import grades as grades_db
from database import weight_overrides, course_configs


def category_average(grades: list[float]) -> float | None:
    if not grades:
        return None
    return sum(grades) / len(grades)


def get_weights(enrollment_id: int) -> dict:
    override = weight_overrides.get_override(enrollment_id)
    if override:
        return {
            "exams":    override["weight_exams"],
            "oral":     override["weight_oral"],
            "homework": override["weight_homework"],
            "quizzes":  override["weight_quizzes"],
        }

    row = _get_enrollment(enrollment_id)
    if row is None:
        raise ValueError(f"Enrollment {enrollment_id} not found")

    config = course_configs.get_config(row["course_id"], row["school_year_id"], row["class"])
    if config is None:
        raise ValueError(
            f"No course config for enrollment {enrollment_id} "
            f"(course={row['course_id']}, year={row['school_year_id']}, class={row['class']})"
        )
    return {
        "exams":    config["weight_exams"],
        "oral":     config["weight_oral"],
        "homework": config["weight_homework"],
        "quizzes":  config["weight_quizzes"],
    }


def _get_enrollment(enrollment_id: int):
    from database.connection import get_connection
    conn = get_connection()
    return conn.execute(
        "SELECT course_id, school_year_id, class FROM enrollments WHERE id = ?",
        (enrollment_id,),
    ).fetchone()


def calculate_final_grade(enrollment_id: int) -> float | None:
    categories = ("exams", "oral", "homework", "quizzes")

    all_grades = grades_db.get_grades(enrollment_id)
    if not all_grades:
        return None

    by_category: dict[str, list[float]] = {cat: [] for cat in categories}
    for g in all_grades:
        by_category[g["category"]].append(g["value"])

    weights = get_weights(enrollment_id)

    weighted_sum = 0.0
    total_weight = 0.0
    for cat in categories:
        w = weights[cat]
        if w == 0:
            continue
        avg = category_average(by_category[cat])
        if avg is None:
            continue
        weighted_sum += avg * w
        total_weight += w

    if total_weight == 0:
        return None

    return round(weighted_sum / total_weight, 1)
