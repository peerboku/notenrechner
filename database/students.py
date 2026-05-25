from database.connection import get_connection


def get_all_students() -> list:
    conn = get_connection()
    return conn.execute("SELECT id, name FROM students ORDER BY name").fetchall()


def get_student_by_id(student_id: int):
    conn = get_connection()
    return conn.execute("SELECT id, name FROM students WHERE id = ?", (student_id,)).fetchone()


def add_student(name: str) -> int:
    conn = get_connection()
    cur = conn.execute("INSERT INTO students (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def update_student(student_id: int, name: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE students SET name = ? WHERE id = ?", (name, student_id))
    conn.commit()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
