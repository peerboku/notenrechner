from database.connection import get_connection


def get_all_courses() -> list:
    conn = get_connection()
    return conn.execute("SELECT id, name FROM courses ORDER BY name").fetchall()


def add_course(name: str) -> int:
    conn = get_connection()
    cur = conn.execute("INSERT INTO courses (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def get_or_create_course(name: str) -> int:
    conn = get_connection()
    row = conn.execute("SELECT id FROM courses WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO courses (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid
