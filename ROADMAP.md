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
- [x] Gear icon (right side) → Settings modal

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
- [x] Columns: Name, one avg column per category with weight > 0, Final Grade — all always visible
- [x] Hover on category average cell → popover showing underlying grade entries (date + value per line)
- [x] Single click on student → action menu: View Grades (stub) / Remove
- [ ] "Add new student" at bottom of list — inline name input on click

### Event-Based Grade Entry
- [x] "Add Event" button → picker modal: category (required) + date (optional) + note (optional)
- [x] Column edit mode: distinct background on active column, "Editing: [Category]" label, other columns dimmed
- [x] Continuous category inputs: free float within grading scale range
- [x] Discrete category inputs: segmented control locked to discrete_values
- [x] Tab/Enter moves to next student, blank = skip
- [x] Save button at top and bottom of list
- [x] On save with blank entries: confirmation popup stating exact count of skipped students
- [x] Cancel discards all unsaved inputs
- [x] Saved entries linked to shared GradeEvent record via event_id

### Events Panel
- [x] Collapsible panel next to weight panel (starts collapsed)
- [x] Lists all grade events for the active class (category · date · note)
- [x] Delete button per event — confirmation dialog, deletes all linked grades
- [x] Counter badge ("3 events") always visible even when panel is collapsed
- [x] Refreshes automatically after Add Event save and after Ctrl+Z undo

### Other Fixes
- [x] When adding Event show already added Events to compare. 
- [x] Load Preset always shows default and doesnt remember when f.ex. standard was chosen.

---

## Phase 5b — Mac Build & CI

No UI work required. Pure CI and packaging task. Done here so both platforms are building before the first teacher feedback round — hand her whichever platform she uses.

- [x] Add `macos-latest` parallel job to GitHub Actions workflow alongside existing `windows-latest` job
- [x] PyInstaller produces `.app` bundle from macOS runner
- [x] Both artifacts uploaded to the same GitHub release
- [ ] Test `.app` locally on Mac — confirm app launches, no terminal window, no import errors
- [x] Document Gatekeeper workaround in README: right-click → Open on first launch (app is unsigned)

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
- Better to show all grade entries with hover. Or with press on grade unten drunter wird aufegeklappt und zeigt alle einetragnene Noten für alle Category grades. 
**Gate:** Do not start Phase 6 until layout and core flow are validated. Rework Screen 1 first if needed.

### Results (June 2026)
Multiple teachers interested — unhappy with existing software. Validated: class selection, weight panel, grade view. Pain points feed Phase 5c below.

---

## Phase 5c — Feedback Round 1 Rework

### Quick wins
- [x] Rename "Add Event" → "Enter Grades" everywhere the teacher sees it
- [x] Grade notation parser: accept "2+" (= 1.75), "2-" (= 2.25), "2-3" / "2/3" (= 2.5), comma decimals ("2,5")
- [x] Live feedback in grade inputs: red border while invalid, shorthand converts to numeric value on focus-out
- [x] Notation hint shown in the editing bar for continuous categories
- [x] Discrete categories display symbols (+ / ~ / −) instead of 1/3/5 — `discrete_labels` column added with migration; numbers stay internal
- [x] Grade tooltips show symbols for discrete categories
- [x] Empty class state: centered "No students in this class yet." + prominent "+ Add Student" button
- [x] Add-student row is a visible "+ Add Student" button that reveals the name entry (also fixes Phase 8 FocusOut item)
- [x] Weight fields accept comma decimals
- [x] German UI: all user-facing strings moved to `i18n.py` dictionary (`t(key)`), German active, English kept for a later language switch
- [x] Default category names migrated to German: Schularbeiten, Mündlich, Hausübungen, Tests

### Flow rework (approach confirmed with user)
- [x] Kill the Enter Grades modal: clicking a category column header starts edit mode for that column directly, date defaults to today, date/note editable inline in the editing bar
- [x] Replace hover tooltips with expand/collapse: clicking a student name expands a detail strip below showing all grades for all categories; action menu moves to a "⋯" button at row end
- [x] Detail strip: proper table layout — one row per date, columns Notiz | Datum | [categories]; multiple grades of the same category on the same date appear as separate rows

### Design rethink — Paper Gradebook Style
> Design goal shifted: audience is older teachers, not tech-savvy users. Drop iOS/Apple references. Aim for the look and feel of a paper gradebook — familiar, readable, no surprises.

#### Design principles
- [ ] **Grid lines, not cards** — visible borders and table rules everywhere; no shadow-only floating panels; the student list should look like a ruled table
- [ ] **Warm muted palette** — replace dark mode with soft off-white or cream background; single calm accent color (navy or forest green); no pure white, no pure black
- [ ] **One accent color, one purpose** — the accent is used identically everywhere for the same meaning (e.g. always forest green for the primary save action); never repurposed as a label color or decoration elsewhere; reduces relearning
- [ ] **Persistent labeled navigation** — no icon-only nav, no hamburger menus; if there are multiple views, show them as visible text tabs at all times; sidebar class list already moves in this direction
- [ ] **Predictable button placement** — Save always in the same corner, Cancel always in the same spot across every screen and modal; older users build spatial memory faster than icon/concept memory

#### Previously planned — still valid under new direction
- [x] Student list as hero element; weight/events panels visually recede (toggle buttons muted, panels compact)
- [x] "Einträge anzeigen" removed toggle — events list always visible
- [x] Weight panel sum: display as integer when whole number
- [x] Replace top-bar class dropdown with left sidebar list
- [ ] Fix detail strip cells: empty Notiz and empty Datum show "—" instead of blank
- [ ] Add chevron (▶ / ▼) to student name cells so expandability is obvious
- [ ] Add text labels to icon-only controls (e.g. ⚙ gear button)
- [ ] Every actionable element permanently visible — no hiding behind ⋯ menus or hover
- [ ] Replace ⋯ button with explicit "Bearbeiten" text button per student row
- [ ] Strict color hierarchy: one primary accent, never repurposed
- [ ] Make the two "save preset" buttons in the weight panel visually separate
- [ ] Visible confirmation after "Speichern" for grades and weight changes
- [ ] Add confirmation step before all destructive actions
- [ ] Plain language audit (no technical terms anywhere)
- [ ] Better cue that leads naturally to grade entry

## Polish 
- [ ] ? - Button next to the grade or more visible features that explains how grades can be typed in 
- [ ] Little tutorial with arrows when starting the app for first time
- [ ] wenn kein Datum eingetragen ist, anstatt "-" Textblock "kein Datum eingetragen"
- [ ] Add light mode option to settings 
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

## Phase 7 — Settings Modal & Individual Weighting

### Settings Modal
- [x] Accessible via gear icon in top bar
- [x] Preset management: list, create, rename, delete (with confirmation on delete)
- [!] Grading scale selector — removed; scale has no effect on calculation or pass/fail threshold, teachers self-regulate input range naturally

### Individual Weighting Modal
- [ ] Single click on student → action menu includes: Add Individual Weighting (or Edit)
- [ ] Individual weight override indicator: dot/icon in Name column, tooltip shows custom weights on hover
- [ ] Class weights shown as read-only reference in modal
- [ ] Weight fields (one per active category) pre-filled with class weights
- [ ] Note field (optional)
- [ ] Save/Apply (disabled until sum = 100%)
- [ ] "Reset to Class Defaults" removes override

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
- [ ] "Add student" field clears when focus is lost (FocusOut on CTkEntry compound widget)
- [ ] Add scrollable Lists with mouse/touchpad
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
