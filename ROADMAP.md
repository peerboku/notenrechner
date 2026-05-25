# Grade Calculator — Roadmap

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done
- [!] Paused — needs rethink

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
- [x] `weight_overrides` — id, enrollment_id, weight_exams, weight_oral, weight_homework, weight_quizzes, note
- [x] `grades` — id, enrollment_id, category (enum: exams/oral/homework/quizzes), value, date

---

## Phase 2 — Calculation Engine

- [x] Category average: exams (mean of 1–5 grades)
- [x] Category average: oral (mean of 1–5 grades)
- [x] Category average: homework (mean of {1,3,5} grades)
- [x] Category average: quizzes (mean of {1,3,5} grades)
- [x] Weighted final grade (inherits CourseConfig, overridden by weight_override if exists)
- [x] Final grade rounding to 1 decimal
- [x] Pass/fail threshold: ≤ 4.0 pass, > 4.0 fail (used for color coding in UI)
- [x] Weight validation: sum must equal 100%
- [x] Handle missing category grades (weight=0 or no grades entered yet)

---

## Phase 3 — Core Screens

### Screen 1 — Student Management ✅
- [x] List all students
- [x] Add new student (name)
- [x] Edit student name
- [x] Create enrollment (assign student to course + class + school year)
- [x] Edit / delete enrollment

### Screen 2 — Course Config ✅
- [x] Select class + course + school year
- [x] Set weights for 4 categories (live validation: must sum to 100%)
- [x] Save as default for that class/course/year
- [x] Set per-student weight override on enrollment
- [x] Optional note field on weight override (reason for individual weighting)

### Screen 3 — Grade Entry ✅
- [x] Select enrollment (student + course + year)
- [x] View existing grades per category
- [x] Add individual grade entry (date + value)
- [x] Edit / delete individual grade
- [x] Input constraints: homework + quizzes locked to {1, 3, 5} via segmented button
- [x] Live display of category average after each entry (color-coded pass/fail)

---

## ⚠️ UX Rethink — Before Continuing

**Status: Paused for redesign**

After building Screens 1–3, the overall workflow was evaluated and found to be too complex for a non-technical teacher audience. The current structure requires too many separate steps and concepts before a teacher can do anything useful.

### Problems identified
- The concept of "enrollment" (student × course × class × year) is not intuitive — a teacher thinks in terms of "my class" not "enrollment records"
- The setup sequence (add students → create courses → set weights → create enrollments → enter grades) is too long and not guided
- The filter/load pattern (pick 3 dropdowns, click "Laden") is repeated across multiple screens and feels like a database tool, not a teacher app
- Navigating between 5 separate screens to complete one task breaks the mental model
- No guided first-run experience — an empty app with 5 screens gives no hint of where to start

### Direction for redesign
- Rethink the primary workflow: what does the teacher actually do on a typical day?
- Consider a more class-centric view (teacher picks their class first, then works within it)
- Reduce or hide the enrollment abstraction — it should be an implementation detail, not a UI concept
- Explore whether some screens can be merged (e.g. grade entry + student detail in one place)
- Consider a guided setup flow for first-time use
- Get feedback from the actual teacher before building Phases 4 and 5

### What to preserve
- The data model and calculation engine are solid — no changes needed there
- The DB schema is flexible enough to support a redesigned UI
- Individual screen components can likely be reused, just reorganised

---

## Phase 4 — Display Screens [!]

> Paused pending UX rethink above.

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

## Phase 5 — Polish & Edge Cases [!]

> Paused pending UX rethink above.

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
