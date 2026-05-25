from database.connection import get_connection


def get_override(enrollment_id: int):
    conn = get_connection()
    return conn.execute(
        """
        SELECT id, enrollment_id, weight_exams, weight_oral,
               weight_homework, weight_quizzes
        FROM weight_overrides
        WHERE enrollment_id = ?
        """,
        (enrollment_id,),
    ).fetchone()


def upsert_override(
    enrollment_id: int,
    weight_exams: float,
    weight_oral: float,
    weight_homework: float,
    weight_quizzes: float,
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO weight_overrides
            (enrollment_id, weight_exams, weight_oral, weight_homework, weight_quizzes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(enrollment_id) DO UPDATE SET
            weight_exams    = excluded.weight_exams,
            weight_oral     = excluded.weight_oral,
            weight_homework = excluded.weight_homework,
            weight_quizzes  = excluded.weight_quizzes
        """,
        (enrollment_id, weight_exams, weight_oral, weight_homework, weight_quizzes),
    )
    conn.commit()


def delete_override(enrollment_id: int) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM weight_overrides WHERE enrollment_id = ?", (enrollment_id,)
    )
    conn.commit()
