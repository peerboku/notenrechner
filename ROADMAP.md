# Grade Calculator — Roadmap

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done
- [!] Paused / needs rethink
- [👩‍🏫] Teacher feedback round

---

## Phase 1 — Project Setup & Foundation ✅

- [x] Initialize Python project structure
- [x] Set up virtual environment
- [x] Install dependencies: `customtkinter`, `pyinstaller`
- [x] Create SQLite database file on first run
- [x] Implement DB schema (all tables)
- [x] Write data access layer (CRUD functions for all entities)
- [x] Set up GitHub repository
- [x] Add GitHub Actions workflow for Windows .exe build

---

## Phase 2 — Calculation Engine ✅

- [x] Category average: mean of all entries per category
- [x] Weighted final grade (inherits CourseConfig, overridden by WeightOverride if exists)
- [x] Final grade rounding to 1 decimal
- [x] Pass/fail threshold (Austria: ≤ 4.0 pass, > 4.0 fail)
- [x] Weight validation: sum must equal 100%
- [x] Handle missing category grades (excluded from weighted average)

---

## Phase 3 — First Prototype (Scrapped UI, Logic Preserved) ✅

Phases 1–3 produced a working prototype with 5 screens. The prototype confirmed the calculation engine is correct. The UI was found too complex for a non-technical teacher audience and is being replaced entirely. DB schema, calculation engine, and individual components may be reused.

---

## Phase 4 — Schema Migration

The data model has been redesigned for flexibility (dynamic categories, dynamic weights, grading scale setting). The old schema used hardcoded category enums and fixed weight columns. Everything below must be migrated before any new UI is built.

### New / changed tables
- [x] `categories` table — id, name, input_type (continuous | discrete), discrete_values, is_default
- [x] Seed 4 default categories on first run: Exams (continuous), Oral (continuous), Homework (discrete 1,3,5), Quizzes (discrete 1,3,5)
- [x] `course_config_weights` table — id, course_config_id, category_id, weight (replaces fixed weight columns on CourseConfig)
- [x] `weight_presets` table — id, name
- [x] `weight_preset_weights` table — id, weight_preset_id, category_id, weight
- [x] `weight_override_weights` table — id, weight_override_id, category_id, weight (replaces fixed weight columns on WeightOverride)
- [x] Add `note` field to `weight_overrides` table
- [x] `grade_events` table — id, course_config_id, category_id, date (optional), note (optional)
- [x] Add `event_id` field to `grades` table (optional FK to grade_events)
- [x] Add `note` field to `grades` table
- [x] Change `grades.category` from enum to FK → `categories.id`
- [x] `settings` table — key, value (stub: grading_scale = "austria")

### Data access layer updates
- [x] Rewrite all weight read/write functions to use new weight row tables
- [x] Rewrite grade read/write to use category_id FK instead of enum
- [x] Add CRUD for categories
- [x] Add CRUD for weight presets and preset weights
- [x] Add CRUD for grade events
- [x] Add settings read/write

---

## Phase 5 — Redesigned UI: Screen 1 (Class View)

> Primary working screen. Teacher selects a class and works within it.

### Top Bar
- [x] Class selector dropdown (combined label: class + course + year, e.g. "4B · English · 2025/26")
- [x] "New Class" button → guided setup: class label, course, year, initial weights (with preset dropdown)
- [ ] Gear icon (right side) → Settings modal

### Weight Panel
- [x] Collapsible panel, open by default on first launch
- [x] Labeled toggle button ("Hide Weights" / "Show Weights") — not just a chevron
- [x] Preset dropdown ("Load Preset") at top of panel
- [x] Weight fields rendered dynamically from active categories
- [x] Live sum validation (red indicator if ≠ 100%), Save/Apply disabled until valid
- [x] "Save as New Preset" appears inline when weights don't match any existing preset
- [ ] Weight changes do not affect displayed grades until Save/Apply confirmed
- [ ] Loading a preset copies weights into CourseConfig — class owns weights independently after that

### Student List
- [ ] Columns: Name, one avg column per category with weight > 0, Final Grade — all always visible
- [ ] Hover on category average cell → popover showing underlying grade entries (date + value per line)
- [ ] Individual weight override indicator: dot/icon in Name column, tooltip shows custom weights on hover
- [ ] Single click on student → action menu: View Grades / Add Individual Weighting (or Edit) / Remove
- [ ] "Add new student" at bottom of list — inline name input on click

### Event-Based Grade Entry
- [ ] "Add Event" button → picker modal: category (required) + date (optional) + note (optional)
- [ ] Column edit mode: distinct background on active column, "Editing: [Category]" label, other columns dimmed
- [ ] Continuous category inputs: free float within grading scale range
- [ ] Discrete category inputs: segmented control locked to discrete_values
- [ ] Tab/Enter moves to next student, blank = skip
- [ ] Save button at top and bottom of list
- [ ] On save with blank entries: confirmation popup stating exact count of skipped students
- [ ] Cancel discards all unsaved inputs
- [ ] Saved entries linked to shared GradeEvent record via event_id

