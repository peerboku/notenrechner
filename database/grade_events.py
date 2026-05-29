from database.connection import get_connection


def add_event(
    course_config_id: int,
    category_id: int,
    date: str | None = None,
    note: str | None = None,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO grade_events (course_config_id, category_id, date, note) VALUES (?, ?, ?, ?)",
        (course_config_id, category_id, date, note),
    )
    conn.commit()
    return cur.lastrowid


def get_event(event_id: int):
    conn = get_connection()
    return conn.execute(
        "SELECT id, course_config_id, category_id, date, note FROM grade_events WHERE id = ?",
        (event_id,),
    ).fetchone()


def get_events_by_config(course_config_id: int) -> list:
    conn = get_connection()
    return conn.execute(
        """
        SELECT id, course_config_id, category_id, date, note
        FROM grade_events
        WHERE course_config_id = ?
        ORDER BY date DESC
        """,
        (course_config_id,),
    ).fetchall()


def get_events_with_category(course_config_id: int) -> list:
    conn = get_connection()
    return conn.execute(
        """
        SELECT ge.id, ge.date, ge.note, c.name AS category_name
        FROM grade_events ge
        JOIN categories c ON c.id = ge.category_id
        WHERE ge.course_config_id = ?
        ORDER BY ge.id DESC
        """,
        (course_config_id,),
    ).fetchall()


def delete_event(event_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM grade_events WHERE id = ?", (event_id,))
    conn.commit()
