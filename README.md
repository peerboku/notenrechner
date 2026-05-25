# Grade Calculator — Teacher Guide

A desktop app for managing and calculating student grades. All data is stored locally on your computer. No internet connection required.

---

## Installation

1. Download the file `Notenrechner.exe`
2. Double-click to open — no installation needed
3. The app creates a database file (`grades.db`) in the same folder on first run. Do not delete this file — it contains all your data.

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

- Exams and Oral grades: any grade from 1 to 5
- Homework and Quizzes: only 1 (good), 3 (okay), or 5 (bad)

---

## Getting Started — Step by Step

### Step 1: Add your students
Go to **Student Management**. Enter each student's name and add them. Students are stored globally — you only add them once, even if they appear in multiple courses.

### Step 2: Create enrollments
For each student, create an enrollment: assign them to a course, a class (e.g. "4B"), and a school year (e.g. "2024/25"). This connects the student to a specific course for a specific year.

### Step 3: Set weights
Go to **Course Config**. Select a class, course, and school year. Set the percentage weight for each category. The four weights must add up to 100%.

If a category does not apply to a course, set its weight to 0%. It will be ignored in the calculation.

You can also set different weights for an individual student if needed — this overrides the default for that student only.

### Step 4: Enter grades
Go to **Grade Entry**. Select a student and their enrollment. Add individual grades for each category as they come in throughout the year. The category average and final grade update automatically.

### Step 5: View results
Go to **Student Detail** to see a full breakdown for any student: all courses, all category averages, the final grade, and every individual entry.

Use the **Dashboard** to get an overview of an entire class or course at once.

---

## Screens Overview

| Screen | Purpose |
|---|---|
| Dashboard | Overview of all students, filter by year / class / course |
| Student Detail | Full grade breakdown for one student |
| Grade Entry | Add and edit individual grades |
| Course Config | Set category weights per class and course |
| Student Management | Add students and manage course enrollments |

---

## School Year and Class

When a new school year begins, create a new school year (e.g. "2025/26") and create new enrollments for your students with their new class label. Previous years remain stored and viewable — nothing is overwritten.

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
