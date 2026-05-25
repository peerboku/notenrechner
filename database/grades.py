from database.connection import get_connection


def get_grades(enrollment_id: int, category: str | None = None) -> list:
    conn = get_connection()
    if category is not None:
        return conn.execute(
            """
            SELECT id, enrollment_id, category, value, date
            FROM grades
            WHERE enrollment_id = ? AND category = ?
            ORDER BY date
            """,
            (enrollment_id, category),
        ).fetchall()
    return conn.execute(
        """
        SELECT id, enrollment_id, category, value, date
        FROM grades
        WHERE enrollment_id = ?
        ORDER BY date
        """,
        (enrollment_id,),
    ).fetchall()


def add_grade(enrollment_id: int, category: str, value: float, date: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO grades (enrollment_id, category, value, date) VALUES (?, ?, ?, ?)",
        (enrollment_id, category, value, date),
    )
    conn.commit()
    return cur.lastrowid


def update_grade(grade_id: int, value: float, date: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE grades SET value = ?, date = ? WHERE id = ?",
        (value, date, grade_id),
    )
    conn.commit()


def delete_grade(grade_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    conn.commit()
