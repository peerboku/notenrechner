from database.connection import get_connection


def get_enrollments_by_student(student_id: int) -> list:
    conn = get_connection()
    return conn.execute(
        """
        SELECT e.id, e.class, e.student_id, e.course_id, e.school_year_id,
               c.name AS course_name,
               sy.label AS school_year_label
        FROM enrollments e
        JOIN courses c ON c.id = e.course_id
        JOIN school_years sy ON sy.id = e.school_year_id
        WHERE e.student_id = ?
        ORDER BY sy.label DESC, c.name
        """,
        (student_id,),
    ).fetchall()


def get_enrollments_by_filter(
    school_year_id: int | None = None,
    class_: str | None = None,
    course_id: int | None = None,
) -> list:
    conn = get_connection()
    query = """
        SELECT e.id, e.class, e.student_id, e.course_id, e.school_year_id,
               s.name AS student_name,
               c.name AS course_name,
               sy.label AS school_year_label
        FROM enrollments e
        JOIN students s ON s.id = e.student_id
        JOIN courses c ON c.id = e.course_id
        JOIN school_years sy ON sy.id = e.school_year_id
        WHERE 1=1
    """
    params: list = []
    if school_year_id is not None:
        query += " AND e.school_year_id = ?"
        params.append(school_year_id)
    if class_ is not None:
        query += " AND e.class = ?"
        params.append(class_)
    if course_id is not None:
        query += " AND e.course_id = ?"
        params.append(course_id)
    query += " ORDER BY s.name, sy.label DESC"
    return conn.execute(query, params).fetchall()


def add_enrollment(
    student_id: int, course_id: int, school_year_id: int, class_: str
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO enrollments (student_id, course_id, school_year_id, class)
        VALUES (?, ?, ?, ?)
        """,
        (student_id, course_id, school_year_id, class_),
    )
    conn.commit()
    return cur.lastrowid


def delete_enrollment(enrollment_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM enrollments WHERE id = ?", (enrollment_id,))
    conn.commit()
