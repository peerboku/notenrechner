"""Parsing of teacher-style grade notation into numeric values.

Teachers write intermediate grades the way they do on paper
(German quarter-step system; Austrian teachers enter whole grades):

    "2"     -> 2.0
    "2,5"   -> 2.5    (comma or dot decimals)
    "2+"    -> 1.75   (a quarter step better)
    "2-"    -> 2.25   (a quarter step worse)
    "2-3"   -> 2.5    (midpoint of two adjacent grades, also "2/3")
"""

GRADE_MIN = 1.0
GRADE_MAX = 6.0


def parse_grade_input(text: str) -> float | None:
    """Parse a grade input string. Returns None if it is not a valid grade."""
    s = text.strip().replace(",", ".").replace(" ", "")
    if not s:
        return None

    value: float | None = None

    if s.endswith("+") and s[:-1].isdigit():
        value = int(s[:-1]) - 0.25
    elif s.endswith("-") and s[:-1].isdigit():
        value = int(s[:-1]) + 0.25
    elif "-" in s or "/" in s:
        sep = "-" if "-" in s else "/"
        left, _, right = s.partition(sep)
        if left.isdigit() and right.isdigit() and int(right) == int(left) + 1:
            value = int(left) + 0.5
    else:
        try:
            value = float(s)
        except ValueError:
            return None

    if value is None or not (GRADE_MIN <= value <= GRADE_MAX):
        return None
    return value


def format_grade(value: float) -> str:
    """Format a grade value for display: 2.0 -> "2", 1.75 -> "1.75"."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"
