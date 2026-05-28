import customtkinter as ctk
from database import course_configs, grades as grades_db
from database.categories import get_all_categories
from database.students import add_student
from database.enrollments import add_enrollment, get_enrollments_by_filter
from calculation.grades import category_average, calculate_final_grade

COL_NAME  = 200
COL_CAT   =  90
COL_FINAL =  90

_FINAL_COLOR = ("#1a6fc4", "#5ba4f5")


class StudentListPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_id: int | None = None
        self._config_data = None
        self._active_cats: list = []

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Action bar (Add Event wired up in 5.4)
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=16, pady=(12, 8))

        self._add_event_btn = ctk.CTkButton(
            action_bar, text="Add Event", width=110, state="disabled"
        )
        self._add_event_btn.pack(side="left")

        # Column header
        self._header_frame = ctk.CTkFrame(
            self, fg_color=("gray85", "gray22"), corner_radius=0
        )
        self._header_frame.pack(fill="x", padx=16)

        # Scrollable rows
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        # Add student
        add_row = ctk.CTkFrame(self, fg_color="transparent")
        add_row.pack(fill="x", padx=16, pady=(0, 12))

        self._add_entry = ctk.CTkEntry(
            add_row, placeholder_text="Add student…", width=COL_NAME
        )
        self._add_entry.pack(side="left")
        self._add_entry.bind("<Return>", self._on_add_student)
        self._add_entry.bind("<FocusOut>", lambda _e: self._add_entry.delete(0, "end"))

    # ── Public API ────────────────────────────────────────────────────────────

    def load_config(self, config_id: int | None):
        self._config_id = config_id
        if config_id is None:
            self._config_data = None
            self._active_cats = []
            self._add_event_btn.configure(state="disabled")
        else:
            self._config_data = course_configs.get_config_by_id(config_id)
            self._active_cats = _active_categories(config_id)
            self._add_event_btn.configure(state="normal")

        self._rebuild_header()
        self._rebuild_rows()

    def refresh(self):
        """Reload weights and redraw — call after saving weights."""
        if self._config_id is not None:
            self._active_cats = _active_categories(self._config_id)
            self._rebuild_header()
        self._rebuild_rows()

    # ── Header ────────────────────────────────────────────────────────────────

    def _rebuild_header(self):
        for w in self._header_frame.winfo_children():
            w.destroy()

        _header_label(self._header_frame, "Name", COL_NAME, anchor="w", padx=(8, 0))
        for cat in self._active_cats:
            _header_label(self._header_frame, cat["name"], COL_CAT)
        _divider(self._header_frame)
        _header_label(self._header_frame, "Final", COL_FINAL, final=True)

    # ── Rows ──────────────────────────────────────────────────────────────────

    def _rebuild_rows(self):
        for w in self._scroll.winfo_children():
            w.destroy()

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

    def _build_row(self, enrollment, bg):
        row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=0)
        row.pack(fill="x")

        grades = grades_db.get_grades(enrollment["id"])
        by_cat: dict[int, list[float]] = {}
        for g in grades:
            by_cat.setdefault(g["category_id"], []).append(g["value"])

        _cell(row, enrollment["student_name"], COL_NAME, anchor="w", padx=(8, 0))

        for cat in self._active_cats:
            avg = category_average(by_cat.get(cat["id"], []))
            _cell(row, f"{avg:.1f}" if avg is not None else "—", COL_CAT)

        try:
            final = calculate_final_grade(enrollment["id"])
        except ValueError:
            final = None
        _divider(row)
        _cell(row, str(final) if final is not None else "—", COL_FINAL, bold=True, final=True)


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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _active_categories(config_id: int) -> list:
    weights = course_configs.get_weights(config_id)
    return [c for c in get_all_categories() if weights.get(c["id"], 0) > 0]


def _divider(parent):
    ctk.CTkFrame(
        parent, width=1, height=20, corner_radius=0,
        fg_color=("gray70", "gray35"),
    ).pack(side="left", padx=(8, 0))


def _header_label(parent, text, width, anchor="center", padx=(0, 0), final=False):
    ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=_FINAL_COLOR if final else ("gray10", "gray90"),
    ).pack(side="left", padx=padx, pady=6)


def _cell(parent, text, width, anchor="center", bold=False, padx=(0, 0), final=False):
    ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=13, weight="bold" if bold else "normal"),
        text_color=_FINAL_COLOR if final else ("gray10", "gray90"),
    ).pack(side="left", padx=padx, pady=6)
