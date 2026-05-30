# Notenrechner — Teacher Guide

Da ich viele Lehrerinnen und Lehrer im Freundes- und Familienkreis habe und mitbekommen habe, dass das Eintragen und Ausrechnen von Noten oft noch klassisch mit Stift, Papier und Taschenrechner passiert, habe ich mich entschieden, als kleines Hobbyprojekt eine simple und intuitive App zu bauen.
Die App ermöglicht es, Noten schnell einzutragen und übersichtlich darzustellen.

Der Markt an Notenrechner- und Verwaltungsapps ist bereits sehr gesättigt, aber trotzdem sind viele Apps entweder zu kompliziert in der Handhabung oder haben ein sehr veraltetes Design. 

Ich möchte euch die Chance geben, aktiv an der Gestaltung der App teilzunehmen — deshalb werde ich nach jeder Version eine kleine Feedbackrunde machen und eure Rückmeldungen direkt in den Prozess einfließen lassen.

Vielen Dank schon mal für eure Hilfe!

Liebe Grüße, Peer

---

> **Hinweis:** In der aktuellen Version sind sowohl die App selbst als auch diese Beschreibung noch auf Englisch. Eine deutsche Benutzeroberfläche ist für eine spätere Version geplant.

---

![Notenrechner Screenshot](docs/screenshot_notenrechner_v.0.5.0.png)

---

## Feedback

This is an early version and your experience with it matters. If you have a few minutes, please fill out the short feedback form — it helps shape what gets built next.

**[→ Give feedback](https://docs.google.com/forms/d/e/1FAIpQLSeE-4u26JZE-SWuTIOBHFQ7Oof3R2aXr3Ax9JmUPsxeXuW8rQ/viewform)**

Any thoughts are welcome: what felt confusing, what worked well, what you wish the app could do.

---

## Installation

### Windows
1. Download `Notenrechner.exe` from the [Releases page](https://github.com/peerboku/notenrechner/releases)
2. Double-click to open — no installation needed
3. On first run the app creates a file called `grades.db` in the same folder. **Do not delete this file** — it contains all your data.

### Mac
1. Download `Notenrechner-mac.zip` from the [Releases page](https://github.com/peerboku/notenrechner/releases)
2. Unzip the file — you will get `Notenrechner.app`
3. Move it to your Applications folder or any folder you prefer
4. On first run the app creates a file called `grades.db` in the same folder as the app. **Do not delete this file** — it contains all your data.

> **First launch on Mac:** Because the app is unsigned, macOS will block it the first time. To open it: right-click (or Ctrl-click) on `Notenrechner.app` → **Open** → click **Open** in the dialog that appears. You only need to do this once.

---

## Upgrading from an Earlier Version

> **If you have used v0.3.x or earlier**, the database format has changed and your existing data is not compatible with v0.5.0. You will need to start fresh.

**Steps to upgrade:**

1. Optional: keep a copy of your old `Notenrechner.exe` and `grades.db` somewhere safe for reference.
2. Download the new `Notenrechner.exe` and place it in a folder of your choice.
3. Run the new version. It will create a new `grades.db` automatically.
4. Re-enter your classes and grades in the new interface.

---

## Current Version (v0.5.0)

This is the first release of the redesigned interface. The previous version (v0.3.x) was evaluated and found to require too many steps for everyday use. This version is built around a single main screen that matches how a teacher actually works with a class.

**What works in this version:**

- Create classes (class label + course + school year)
- Set category weights with reusable presets — the app remembers which preset is applied to each class
- Add students to a class by name
- Enter grades class-wide after an event (e.g. a test returned — one grade per student at once)
- View category averages and final grades live in the student list
- Hover over any category average to see the individual grades behind it
- Manage and delete past grade events from the Events panel
- Manage weight presets (create, rename, delete) via the Settings gear icon
- Undo the last grade event with Ctrl+Z (Windows) or Cmd+Z (Mac)

**Not yet available (coming in a future release):**

- Full grade detail view per student (Screen 2)
- Individual weight overrides per student
- Print / PDF export

---

## How Grades Are Calculated

Every student receives one final grade per course. That grade is built from up to four categories:

| Category | Input type | Valid values |
|---|---|---|
| Exams | Continuous | Any value (e.g. 1.0 – 5.0) |
| Oral | Continuous | Any value (e.g. 1.0 – 5.0) |
| Homework | Discrete | Good (1), Okay (3), or Bad (5) only |
| Quizzes | Discrete | Good (1), Okay (3), or Bad (5) only|

**Category grade** = average of all individual entries in that category.

**Final grade** = weighted average of the category grades, rounded to one decimal place.

Categories with a weight of 0% are hidden from the student list and excluded from the final grade. Categories with no grades entered are also excluded.

Example with weights Exams 50%, Oral 20%, Homework 15%, Quizzes 15%:

```
Exams average:    2.0  × 50% = 1.00
Oral average:     3.0  × 20% = 0.60
Homework average: 2.33 × 15% = 0.35
Quizzes average:  1.67 × 15% = 0.25

Final grade: 1.00 + 0.60 + 0.35 + 0.25 = 2.2
```

---

## The Main Screen

At the top, select which class you are working with using the dropdown. Use **New Class** to set one up.

### Weight Panel

Shows the current category weights for the selected class. You can change the weights and click **Save** to apply them. The sum must equal 100% before saving is allowed.

Use **Load Preset** to apply a saved weight configuration. If you enter weights that don't match any existing preset, an option to **Save as New Preset** appears automatically. The dropdown always shows which preset is currently applied — when the panel is collapsed, the preset name appears next to the "Show Weights" button.

### Events Panel

Lists all grade events that have been saved for the current class. Click **Show Events** to expand it. Each event shows the category, date, and note. Use the **Delete** button to remove an event and all the grades linked to it — a confirmation will appear before anything is deleted.

### Student List

Shows every student with their current category averages and final grade. Hover over any category average to see the individual grade entries behind it.

**Entering grades after an event (e.g. homework returned today):**
Click **Add Event**, choose the category, optionally add a date and note, then confirm. The list switches into edit mode — enter one grade per student. You can leave students blank to skip them. At the top and bottom of the list there is a **Save** button. When you save, the app will tell you exactly how many students have no grade and ask you to confirm.

**To undo the last event:** press Ctrl+Z (or Cmd+Z on Mac). This removes all grades from that event and deletes the event record. The undo history is session-only — it resets when you close the app.

**Working with a student:**
Click on any student's name to open a small menu with the option to remove them from the class.

---

## Weight Presets

Presets let you save a set of weights under a name and reuse them across classes. To manage presets (rename or delete existing ones), open Settings via the gear icon in the top right.

---

## Your Data

All data is saved in a file called `grades.db` in the same folder as the app.

- **Do not delete this file**
- To back up your data, copy this file to a safe location (USB drive, cloud storage)
- If you move the app to a new computer, copy both `Notenrechner.exe` and `grades.db` together
