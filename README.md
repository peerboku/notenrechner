# Notenrechner — Teacher Guide

A desktop app for managing and calculating student grades. All data is stored locally on your computer. No internet connection required.

---

## Installation

1. Download `Notenrechner.exe` from the [Releases page](https://github.com/peerboku/notenrechner/releases)
2. Double-click to open — no installation needed
3. On first run the app creates a file called `grades.db` in the same folder. Do not delete this file — it contains all your data.

---
## Current Version (v0.3.2 — Early Preview)

This is an early preview release for testing purposes. Not all features are available yet.

**What works in this version:**

- Add, rename, and delete students
- Assign students to courses, classes, and school years
- Set category weights per course — with an optional per-student override and reason note
- Enter grades per category, with live category averages
- Input validation: homework and quiz grades are locked to 1, 3, or 5

**Not yet available (coming in a future release):**

- Overview of all students with final grades (Dashboard)
- Full grade breakdown per student across all courses (Student Detail)

**Note:** The next release will also include a reworked interface. The current version was tested internally and found to require too many steps for comfortable daily use. The workflow will be simplified before the app is ready for regular use.

## Next Version (v0.4.0 — First Preview)

This version introduces a fully reworked interface. The previous version was evaluated and found to require too many steps for comfortable daily use. The new interface is built around two screens and is designed to match how a teacher actually thinks about their class.

**What works in this version:**

- Create a class (class label + course + school year)
- Set category weights with reusable presets
- Add students to a class by name
- Enter grades after a class event (e.g. homework returned — enter grades for the whole class at once)
- View and edit all grades for one student in detail
- Final grades and category averages calculated live
- Individual weight overrides per student (e.g. for students with special needs)
- Print student grade overview for parent meetings

---

## How Grades Are Calculated

Every student receives one final grade per course. That final grade is built from four categories:

| Category | What counts |
|---|---|
| Exams | Written exams and tests |
| Oral | Oral participation and oral exams |
| Homework | Homework assignments |
| Quizzes | Short quizzes |

**Category grade** = average of all individual entries in that category.

**Final grade** = weighted average of the four category grades. If you set a category's weight to 0%, that category is hidden from the class view and not included in the final grade.

Example with weights Exams 50%, Oral 20%, Homework 15%, Quizzes 15%:

```
Exams average:    2.0  × 50% = 1.00
Oral average:     3.0  × 20% = 0.60
Homework average: 2.33 × 15% = 0.35
Quizzes average:  1.67 × 15% = 0.25

Final grade: 1.00 + 0.60 + 0.35 + 0.25 = 2.2
```

The final grade is rounded to one decimal place.

The app supports both the Austrian and German grading scales. You can switch between them in Settings (gear icon, top right).

**Austrian scale** — 1 is best, 5 is worst. Grade 4 is the lowest passing grade.

| Grade | Meaning |
|---|---|
| 1 | Sehr gut (Very good) |
| 2 | Gut (Good) |
| 3 | Befriedigend (Satisfactory) |
| 4 | Genügend (Sufficient) — lowest pass |
| 5 | Nicht genügend (Insufficient) — fail |

**German scale** — 1 is best, 6 is worst. Grade 4 is the lowest passing grade.

| Grade | Meaning |
|---|---|
| 1 | Sehr gut (Very good) |
| 2 | Gut (Good) |
| 3 | Befriedigend (Satisfactory) |
| 4 | Ausreichend (Sufficient) — lowest pass |
| 5 | Mangelhaft (Poor) — fail |
| 6 | Ungenügend (Insufficient) — fail |

---

## Input Rules

- Exams and Oral grades: any value within the active grading scale (1–5 for Austria, 1–6 for Germany)
- Homework and Quizzes: only 1 (good), 3 (okay), or 5 (bad)

---

## The Two Screens

### Screen 1 — Class View

Your main working screen. At the top, select which class you are working with. The weight panel shows the current category weights — you can change these and save at any time.

The student list shows every student with their current category averages and final grade. Hover over any average to see the individual grades behind it.

**Entering grades after an event (e.g. homework returned today):**
Click "Add Event", choose the category, optionally add a date and note, then enter one grade per student. You can skip students who were absent. When you save, the app will tell you if any students are missing a grade and ask you to confirm.

**Working with a student:**
Click on any student name to open a small menu: view their full grade detail, add an individual weight override, or remove them from the class.

### Screen 2 — Student Detail

A full view of one student's grades. Accessed by clicking "View Grades" from the class list. Use the back button to return to the class.

Here you can see all grades grouped by category, edit any grade by clicking on it, and add new grades individually. This is also where end-of-semester teachers can enter all grades for one student at once.

The print button produces a clean PDF of this view — suitable for parent meetings.

---

## Weight Presets

Presets let you save a set of weights under a name and reuse them across classes. The weight panel in Screen 1 has a "Load Preset" dropdown. If you change the weights to something that doesn't match any existing preset, an option to save the new combination as a preset appears automatically.

To manage presets (create, rename, delete), open Settings via the gear icon.

---

## Individual Weight Overrides

If a student needs different weights than the rest of the class (for example, due to a learning accommodation), click the student's name → "Add Individual Weighting". Enter the weights and an optional note explaining the reason. The student's row will show a small indicator so you can see at a glance that their grade uses different weights.

---

## Undo and Redo

Most actions can be undone. Use the undo button (or keyboard shortcut) to reverse the last action. If you entered grades for a whole class event and made a mistake, one undo reverses the entire event. Redo reinstates undone actions. The undo history resets when you close the app.

---

## Your Data

All data is saved in a file called `grades.db` in the same folder as the app.

- Do not delete this file
- To back up your data, copy this file to a safe location (USB drive, cloud storage)
- If you move the app to a new computer, copy both `Notenrechner.exe` and `grades.db` together
