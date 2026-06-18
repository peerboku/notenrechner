"""UI string dictionary. The app ships German-first; English is kept so a
language switch later is a one-line change (LANG = "en").

"Note" (grade) vs "Notiz" (free-text note) — never mix these up in German.
"""

LANG = "de"

_STRINGS = {
    "en": {
        # Top bar
        "class_label": "Class:",
        "no_class_yet": "— no class yet —",
        "new_class": "New Class",

        # Common buttons
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "rename": "Rename",
        "remove": "Remove",
        "create": "Create",
        "start": "Start",

        # Student list
        "enter_grades": "Enter Grades",
        "editing": "Editing: {name}",
        "notation_hint": "You can type  2+ (= 1.75)   2-3 (= 2.5)   2,5 (= 2.5)",
        "notation_hint_short": "2+  2-3  2,5 ...",
        "header_click_hint": "Click a category column to enter grades",
        "date_label": "Date:",
        "note_label": "Note:",
        "name_column": "Name",
        "final_column": "Final",
        "add_student": "+  Add Student",
        "student_name_placeholder": "Student name…",
        "no_students": "No students in this class yet.",
        "view_grades": "View Grades",

        # Confirm save dialog
        "confirm_save_title": "Confirm Save",
        "confirm_blank_one": "1 student has no grade for this entry.\nSave anyway?",
        "confirm_blank_many": "{count} students have no grade for this entry.\nSave anyway?",
        "save_anyway": "Save anyway",

        # Remove student dialog
        "remove_student_title": "Remove Student",
        "remove_student_text": "Remove this student from the class?\nAll their grades will also be deleted.",

        # Weight panel
        "hide_weights": "Hide Weights",
        "show_weights": "Show Weights",
        "load_preset": "Load Preset:",
        "no_presets_option": "— no presets —",
        "choose_preset_option": "— load a preset —",
        "sum_empty": "Sum: —",
        "sum_value": "Sum: {total}%",
        "save_as_preset": "Save as New Preset",
        "custom_weights": "Custom",
        "save_preset_title": "Save Preset",
        "preset_name_label": "Preset name:",
        "preset_name_placeholder": "e.g. Standard",
        "name_required": "Name is required.",

        # Events panel
        "show_events": "Show Entries",
        "hide_events": "Hide Entries",
        "events_none": "(none)",
        "events_one": "(1 entry)",
        "events_many": "({count} entries)",
        "no_events": "No entries yet.",
        "delete_event_title": "Delete Entry",
        "delete_event_text": "Delete this entry and all its grades?",
        "cannot_be_undone": "This cannot be undone.",

        # Enter grades modal
        "category": "Category",
        "date": "Date",
        "note": "Note",
        "date_placeholder": "e.g. 28.05.2026  (optional)",
        "optional": "optional",
        "select_category": "Please select a category.",

        # New class modal
        "class_field": "Class",
        "class_placeholder": "e.g. 4B",
        "course_field": "Course",
        "course_placeholder": "e.g. English",
        "year_field": "School Year",
        "year_placeholder": "e.g. 2025/26",
        "class_required": "Class label is required.",
        "course_required": "Course is required.",
        "year_required": "School year is required.",

        # Settings modal
        "settings": "Settings",
        "weight_presets": "Weight Presets",
        "no_presets_hint": "No presets yet. Save one from the weight panel.",
        "rename_preset_title": "Rename Preset",
        "new_name_label": "New name:",
        "delete_preset_title": "Delete Preset",
        "delete_preset_text": 'Delete preset "{name}"?\nThis cannot be undone.',
    },
    "de": {
        # Top bar
        "class_label": "Klasse:",
        "no_class_yet": "— noch keine Klasse —",
        "new_class": "Neue Klasse",

        # Common buttons
        "save": "Speichern",
        "cancel": "Abbrechen",
        "delete": "Löschen",
        "rename": "Umbenennen",
        "remove": "Entfernen",
        "create": "Erstellen",
        "start": "Starten",

        # Student list
        "enter_grades": "Noten eintragen",
        "editing": "Eingabe: {name}",
        "notation_hint": "Eingabe möglich:  2+ (= 1.75)   2-3 (= 2.5)   2,5 (= 2.5)",
        "notation_hint_short": "2+  2-3  2,5 ...",
        "header_click_hint": "Kategorie anklicken zum Noten eintragen",
        "date_label": "Datum:",
        "note_label": "Notiz:",
        "name_column": "Name",
        "final_column": "Endnote",
        "add_student": "+  Schüler hinzufügen",
        "student_name_placeholder": "Name…",
        "no_students": "Noch keine Schüler in dieser Klasse.",
        "view_grades": "Noten anzeigen",

        # Confirm save dialog
        "confirm_save_title": "Speichern bestätigen",
        "confirm_blank_one": "1 Schüler hat keine Note für diesen Eintrag.\nTrotzdem speichern?",
        "confirm_blank_many": "{count} Schüler haben keine Note für diesen Eintrag.\nTrotzdem speichern?",
        "save_anyway": "Trotzdem speichern",

        # Remove student dialog
        "remove_student_title": "Schüler entfernen",
        "remove_student_text": "Diesen Schüler aus der Klasse entfernen?\nAlle Noten werden ebenfalls gelöscht.",

        # Weight panel
        "hide_weights": "Gewichtung ausblenden",
        "show_weights": "Gewichtung anzeigen",
        "load_preset": "Vorlage laden:",
        "no_presets_option": "— keine Vorlagen —",
        "choose_preset_option": "— Vorlage wählen —",
        "sum_empty": "Summe: —",
        "sum_value": "Summe: {total}%",
        "save_as_preset": "Als neue Vorlage speichern",
        "custom_weights": "Eigene",
        "save_preset_title": "Vorlage speichern",
        "preset_name_label": "Name der Vorlage:",
        "preset_name_placeholder": "z. B. Standard",
        "name_required": "Bitte einen Namen eingeben.",

        # Events panel
        "show_events": "Einträge anzeigen",
        "hide_events": "Einträge ausblenden",
        "events_none": "(keine)",
        "events_one": "(1 Eintrag)",
        "events_many": "({count} Einträge)",
        "no_events": "Noch keine Einträge.",
        "delete_event_title": "Eintrag löschen",
        "delete_event_text": "Diesen Eintrag und alle zugehörigen Noten löschen?",
        "cannot_be_undone": "Das kann nicht rückgängig gemacht werden.",

        # Enter grades modal
        "category": "Kategorie",
        "date": "Datum",
        "note": "Notiz",
        "date_placeholder": "z. B. 28.05.2026  (optional)",
        "optional": "optional",
        "select_category": "Bitte eine Kategorie wählen.",

        # New class modal
        "class_field": "Klasse",
        "class_placeholder": "z. B. 4B",
        "course_field": "Fach",
        "course_placeholder": "z. B. Englisch",
        "year_field": "Schuljahr",
        "year_placeholder": "z. B. 2025/26",
        "class_required": "Bitte eine Klasse angeben.",
        "course_required": "Bitte ein Fach angeben.",
        "year_required": "Bitte ein Schuljahr angeben.",

        # Settings modal
        "settings": "Einstellungen",
        "weight_presets": "Gewichtungs-Vorlagen",
        "no_presets_hint": "Noch keine Vorlagen. Speichere eine über die Gewichtung.",
        "rename_preset_title": "Vorlage umbenennen",
        "new_name_label": "Neuer Name:",
        "delete_preset_title": "Vorlage löschen",
        "delete_preset_text": 'Vorlage "{name}" löschen?\nDas kann nicht rückgängig gemacht werden.',
    },
}


def t(key: str, **kwargs) -> str:
    text = _STRINGS.get(LANG, {}).get(key) or _STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text
