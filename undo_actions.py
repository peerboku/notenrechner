"""Undo/redo action classes.

Each action captures enough data to both undo and redo the operation.
"""
from __future__ import annotations


class AddEventAction:
    """A bulk grade-entry event: one GradeEvent + N Grade records."""

    def __init__(
        self,
        event_id: int,
        event_snapshot: dict,        # {course_config_id, category_id, date, note}
        grade_snapshots: list[dict], # [{enrollment_id, category_id, value, date}, ...]
    ):
        self._event_id = event_id
        self._event_snapshot = event_snapshot
        self._grade_snapshots = grade_snapshots
        self.description = "Add Event"

    def undo(self) -> None:
        from database.grades import delete_grades_by_event
        from database.grade_events import delete_event
        delete_grades_by_event(self._event_id)
        delete_event(self._event_id)

    def redo(self) -> None:
        from database.grade_events import add_event
        from database.grades import add_grade
        self._event_id = add_event(**self._event_snapshot)
        for gs in self._grade_snapshots:
            add_grade(event_id=self._event_id, **gs)
