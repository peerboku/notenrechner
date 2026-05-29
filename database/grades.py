from database.connection import get_connection


def get_grades(enrollment_id: int, category_id: int | None = None) -> list:
    conn = get_connection()
    if category_id is not None:
        return conn.execute(
            """
            SELECT id, enrollment_id, event_id, category_id, value, date, note
            FROM grades
            WHERE enrollment_id = ? AND category_id = ?
            ORDER BY date
            """,
            (enrollment_id, category_id),
        ).fetchall()
    return conn.execute(
        """
        SELECT id, enrollment_id, event_id, category_id, value, date, note
        FROM grades
        WHERE enrollment_id = ?
        ORDER BY date
        """,
        (enrollment_id,),
    ).fetchall()


def add_grade(
    enrollment_id: int,
    category_id: int,
    value: float,
    date: str | None = None,
    note: str | None = None,
    event_id: int | None = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO grades (enrollment_id, event_id, category_id, value, date, note)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (enrollment_id, event_id, category_id, value, date, note),
    )
    conn.commit()
    return cur.lastrowid


def update_grade(
    grade_id: int,
    value: float,
    date: str | None = None,
    note: str | None = None,
) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE grades SET value = ?, date = ?, note = ? WHERE id = ?",
        (value, date, note, grade_id),
    )
    conn.commit()


def delete_grade(grade_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    conn.commit()


def delete_grades_by_event(event_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM grades WHERE event_id = ?", (event_id,))
    conn.commit()