### Individual Weighting Modal
- [ ] Class weights shown as read-only reference
- [ ] Weight fields (one per active category) pre-filled with class weights
- [ ] Note field (optional)
- [ ] Save/Apply (disabled until sum = 100%)
- [ ] "Reset to Class Defaults" removes override
- [ ] Row indicator + tooltip once override is active

### Undo / Redo
- [ ] Linear undo/redo stack, session-only
- [ ] Bulk event save treated as single undo unit
- [ ] Single grade edit treated as single undo unit

---

## Phase 5b — Mac Build & CI

No UI work required. Pure CI and packaging task. Done here so both platforms are building before the first teacher feedback round — hand her whichever platform she uses.

- [ ] Add `macos-latest` parallel job to GitHub Actions workflow alongside existing `windows-latest` job
- [ ] PyInstaller produces `.app` bundle from macOS runner
- [ ] Both artifacts uploaded to the same GitHub release
- [ ] Test `.app` locally on Mac — confirm app launches, no terminal window, no import errors
- [ ] Document Gatekeeper workaround in README: right-click → Open on first launch (app is unsigned)

---

## 👩‍🏫 Feedback Round 1 — Layout & Core Flow

**When:** After Phase 5 is complete, before building Screen 2.
**What to test:** Show the teacher a running Screen 1 with real or dummy data loaded.
**Questions to answer:**
- Does the class selector at the top make sense immediately?
- Is the weight panel understandable without explanation?
- Can she find "Add Event" and understand what it does without guidance?
- Does the student list feel readable or overwhelming?
- Does column edit mode feel clear or confusing when active?

**Gate:** Do not start Phase 6 until layout and core flow are validated. Rework Screen 1 first if needed.

---

## Phase 6 — Redesigned UI: Screen 2 (Student Detail)

> Full grade view for one student. Accessed via "View Grades" from Screen 1.

- [ ] Back button to Screen 1
- [ ] Header: student name, class, course, year, final grade (prominent), category averages summary
- [ ] Grade list grouped by category
- [ ] Each entry shows: date (if exists) + value + note (if exists)
- [ ] Inline edit: click grade value to edit directly
- [ ] Add grade per category: value + date (optional, collapsed by default) + note (optional)
- [ ] Discrete category inputs locked to discrete_values
- [ ] All averages and final grade update live
- [ ] Undo / Redo (shared session stack with Screen 1)
- [ ] Print button → clean PDF layout (student info, category averages, full grade list)

---

## Phase 7 — Settings Modal

- [ ] Accessible via gear icon in top bar
- [ ] Grading scale selector — Austria and Germany both supported
- [ ] Preset management: list, create, rename, delete (with confirmation on delete)

---

## 👩‍🏫 Feedback Round 2 — Full Workflow End-to-End

**When:** After Phases 6 and 7 are complete, before Phase 8 polish.
**What to test:** Give the teacher a build with dummy data and ask her to complete a full realistic task sequence without guidance: open a class, check a student's grades, add a homework event for the whole class, open one student detail, fix a grade, print.
**Questions to answer:**
- Can she complete the full sequence without asking for help?
- Where does she hesitate or get stuck?
- Does the Student Detail screen feel useful for end-of-semester bulk entry?
- Is the print output suitable for parent meetings?
- Any missing features she immediately asks for?

**Gate:** Do not start Phase 8 polish until the full workflow is validated. Fix structural issues before polishing.

---

## Phase 8 — Polish & Distribution

- [ ] Empty state handling (no students, no grades, unconfigured weights)
- [ ] Confirmation dialogs for destructive actions (remove student, delete preset)
- [ ] Input validation error messages in plain non-technical language
- [ ] Consistent navigation and back button behaviour
- [ ] App runs without terminal window on Windows
- [ ] Test .exe on Windows machine

### Docs
- [ ] README updated for new UI
- [ ] README includes installation instructions for both Windows (.exe) and Mac (.app)

---

## 👩‍🏫 Feedback Round 3 — Pre-Release Validation

**When:** After Phase 8 is complete, on the actual built artifacts.
**What to test:** Hand the teacher the .exe (Windows) or .app (Mac) and ask her to use it independently for one real class — no guidance, no developer present if possible.
**Questions to answer:**
- Does the app open without confusion on her platform?
- Does she encounter any errors or dead ends?
- Does she trust the grade calculations?
- Would she use this instead of her current method?

**Gate:** Sign-off before treating the app as production-ready.

---

## Phase 9 — Future (Post-MVP)

- [ ] Moving students to a new school year / class
- [ ] Category management UI (teacher-defined categories: add, rename, set input type, set discrete values)
- [ ] Configurable rounding thresholds
- [ ] Database backup / export
