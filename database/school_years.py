from database.connection import get_connection


def get_all_school_years() -> list:
    conn = get_connection()
    return conn.execute(
        "SELECT id, label FROM school_years ORDER BY label DESC"
    ).fetchall()


def add_school_year(label: str) -> int:
    conn = get_connection()
    cur = conn.execute("INSERT INTO school_years (label) VALUES (?)", (label,))
    conn.commit()
    return cur.lastrowid


def get_or_create_school_year(label: str) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM school_years WHERE label = ?", (label,)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO school_years (label) VALUES (?)", (label,))
    conn.commit()
    return cur.lastrowid
