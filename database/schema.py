from database.connection import get_connection

_SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS school_years (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS enrollments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id     INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id      INTEGER NOT NULL REFERENCES courses(id),
    school_year_id INTEGER NOT NULL REFERENCES school_years(id),
    class          TEXT NOT NULL,
    UNIQUE(student_id, course_id, school_year_id)
);

CREATE TABLE IF NOT EXISTS course_configs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id      INTEGER NOT NULL REFERENCES courses(id),
    school_year_id INTEGER NOT NULL REFERENCES school_years(id),
    class          TEXT NOT NULL,
    weight_exams   REAL NOT NULL DEFAULT 0,
    weight_oral    REAL NOT NULL DEFAULT 0,
    weight_homework REAL NOT NULL DEFAULT 0,
    weight_quizzes REAL NOT NULL DEFAULT 0,
    UNIQUE(course_id, school_year_id, class)
);

CREATE TABLE IF NOT EXISTS weight_overrides (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id  INTEGER NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE CASCADE,
    weight_exams   REAL NOT NULL,
    weight_oral    REAL NOT NULL,
    weight_homework REAL NOT NULL,
    weight_quizzes REAL NOT NULL,
    note           TEXT
);

CREATE TABLE IF NOT EXISTS grades (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    category      TEXT NOT NULL,
    value         REAL NOT NULL,
    date          TEXT NOT NULL
);
"""


def init_db() -> None:
    conn = get_connection()
    conn.executescript(_SCHEMA)
    _migrate(conn)
    conn.commit()


def _migrate(conn) -> None:
    """Add columns that were introduced after initial release."""
    existing = {r[1] for r in conn.execute("PRAGMA table_info(weight_overrides)").fetchall()}
    if "note" not in existing:
        conn.execute("ALTER TABLE weight_overrides ADD COLUMN note TEXT")
