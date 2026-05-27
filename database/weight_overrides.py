from database.connection import get_connection


def get_override(enrollment_id: int):
    conn = get_connection()
    return conn.execute(
        "SELECT id, enrollment_id, note FROM weight_overrides WHERE enrollment_id = ?",
        (enrollment_id,),
    ).fetchone()


def upsert_override(enrollment_id: int, note: str = "") -> int:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO weight_overrides (enrollment_id, note) VALUES (?, ?)
        ON CONFLICT(enrollment_id) DO UPDATE SET note = excluded.note
        """,
        (enrollment_id, note or None),
    )
    conn.commit()
    return get_override(enrollment_id)["id"]


def delete_override(enrollment_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM weight_overrides WHERE enrollment_id = ?", (enrollment_id,))
    conn.commit()


def get_override_weights(weight_override_id: int) -> dict[int, float]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT category_id, weight FROM weight_override_weights WHERE weight_override_id = ?",
        (weight_override_id,),
    ).fetchall()
    return {r["category_id"]: r["weight"] for r in rows}


def set_override_weights(weight_override_id: int, weights: dict[int, float]) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM weight_override_weights WHERE weight_override_id = ?",
        (weight_override_id,),
    )
    conn.executemany(
        "INSERT INTO weight_override_weights (weight_override_id, category_id, weight) VALUES (?, ?, ?)",
        [(weight_override_id, cat_id, w) for cat_id, w in weights.items()],
    )
    conn.commit()
