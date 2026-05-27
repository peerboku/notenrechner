from database.connection import get_connection

_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    input_type      TEXT NOT NULL CHECK(input_type IN ('continuous', 'discrete')),
    discrete_values TEXT,
    is_default      INTEGER NOT NULL DEFAULT 0
);

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
    UNIQUE(course_id, school_year_id, class)
);

CREATE TABLE IF NOT EXISTS course_config_weights (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    course_config_id INTEGER NOT NULL REFERENCES course_configs(id) ON DELETE CASCADE,
    category_id      INTEGER NOT NULL REFERENCES categories(id),
    weight           REAL NOT NULL,
    UNIQUE(course_config_id, category_id)
);

CREATE TABLE IF NOT EXISTS weight_presets (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS weight_preset_weights (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    weight_preset_id INTEGER NOT NULL REFERENCES weight_presets(id) ON DELETE CASCADE,
    category_id      INTEGER NOT NULL REFERENCES categories(id),
    weight           REAL NOT NULL,
    UNIQUE(weight_preset_id, category_id)
);

CREATE TABLE IF NOT EXISTS weight_overrides (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE CASCADE,
    note          TEXT
);

CREATE TABLE IF NOT EXISTS weight_override_weights (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    weight_override_id INTEGER NOT NULL REFERENCES weight_overrides(id) ON DELETE CASCADE,
    category_id        INTEGER NOT NULL REFERENCES categories(id),
    weight             REAL NOT NULL,
    UNIQUE(weight_override_id, category_id)
);

CREATE TABLE IF NOT EXISTS grade_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    course_config_id INTEGER NOT NULL REFERENCES course_configs(id),
    category_id      INTEGER NOT NULL REFERENCES categories(id),
    date             TEXT,
    note             TEXT
);

CREATE TABLE IF NOT EXISTS grades (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    event_id      INTEGER REFERENCES grade_events(id),
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    value         REAL NOT NULL,
    date          TEXT,
    note          TEXT
);
"""

_DEFAULT_CATEGORIES = [
    ("Exams",    "continuous", None,    1),
    ("Oral",     "continuous", None,    1),
    ("Homework", "discrete",   "1,3,5", 1),
    ("Quizzes",  "discrete",   "1,3,5", 1),
]


def init_db() -> None:
    conn = get_connection()
    _drop_old_schema(conn)
    conn.executescript(_SCHEMA)
    _seed(conn)
    conn.commit()


def _drop_old_schema(conn) -> None:
    """Drop tables whose structure changed in the Phase 4 migration."""
    existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(course_configs)").fetchall()}
    if "weight_exams" not in existing_cols:
        return
    # Old hardcoded-weight schema detected — drop affected tables in FK order
    conn.executescript("""
        DROP TABLE IF EXISTS grades;
        DROP TABLE IF EXISTS weight_overrides;
        DROP TABLE IF EXISTS course_configs;
    """)


def _seed(conn) -> None:
    existing = conn.execute(
        "SELECT COUNT(*) FROM categories WHERE is_default = 1"
    ).fetchone()[0]
    if existing == 0:
        conn.executemany(
            "INSERT INTO categories (name, input_type, discrete_values, is_default) VALUES (?, ?, ?, ?)",
            _DEFAULT_CATEGORIES,
        )
    if conn.execute("SELECT value FROM settings WHERE key = 'grading_scale'").fetchone() is None:
        conn.execute("INSERT INTO settings (key, value) VALUES ('grading_scale', 'austria')")
    if conn.execute("SELECT COUNT(*) FROM weight_presets").fetchone()[0] == 0:
        cat_map = {
            r["name"]: r["id"]
            for r in conn.execute("SELECT id, name FROM categories").fetchall()
        }
        cur = conn.execute("INSERT INTO weight_presets (name) VALUES ('Standard')")
        preset_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO weight_preset_weights (weight_preset_id, category_id, weight) VALUES (?, ?, ?)",
            [
                (preset_id, cat_map["Exams"],    40.0),
                (preset_id, cat_map["Oral"],     30.0),
                (preset_id, cat_map["Homework"], 10.0),
                (preset_id, cat_map["Quizzes"],  20.0),
            ],
        )
