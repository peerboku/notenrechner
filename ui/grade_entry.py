import customtkinter as ctk
from tkinter import messagebox
from datetime import date as _date

from database import grades as grades_db
from database import enrollments as enrollments_db
from database.students import get_all_students
from calculation.grades import category_average
from calculation.validation import validate_grade_value

CATEGORIES = [
    ("exams",    "Schularbeiten"),
    ("oral",     "Mündlich"),
    ("homework", "Hausübungen"),
    ("quizzes",  "Quizzes"),
]

RESTRICTED = {"homework", "quizzes"}


def _to_display(iso: str) -> str:
    """YYYY-MM-DD → DD.MM.YYYY"""
    try:
        y, m, d = iso.split("-")
        return f"{d}.{m}.{y}"
    except Exception:
        return iso


def _to_iso(s: str) -> str:
    """DD.MM.YYYY → YYYY-MM-DD, raises ValueError on bad input."""
    from datetime import datetime
    return datetime.strptime(s.strip(), "%d.%m.%Y").strftime("%Y-%m-%d")


def _fmt_avg(v: float) -> str:
    return "Ø " + f"{v:.2f}".rstrip("0").rstrip(".")


class GradeEntryFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._enrollment_id: int | None = None
        self._enrollment_rows: list = []
        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self):
        ctk.CTkLabel(
            self, text="Noten eingeben",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", pady=(0, 16))

        self._build_filter_bar()

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True)
        self._show_placeholder()

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(self)
        bar.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(padx=16, pady=12)

        def header(col, text):
            ctk.CTkLabel(
                inner, text=text,
                text_color="gray", font=ctk.CTkFont(size=12),
            ).grid(row=0, column=col, sticky="w", padx=(0, 4), pady=(0, 2))

        header(0, "Schüler")
        students = get_all_students()
        self._student_map = {s["name"]: s["id"] for s in students}
        self._student_combo = ctk.CTkComboBox(
            inner,
            values=list(self._student_map.keys()),
            width=220,
            command=self._on_student_change,
        )
        self._student_combo.set("")
        self._student_combo.grid(row=1, column=0, padx=(0, 12))

        header(1, "Einschreibung")
        self._enrollment_combo = ctk.CTkComboBox(
            inner, values=[], width=340,
            command=self._on_enrollment_change,
        )
        self._enrollment_combo.set("")
        self._enrollment_combo.grid(row=1, column=1)

    # ------------------------------------------------------------------
    # Filter callbacks
    # ------------------------------------------------------------------

    def _on_student_change(self, name: str):
        sid = self._student_map.get(name)
        if sid is None:
            return
        rows = enrollments_db.get_enrollments_by_student(sid)
        self._enrollment_rows = rows
        labels = [
            f"{r['course_name']}  –  Klasse {r['class']}  –  {r['school_year_label']}"
            for r in rows
        ]
        self._enrollment_combo.configure(values=labels)
        if labels:
            self._enrollment_combo.set(labels[0])
            self._on_enrollment_change(labels[0])
        else:
            self._enrollment_combo.set("")
            self._enrollment_id = None
            self._show_placeholder()

    def _on_enrollment_change(self, label: str):
        labels = [
            f"{r['course_name']}  –  Klasse {r['class']}  –  {r['school_year_label']}"
            for r in self._enrollment_rows
        ]
        try:
            idx = labels.index(label)
        except ValueError:
            return
        self._enrollment_id = self._enrollment_rows[idx]["id"]
        self._render_grades()

    def _show_placeholder(self):
        for w in self._content.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._content,
            text="Schüler und Einschreibung auswählen.",
            text_color="gray", font=ctk.CTkFont(size=14),
        ).pack(expand=True)

    # ------------------------------------------------------------------
    # 2×2 category grid
    # ------------------------------------------------------------------

    def _render_grades(self):
        for w in self._content.winfo_children():
            w.destroy()

        self._content.columnconfigure(0, weight=1)
        self._content.columnconfigure(1, weight=1)
        self._content.rowconfigure(0, weight=1)
        self._content.rowconfigure(1, weight=1)

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (r, c), (cat, lbl) in zip(positions, CATEGORIES):
            panel = ctk.CTkFrame(self._content)
            px = (0, 6) if c == 0 else (6, 0)
            py = (0, 6) if r == 0 else (6, 0)
            panel.grid(row=r, column=c, sticky="nsew", padx=px, pady=py)
            panel.rowconfigure(1, weight=1)
            panel.columnconfigure(0, weight=1)
            self._build_panel(panel, cat, lbl)

    def _build_panel(self, panel: ctk.CTkFrame, category: str, label: str):
        eid = self._enrollment_id

        # Header
        hdr = ctk.CTkFrame(panel, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 4))
        hdr.columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr, text=label,
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w")
        avg_lbl = ctk.CTkLabel(hdr, text="", font=ctk.CTkFont(size=13), anchor="e")
        avg_lbl.grid(row=0, column=1, sticky="e", padx=(8, 0))

        # Grade list
        list_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=4)

        # Add button
        ctk.CTkButton(
            panel, text="+ Hinzufügen", height=30,
            fg_color="transparent", border_width=1,
            command=lambda: self._add_grade(eid, category, label, refresh),
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(6, 14))

        def refresh():
            self._rebuild_list(list_frame, avg_lbl, eid, category, label, refresh)

        refresh()

    def _rebuild_list(
        self, list_frame, avg_lbl,
        enrollment_id: int, category: str, label: str,
        refresh_fn=None,
    ):
        for w in list_frame.winfo_children():
            w.destroy()

        rows = grades_db.get_grades(enrollment_id, category)
        avg = category_average([r["value"] for r in rows])

        if avg is None:
            avg_lbl.configure(text="Keine Noten", text_color="gray")
            ctk.CTkLabel(
                list_frame,
                text="Noch keine Noten eingetragen.",
                text_color="gray", font=ctk.CTkFont(size=12),
            ).pack(pady=12, padx=8, anchor="w")
        else:
            color = "#4CAF50" if avg <= 4.0 else "#f44336"
            avg_lbl.configure(text=_fmt_avg(avg), text_color=color)

        for g in rows:
            self._grade_row(list_frame, g, enrollment_id, category, label, refresh_fn)

    def _grade_row(self, parent, grade, enrollment_id: int, category: str, label: str, refresh_fn=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=1)

        v = grade["value"]
        v_text = str(int(v)) if v % 1 == 0 else str(v)

        ctk.CTkLabel(
            row, text=_to_display(grade["date"]),
            font=ctk.CTkFont(size=12), text_color="gray",
            width=88, anchor="w",
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            row, text=v_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=28, anchor="center",
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            row, text="✎", width=26, height=26,
            fg_color="transparent", hover_color=("gray74", "gray26"),
            command=lambda gid=grade["id"], gv=grade["value"], gd=grade["date"]:
                self._edit_grade(gid, gv, gd, enrollment_id, category, label),
        ).pack(side="right", padx=(0, 2))

        ctk.CTkButton(
            row, text="✕", width=26, height=26,
            fg_color="transparent", hover_color=("gray74", "gray26"),
            text_color=("red3", "#ff6b6b"),
            command=lambda gid=grade["id"]: self._delete_grade(gid),
        ).pack(side="right", padx=(0, 2))

    # ------------------------------------------------------------------
    # Grade actions — re-render full grid after each change
    # ------------------------------------------------------------------

    def _add_grade(self, enrollment_id: int, category: str, label: str, refresh_fn):
        dlg = _GradeDialog(self, title=f"Note hinzufügen – {label}", category=category)
        self.wait_window(dlg)
        if dlg.result:
            grades_db.add_grade(enrollment_id, category, dlg.result["value"], dlg.result["date"])
            refresh_fn()

    def _edit_grade(
        self, grade_id: int, current_value: float, current_date: str,
        enrollment_id: int, category: str, label: str,
    ):
        dlg = _GradeDialog(
            self,
            title=f"Note bearbeiten – {label}",
            category=category,
            initial_value=current_value,
            initial_date=current_date,
        )
        self.wait_window(dlg)
        if dlg.result:
            grades_db.update_grade(grade_id, dlg.result["value"], dlg.result["date"])
            self._render_grades()   # rebuild all panels so averages update

    def _delete_grade(self, grade_id: int):
        if messagebox.askyesno("Note löschen", "Diese Note wirklich löschen?", icon="warning"):
            grades_db.delete_grade(grade_id)
            self._render_grades()


# ------------------------------------------------------------------
# Grade input dialog
# ------------------------------------------------------------------

class _GradeDialog(ctk.CTkToplevel):
    def __init__(
        self, parent, title: str, category: str,
        initial_value: float | None = None,
        initial_date: str | None = None,
    ):
        super().__init__(parent)
        self.title(title)
        self.result: dict | None = None
        self.resizable(False, False)
        self.grab_set()

        self._category = category
        self._restricted = category in RESTRICTED

        # Date
        ctk.CTkLabel(self, text="Datum (TT.MM.JJJJ):").pack(
            anchor="w", padx=24, pady=(20, 2)
        )
        self._date_entry = ctk.CTkEntry(self, width=220)
        self._date_entry.pack(anchor="w", padx=24)
        default = _to_display(initial_date) if initial_date else _date.today().strftime("%d.%m.%Y")
        self._date_entry.insert(0, default)

        # Value
        hint = "1, 3 oder 5" if self._restricted else "1 – 5"
        ctk.CTkLabel(self, text=f"Note ({hint}):").pack(
            anchor="w", padx=24, pady=(14, 2)
        )

        if self._restricted:
            self._seg = ctk.CTkSegmentedButton(self, values=["1", "3", "5"], width=220)
            self._seg.pack(anchor="w", padx=24)
            self._seg.set(str(int(initial_value)) if initial_value is not None else "1")
            self._value_entry = None
        else:
            self._value_entry = ctk.CTkEntry(self, width=220, placeholder_text="z. B. 2")
            self._value_entry.pack(anchor="w", padx=24)
            if initial_value is not None:
                v = str(int(initial_value)) if initial_value % 1 == 0 else str(initial_value)
                self._value_entry.insert(0, v)
            self._seg = None

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(padx=24, pady=20)
        ctk.CTkButton(btns, text="Speichern", width=120, command=self._save).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(
            btns, text="Abbrechen", width=120, command=self.destroy,
            fg_color="transparent", border_width=1,
        ).pack(side="left")

        self._center(parent)

    def _save(self):
        # Validate date
        try:
            iso_date = _to_iso(self._date_entry.get())
        except ValueError:
            messagebox.showwarning(
                "Ungültiges Datum",
                "Bitte das Datum im Format TT.MM.JJJJ eingeben.\nBeispiel: 15.01.2025",
                parent=self,
            )
            return

        # Validate value
        if self._restricted:
            value = float(self._seg.get())
        else:
            raw = self._value_entry.get().strip().replace(",", ".")
            try:
                value = float(raw)
            except ValueError:
                messagebox.showwarning(
                    "Ungültige Note",
                    "Bitte eine Zahl zwischen 1 und 5 eingeben.",
                    parent=self,
                )
                return

        if not validate_grade_value(value, self._category):
            messagebox.showwarning(
                "Ungültige Note",
                "Bitte eine Note zwischen 1 und 5 eingeben."
                if not self._restricted
                else "Nur 1, 3 oder 5 sind für diese Kategorie erlaubt.",
                parent=self,
            )
            return

        self.result = {"value": value, "date": iso_date}
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
