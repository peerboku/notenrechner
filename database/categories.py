from database.connection import get_connection


def get_all_categories() -> list:
    conn = get_connection()
    return conn.execute(
        "SELECT id, name, input_type, discrete_values, is_default FROM categories ORDER BY id"
    ).fetchall()


def get_category(category_id: int):
    conn = get_connection()
    return conn.execute(
        "SELECT id, name, input_type, discrete_values, is_default FROM categories WHERE id = ?",
        (category_id,),
    ).fetchone()


def add_category(name: str, input_type: str, discrete_values: str | None = None) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO categories (name, input_type, discrete_values, is_default) VALUES (?, ?, ?, 0)",
        (name, input_type, discrete_values),
    )
    conn.commit()
    return cur.lastrowid


def update_category(
    category_id: int, name: str, input_type: str, discrete_values: str | None = None
) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categories SET name = ?, input_type = ?, discrete_values = ? WHERE id = ?",
        (name, input_type, discrete_values, category_id),
    )
    conn.commit()


def delete_category(category_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
