# Grade Calculator — Roadmap

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done

---

## Phase 1 — Project Setup & Foundation

- [x] Initialize Python project structure
- [x] Set up virtual environment
- [x] Install dependencies: `customtkinter`, `pyinstaller`
- [x] Create SQLite database file on first run
- [x] Implement DB schema (all tables below)
- [x] Write data access layer (CRUD functions for all entities)
- [x] Set up GitHub repository
- [x] Add GitHub Actions workflow for Windows .exe build

### DB Schema
- [x] `students` — id, name
- [x] `school_years` — id, label (e.g. "2024/25")
- [x] `courses` — id, name
- [x] `enrollments` — id, student_id, course_id, class, school_year_id
- [x] `course_configs` — id, class, course_id, school_year_id, weight_exams, weight_oral, weight_homework, weight_quizzes
- [x] `weight_overrides` — id, enrollment_id, weight_exams, weight_oral, weight_homework, weight_quizzes
- [x] `grades` — id, enrollment_id, category (enum: exams/oral/homework/quizzes), value, date

---

## Phase 2 — Calculation Engine

- [ ] Category average: exams (mean of 1–5 grades)
- [ ] Category average: oral (mean of 1–5 grades)
- [ ] Category average: homework (mean of {1,3,5} grades)
- [ ] Category average: quizzes (mean of {1,3,5} grades)
- [ ] Weighted final grade (inherits CourseConfig, overridden by weight_override if exists)
- [ ] Final grade rounding to 1 decimal
- [ ] Pass/fail logic: ≤ 4.0 pass, > 4.0 fail
- [ ] Weight validation: sum must equal 100%
- [ ] Handle missing category grades (weight=0 or no grades entered yet)

---

## Phase 3 — Core Screens

### Screen 1 — Student Management
- [ ] List all students
- [ ] Add new student (name)
- [ ] Edit student name
- [ ] Create enrollment (assign student to course + class + school year)
- [ ] Edit / delete enrollment

### Screen 2 — Course Config
- [ ] Select class + course + school year
- [ ] Set weights for 4 categories (live validation: must sum to 100%)
- [ ] Save as default for that class/course/year
- [ ] Set per-student weight override on enrollment

### Screen 3 — Grade Entry
- [ ] Select enrollment (student + course + year)
- [ ] View existing grades per category
- [ ] Add individual grade entry (date + value)
- [ ] Edit / delete individual grade
- [ ] Input constraints: homework + quizzes locked to {1, 3, 5}
- [ ] Live display of category average after each entry

---

## Phase 4 — Display Screens

### Screen 4 — Student Detail
- [ ] Select student
- [ ] List all enrollments (course + class + year)
- [ ] Per enrollment: show 4 category averages + final grade
- [ ] Expandable category view: show all individual grades
- [ ] Visual indicator: pass (green) / fail (red)

### Screen 5 — Dashboard
- [ ] Filter by school year
- [ ] Filter by class
- [ ] Filter by course
- [ ] Student list with final grade column
- [ ] Quick visual pass/fail indicator per student
- [ ] Click student → navigate to Student Detail

---

## Phase 5 — Polish & Edge Cases

- [ ] Empty state handling (no grades entered, unconfigured weights)
- [ ] Confirmation dialogs for delete actions
- [ ] Input validation error messages (clear, non-technical language)
- [ ] Consistent navigation (back buttons, breadcrumb labels)
- [ ] App runs without terminal window on Windows
- [ ] Test .exe on Windows machine
- [ ] README reviewed by non-technical user

---

## Phase 6 — Future (Post-MVP)

- [ ] German grading scale (1–6) as switchable option
- [ ] Teacher-defined categories per course
- [ ] Export grade overview to PDF (for showing students)
- [ ] Configurable rounding thresholds
- [ ] Backup / export database
