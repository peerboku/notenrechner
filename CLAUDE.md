## What This Is

A desktop grade calculator app for a single teacher. Built in Python with CustomTkinter. Targets Windows. Developed on macOS. Distributed as a standalone .exe via PyInstaller built through GitHub Actions.

Purpose: teacher enters grades for students across categories. App calculates category averages and a weighted final grade. Non-technical teacher audience — UX clarity is a primary constraint.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python |
| UI | CustomTkinter |
| Database | SQLite (local file) |
| Packaging | PyInstaller → .exe |
| Build pipeline | GitHub Actions (Mac dev → Windows .exe) |

---

## Data Model

```
Student
  id, name

SchoolYear
  id, label         e.g. "2024/25"

Course
  id, name

Enrollment          (student × course × class × school_year)
  id
  student_id
  course_id
  class             e.g. "4B" — belongs to enrollment, not student
  school_year_id
  → inherits weights from CourseConfig unless weight_override exists

CourseConfig        (default weights for class × course × school_year)
  id
  class
  course_id
  school_year_id
  weight_exams, weight_oral, weight_homework, weight_quizzes
  → all weights sum to 100%, zeros allowed to disable a category

WeightOverride      (optional per-enrollment override)
  id
  enrollment_id
  weight_exams, weight_oral, weight_homework, weight_quizzes

Grade               (individual grade entry)
  id
  enrollment_id
  category          enum: exams | oral | homework | quizzes
  value             float
  date
```

---

## Grading System

Austrian scale: **1 (best) → 5 (worst)**. Pass threshold: ≤ 4.0. Fail: > 4.0.

### Categories (fixed, 4 total)

| Category | Input values | Calculation |
|---|---|---|
| Exams | 1–5 | mean of all entries |
| Oral | 1–5 | mean of all entries |
| Homework | {1, 3, 5} only | mean of all entries |
| Quizzes | {1, 3, 5} only | mean of all entries |

### Final Grade
- Weighted average of the 4 category averages
- Weights sourced from WeightOverride if exists, else CourseConfig
- Rounded to **1 decimal**
- Category averages displayed as raw floats (unrounded)

---

## Screens (5 total)

1. **Dashboard** — filter by year/class/course, student list with final grades
2. **Student Detail** — all enrollments, per enrollment: category averages + expandable individual grades
3. **Grade Entry** — add/edit/delete individual grades per category per enrollment
4. **Course Config** — set weights per class/course/year, set per-student weight overrides
5. **Student Management** — add/edit students, create/edit enrollments

---

## Key Constraints

- Homework and quizzes input must be locked to {1, 3, 5} in the UI
- Weight fields must validate to sum = 100% before saving
- Class is scoped to enrollment + school year (students change class each year)
- A student can have multiple enrollments (multiple courses per year, multiple years)
- App must run without a terminal window on Windows
- No network dependency — fully local

---

## Current Phase

Phase 1 (DB schema + data access layer + calculation engine + GitHub Actions) complete.
Starting Phase 3 — Core Screens (UI). See ROADMAP.md for full task breakdown.

---

## Future Scope (not in MVP)

- German grading scale (1–6) as switchable option
- Teacher-defined categories per course
- Export grade overview to PDF
- Configurable rounding thresholds
- Database backup / export
