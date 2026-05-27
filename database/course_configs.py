from database.connection import get_connection


def get_config(course_id: int, school_year_id: int, class_: str):
    conn = get_connection()
    return conn.execute(
        """
        SELECT id, course_id, school_year_id, class
        FROM course_configs
        WHERE course_id = ? AND school_year_id = ? AND class = ?
        """,
        (course_id, school_year_id, class_),
    ).fetchone()


def upsert_config(course_id: int, school_year_id: int, class_: str) -> int:
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO course_configs (course_id, school_year_id, class) VALUES (?, ?, ?)",
        (course_id, school_year_id, class_),
    )
    conn.commit()
    return get_config(course_id, school_year_id, class_)["id"]


def get_weights(course_config_id: int) -> dict[int, float]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT category_id, weight FROM course_config_weights WHERE course_config_id = ?",
        (course_config_id,),
    ).fetchall()
    return {r["category_id"]: r["weight"] for r in rows}


def set_weights(course_config_id: int, weights: dict[int, float]) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM course_config_weights WHERE course_config_id = ?",
        (course_config_id,),
    )
    conn.executemany(
        "INSERT INTO course_config_weights (course_config_id, category_id, weight) VALUES (?, ?, ?)",
        [(course_config_id, cat_id, w) for cat_id, w in weights.items()],
    )
    conn.commit()
