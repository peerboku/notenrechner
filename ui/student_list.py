import customtkinter as ctk
from database import course_configs, grades as grades_db
from database.categories import get_all_categories
from database.students import add_student
from database.enrollments import add_enrollment, get_enrollments_by_filter
from database.grade_events import add_event
from calculation.grades import category_average, calculate_final_grade

COL_NAME  = 200
COL_CAT   =  90
COL_FINAL =  90

_FINAL_COLOR       = ("#1a6fc4", "#5ba4f5")   # blue  — Final column
_EDIT_ACTIVE_COLOR = ("#b85c00", "#ff9040")   # amber — active edit column


class StudentListPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_id: int | None = None
        self._config_data = None
        self._active_cats: list = []

        # Edit-mode state
        self._edit_mode = False
        self._edit_cat: dict | None = None
        self._edit_event_data: dict | None = None
        self._edit_inputs: list[tuple[int, object]] = []

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Action bar (contents swapped between normal / edit mode)
        self._action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self._action_bar.pack(fill="x", padx=16, pady=(12, 8))
        self._set_action_bar_normal()

        # Column header
        self._header_frame = ctk.CTkFrame(
            self, fg_color=("gray85", "gray22"), corner_radius=0
        )
        self._header_frame.pack(fill="x", padx=16)

        # Scrollable rows
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        # Bottom save bar (hidden until edit mode)
        self._bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        # Not packed yet
        ctk.CTkButton(
            self._bottom_bar, text="Cancel",
            width=90, fg_color="transparent", border_width=1,
            command=self._cancel_edit,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            self._bottom_bar, text="Save", width=90,
            command=self._save_event,
        ).pack(side="right")

        # Add student (saved as self._add_row so edit mode can reorder it)
        self._add_row = ctk.CTkFrame(self, fg_color="transparent")
        self._add_row.pack(fill="x", padx=16, pady=(0, 12))
        self._add_entry = ctk.CTkEntry(
            self._add_row, placeholder_text="Add student…", width=COL_NAME
        )
        self._add_entry.pack(side="left")
        self._add_entry.bind("<Return>", self._on_add_student)

    # ── Action bar states ─────────────────────────────────────────────────────

    def _set_action_bar_normal(self):
        for w in self._action_bar.winfo_children():
            w.destroy()
        self._add_event_btn = ctk.CTkButton(
            self._action_bar, text="Add Event", width=110,
            state="disabled",
            command=self._open_add_event_modal,
        )
        self._add_event_btn.pack(side="left")

    def _set_action_bar_edit(self):
        for w in self._action_bar.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._action_bar,
            text=f"Editing: {self._edit_cat['name']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=_EDIT_ACTIVE_COLOR,
        ).pack(side="left")
        ctk.CTkButton(
            self._action_bar, text="Cancel",
            width=90, fg_color="transparent", border_width=1,
            command=self._cancel_edit,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            self._action_bar, text="Save", width=90,
            command=self._save_event,
        ).pack(side="right")

    # ── Public API ────────────────────────────────────────────────────────────

    def load_config(self, config_id: int | None):
        if self._edit_mode:
            self._exit_edit_mode()
        self._config_id = config_id
        if config_id is None:
            self._config_data = None
            self._active_cats = []
        else:
            self._config_data = course_configs.get_config_by_id(config_id)
            self._active_cats = _active_categories(config_id)
            self._add_event_btn.configure(state="normal")
        self._rebuild_header()
        self._rebuild_rows()

    def refresh(self):
        if self._config_id is not None:
            self._active_cats = _active_categories(self._config_id)
            self._rebuild_header()
        self._rebuild_rows()

    # ── Edit mode ─────────────────────────────────────────────────────────────

    def _open_add_event_modal(self):
        from ui.add_event_modal import AddEventModal
        if not self._active_cats:
            return
        AddEventModal(self, categories=self._active_cats, on_confirmed=self._enter_edit_mode)

    def _enter_edit_mode(self, cat: dict, date: str | None, note: str | None):
        self._edit_mode = True
        self._edit_cat = dict(cat)
        self._edit_event_data = {"date": date, "note": note}
        self._edit_inputs = []
        self._set_action_bar_edit()
        self._add_entry.configure(state="disabled")
        self._rebuild_header()
        self._rebuild_rows()
        # Insert bottom bar between scroll and add_row (avoid after=/before= — CTkScrollableFrame
        # delegates pack() to an internal _parent_frame, so self._scroll isn't in the pack manager)
        self._add_row.pack_forget()
        self._bottom_bar.pack(fill="x", padx=16, pady=(0, 4))
        self._add_row.pack(fill="x", padx=16, pady=(0, 12))

    def _exit_edit_mode(self):
        self._edit_mode = False
        self._edit_cat = None
        self._edit_event_data = None
        self._edit_inputs = []
        self._set_action_bar_normal()
        self._bottom_bar.pack_forget()
        if self._config_id is not None:
            self._add_event_btn.configure(state="normal")
        self._add_entry.configure(state="normal")
        self._rebuild_header()
        self._rebuild_rows()

    def _cancel_edit(self):
        self._exit_edit_mode()

    # ── Save event ────────────────────────────────────────────────────────────

    def _save_event(self):
        if not self._edit_cat:
            return

        valid_discrete: set[str] = set()
        if self._edit_cat["input_type"] == "discrete" and self._edit_cat["discrete_values"]:
            valid_discrete = {v.strip() for v in self._edit_cat["discrete_values"].split(",")}

        entries: list[tuple[int, float | None]] = []
        blank_count = 0

        for enrollment_id, widget in self._edit_inputs:
            if isinstance(widget, ctk.CTkSegmentedButton):
                val_str = widget.get()
                if val_str in valid_discrete:
                    entries.append((enrollment_id, float(val_str)))
                else:
                    entries.append((enrollment_id, None))
                    blank_count += 1
            else:
                val_str = widget.get().strip()
                if val_str:
                    try:
                        entries.append((enrollment_id, float(val_str)))
                    except ValueError:
                        entries.append((enrollment_id, None))
                        blank_count += 1
                else:
                    entries.append((enrollment_id, None))
                    blank_count += 1

        if blank_count > 0:
            _ConfirmSaveDialog(
                self, blank_count=blank_count,
                on_confirmed=lambda: self._do_save(entries),
            )
        else:
            self._do_save(entries)

    def _do_save(self, entries: list[tuple[int, float | None]]):
        cat_id = self._edit_cat["id"]
        date   = self._edit_event_data.get("date")
        note   = self._edit_event_data.get("note")

        event_id = add_event(
            course_config_id=self._config_id,
            category_id=cat_id,
            date=date,
            note=note,
        )
        for enrollment_id, value in entries:
            if value is not None:
                grades_db.add_grade(
                    enrollment_id=enrollment_id,
                    category_id=cat_id,
                    value=value,
                    date=date,
                    event_id=event_id,
                )
        self._exit_edit_mode()

    # ── Header ────────────────────────────────────────────────────────────────

    def _rebuild_header(self):
        for w in self._header_frame.winfo_children():
            w.destroy()

        _header_label(self._header_frame, "Name", COL_NAME, anchor="w", padx=(8, 0))
        for cat in self._active_cats:
            active = self._edit_mode and self._edit_cat and cat["id"] == self._edit_cat["id"]
            dim    = self._edit_mode and not active
            _header_label(self._header_frame, cat["name"], COL_CAT,
                          highlight=active, dim=dim)
        _divider(self._header_frame)
        _header_label(self._header_frame, "Final", COL_FINAL, final=True)

    # ── Rows ──────────────────────────────────────────────────────────────────

    def _rebuild_rows(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._edit_inputs = []

        if self._config_data is None:
            return

        enrollments = get_enrollments_by_filter(
            school_year_id=self._config_data["school_year_id"],
            class_=self._config_data["class"],
            course_id=self._config_data["course_id"],
        )

        if not enrollments:
            ctk.CTkLabel(
                self._scroll,
                text="No students yet.",
                text_color=("gray50", "gray60"),
                font=ctk.CTkFont(size=13),
            ).pack(pady=24)
            return

        for i, enrollment in enumerate(enrollments):
            bg = ("gray96", "gray18") if i % 2 == 0 else ("gray90", "gray16")
            self._build_row(enrollment, bg)

        if self._edit_mode:
            self._wire_navigation()

    def _build_row(self, enrollment, bg):
        row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=0)
        row.pack(fill="x")

        grades = grades_db.get_grades(enrollment["id"])
        by_cat: dict[int, list[float]] = {}
        for g in grades:
            by_cat.setdefault(g["category_id"], []).append(g["value"])

        _cell(row, enrollment["student_name"], COL_NAME, anchor="w", padx=(8, 0))

        for cat in self._active_cats:
            active = self._edit_mode and self._edit_cat and cat["id"] == self._edit_cat["id"]
            dim    = self._edit_mode and not active

            if active:
                widget = _input_widget(row, cat)
                self._edit_inputs.append((enrollment["id"], widget))
            else:
                avg = category_average(by_cat.get(cat["id"], []))
                _cell(row, f"{avg:.1f}" if avg is not None else "—", COL_CAT, dim=dim)

        _divider(row)

        try:
            final = calculate_final_grade(enrollment["id"])
        except ValueError:
            final = None
        _cell(row, str(final) if final is not None else "—", COL_FINAL,
              bold=True, final=True)

    def _wire_navigation(self):
        """Bind Return on continuous entries to focus the next student's input."""
        continuous = [
            (eid, w) for eid, w in self._edit_inputs
            if isinstance(w, ctk.CTkEntry)
        ]
        for i, (_, entry) in enumerate(continuous):
            if i + 1 < len(continuous):
                nxt = continuous[i + 1][1]
                entry._entry.bind("<Return>", lambda _e, n=nxt: n.focus_set())

    # ── Add student ───────────────────────────────────────────────────────────

    def _on_add_student(self, _event=None):
        name = self._add_entry.get().strip()
        if not name or self._config_data is None:
            return
        student_id = add_student(name)
        add_enrollment(
            student_id,
            self._config_data["course_id"],
            self._config_data["school_year_id"],
            self._config_data["class"],
        )
        self._add_entry.delete(0, "end")
        self._rebuild_rows()


