# Notenrechner — Teacher Guide

A desktop app for managing and calculating student grades. All data is stored locally on your computer. No internet connection required.

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

The sections below describe the full app as it will work when complete.

---

## Installation

1. Download `Notenrechner.exe` from the [Releases page](https://github.com/peerboku/notenrechner/releases) (or on the right side of this page)
2. Double-click to open — no installation needed
3. On first run the app creates a file called `grades.db` in the same folder. Do not delete this file — it contains all your data.

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

**Final grade** = weighted average of the four category grades.

Example with weights Exams 50%, Oral 20%, Homework 15%, Quizzes 15%:

```
Exams average:    2.0  × 50% = 1.00
Oral average:     3.0  × 20% = 0.60
Homework average: 2.33 × 15% = 0.35
Quizzes average:  1.67 × 15% = 0.25

Final grade: 1.00 + 0.60 + 0.35 + 0.25 = 2.2
```

The final grade is rounded to one decimal place.

Grades use the Austrian scale: **1 is the best, 5 is the worst. Grade 4 is the lowest passing grade.**

---

## Input Rules

- Exams and Oral grades: any value from 1 to 5
- Homework and Quizzes: only 1 (good), 3 (okay), or 5 (bad)

---

## Getting Started — Step by Step

### Step 1: Add your students ✅ Available now
Go to **Schüler** in the sidebar. Enter each student's name and add them. Students are stored globally — you only add them once, even if they appear in multiple courses.

### Step 2: Create enrollments ✅ Available now
For each student, click **+ Einschreibung**. Assign them to a course, a class (e.g. "4B"), and a school year (e.g. "2024/25"). This connects the student to a specific course for a specific year.

### Step 3: Set weights ✅ Available now
Go to **Kurskonfiguration**. Select a class, course, and school year. Set the percentage weight for each of the four categories. The weights must add up to 100%.

If a category does not apply to a course, set its weight to 0% — it will be ignored in the calculation.

You can also set different weights for an individual student if needed — this overrides the default for that student only. An optional note field lets you record the reason (e.g. "Legasthenie-Ausgleich").

### Step 4: Enter grades ✅ Available now
Go to **Noten eingeben**. Select a student and their enrollment. Add individual grades for each category as they come in throughout the year. Each panel shows the live category average, colour-coded green (pass) or red (fail).

### Step 5: View results *(coming soon)*
The **Dashboard** gives an overview of an entire class or course. Click any student to see a full breakdown: all category averages, the final grade, and every individual entry.

---

## Screens Overview

| Screen | Purpose | Status |
|---|---|---|
| Schüler | Add students and manage course enrollments | ✅ Available |
| Kurskonfiguration | Set category weights per class and course | ✅ Available |
| Noten eingeben | Add and edit individual grades | ✅ Available |
| Dashboard | Overview of all students with final grades | Coming soon |
| Schüler-Detail | Full grade breakdown for one student | Coming soon |

---

## School Year and Class

When a new school year begins, create a new school year (e.g. "2025/26") and add new enrollments for your students with their new class label. Previous years stay stored and viewable — nothing is overwritten.

---

## Your Data

All data is saved in a file called `grades.db` in the same folder as the app.

- Do not delete this file
- To back up your data, copy this file to a safe location (USB drive, cloud storage)
- If you move the app to a new computer, copy both `Notenrechner.exe` and `grades.db` together

---

## Grading Scale Reference

| Grade | Meaning |
|---|---|
| 1 | Sehr gut (Very good) |
| 2 | Gut (Good) |
| 3 | Befriedigend (Satisfactory) |
| 4 | Genügend (Sufficient) — lowest pass |
| 5 | Nicht genügend (Insufficient) — fail |
