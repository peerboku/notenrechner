from database.connection import get_connection


def get_all_presets() -> list:
    conn = get_connection()
    return conn.execute("SELECT id, name FROM weight_presets ORDER BY name").fetchall()


def get_preset(preset_id: int):
    conn = get_connection()
    return conn.execute(
        "SELECT id, name FROM weight_presets WHERE id = ?", (preset_id,)
    ).fetchone()


def add_preset(name: str) -> int:
    conn = get_connection()
    cur = conn.execute("INSERT INTO weight_presets (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def rename_preset(preset_id: int, name: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE weight_presets SET name = ? WHERE id = ?", (name, preset_id))
    conn.commit()


def delete_preset(preset_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM weight_presets WHERE id = ?", (preset_id,))
    conn.commit()


def get_preset_weights(preset_id: int) -> dict[int, float]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT category_id, weight FROM weight_preset_weights WHERE weight_preset_id = ?",
        (preset_id,),
    ).fetchall()
    return {r["category_id"]: r["weight"] for r in rows}


def set_preset_weights(preset_id: int, weights: dict[int, float]) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM weight_preset_weights WHERE weight_preset_id = ?", (preset_id,)
    )
    conn.executemany(
        "INSERT INTO weight_preset_weights (weight_preset_id, category_id, weight) VALUES (?, ?, ?)",
        [(preset_id, cat_id, w) for cat_id, w in weights.items()],
    )
    conn.commit()
