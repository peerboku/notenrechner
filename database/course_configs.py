from database.connection import get_connection


def get_config(course_id: int, school_year_id: int, class_: str):
    conn = get_connection()
    return conn.execute(
        """
        SELECT id, course_id, school_year_id, class,
               weight_exams, weight_oral, weight_homework, weight_quizzes
        FROM course_configs
        WHERE course_id = ? AND school_year_id = ? AND class = ?
        """,
        (course_id, school_year_id, class_),
    ).fetchone()


def upsert_config(
    course_id: int,
    school_year_id: int,
    class_: str,
    weight_exams: float,
    weight_oral: float,
    weight_homework: float,
    weight_quizzes: float,
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO course_configs
            (course_id, school_year_id, class, weight_exams, weight_oral,
             weight_homework, weight_quizzes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id, school_year_id, class) DO UPDATE SET
            weight_exams    = excluded.weight_exams,
            weight_oral     = excluded.weight_oral,
            weight_homework = excluded.weight_homework,
            weight_quizzes  = excluded.weight_quizzes
        """,
        (course_id, school_year_id, class_, weight_exams, weight_oral,
         weight_homework, weight_quizzes),
    )
    conn.commit()