# ── Confirm save dialog ───────────────────────────────────────────────────────

class _ConfirmSaveDialog(ctk.CTkToplevel):
    def __init__(self, parent, blank_count: int, on_confirmed):
        super().__init__(parent)
        self._on_confirmed = on_confirmed
        self.title("Confirm Save")
        self.geometry("360x190")
        self.resizable(False, False)
        self.grab_set()

        noun = "student has" if blank_count == 1 else "students have"
        ctk.CTkLabel(
            self,
            text=f"{blank_count} {noun} no grade for this event.\nSave anyway?",
            font=ctk.CTkFont(size=13),
            justify="center",
        ).pack(pady=(36, 20), padx=24)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkButton(
            btn_row, text="Cancel",
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text="Save anyway",
            command=self._confirm,
        ).pack(side="right")

    def _confirm(self):
        self._on_confirmed()
        self.destroy()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _active_categories(config_id: int) -> list:
    weights = course_configs.get_weights(config_id)
    return [c for c in get_all_categories() if weights.get(c["id"], 0) > 0]


def _input_widget(parent, cat: dict):
    """Return a grade input widget appropriate for the category input type."""
    if cat["input_type"] == "discrete" and cat["discrete_values"]:
        values = [v.strip() for v in cat["discrete_values"].split(",")]
        seg = ctk.CTkSegmentedButton(
            parent, values=values, width=COL_CAT, dynamic_resizing=False
        )
        seg.set("")   # nothing selected = skipped
        seg.pack(side="left", padx=2, pady=4)
        return seg
    else:
        entry = ctk.CTkEntry(parent, width=COL_CAT, justify="center")
        entry.pack(side="left", padx=2, pady=4)
        return entry


def _divider(parent):
    ctk.CTkFrame(
        parent, width=1, height=20, corner_radius=0,
        fg_color=("gray70", "gray35"),
    ).pack(side="left", padx=(8, 0))


def _header_label(parent, text, width, anchor="center", padx=(0, 0),
                  final=False, highlight=False, dim=False):
    if highlight:
        color = _EDIT_ACTIVE_COLOR
    elif dim:
        color = ("gray60", "gray50")
    elif final:
        color = _FINAL_COLOR
    else:
        color = ("gray10", "gray90")
    ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=color,
    ).pack(side="left", padx=padx, pady=6)


def _cell(parent, text, width, anchor="center", bold=False, padx=(0, 0),
          final=False, dim=False):
    if dim:
        color = ("gray60", "gray50")
    elif final:
        color = _FINAL_COLOR
    else:
        color = ("gray10", "gray90")
    ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=13, weight="bold" if bold else "normal"),
        text_color=color,
    ).pack(side="left", padx=padx, pady=6)
