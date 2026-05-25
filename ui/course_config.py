import customtkinter as ctk
from tkinter import messagebox

from database import course_configs, weight_overrides
from database import enrollments as enrollments_db
from database.courses import get_all_courses
from database.school_years import get_all_school_years
from database.connection import get_connection

# (key, German label) — fixed order used everywhere in this file
CATEGORIES = [
    ("exams",    "Schularbeiten"),
    ("oral",     "Mündlich"),
    ("homework", "Hausübungen"),
    ("quizzes",  "Quizzes"),
]


def _fmt(v: float) -> str:
    """Format a weight value without a trailing .0 when it's a whole number."""
    return str(int(v)) if v % 1 == 0 else f"{v:.1f}"


class CourseConfigFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._filter: tuple | None = None       # (course_id, school_year_id, class_)
        self._weight_vars: dict = {}
        self._sum_label: ctk.CTkLabel | None = None
        self._save_btn: ctk.CTkButton | None = None
        self._students_panel: ctk.CTkFrame | None = None
        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self):
        ctk.CTkLabel(
            self, text="Kurskonfiguration",
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

        years   = [r["label"] for r in get_all_school_years()]
        courses = [r["name"]  for r in get_all_courses()]
        classes = enrollments_db.get_distinct_classes()

        def header(col, text):
            ctk.CTkLabel(
                inner, text=text,
                text_color="gray", font=ctk.CTkFont(size=12),
            ).grid(row=0, column=col, sticky="w", padx=(0, 4), pady=(0, 2))

        header(0, "Schuljahr")
        self._year_combo = ctk.CTkComboBox(inner, values=years, width=120)
        self._year_combo.set("")
        self._year_combo.grid(row=1, column=0, padx=(0, 12))

        header(1, "Klasse")
        self._class_combo = ctk.CTkComboBox(inner, values=classes, width=100)
        self._class_combo.set("")
        self._class_combo.grid(row=1, column=1, padx=(0, 12))

        header(2, "Kurs")
        self._course_combo = ctk.CTkComboBox(inner, values=courses, width=220)
        self._course_combo.set("")
        self._course_combo.grid(row=1, column=2, padx=(0, 12))

        ctk.CTkButton(
            inner, text="Laden", width=90,
            command=self._load,
        ).grid(row=1, column=3, padx=(8, 0))

    def _show_placeholder(self):
        for w in self._content.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._content,
            text="Schuljahr, Klasse und Kurs auswählen,\ndann auf Laden klicken.",
            text_color="gray", font=ctk.CTkFont(size=14),
        ).pack(expand=True)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def _load(self):
        year_label  = self._year_combo.get().strip()
        class_      = self._class_combo.get().strip()
        course_name = self._course_combo.get().strip()

        if not year_label or not class_ or not course_name:
            messagebox.showwarning(
                "Fehlende Auswahl",
                "Bitte Schuljahr, Klasse und Kurs angeben.",
            )
            return

        conn = get_connection()
        year_row   = conn.execute("SELECT id FROM school_years WHERE label = ?", (year_label,)).fetchone()
        course_row = conn.execute("SELECT id FROM courses WHERE name = ?", (course_name,)).fetchone()

        if not year_row:
            messagebox.showwarning("Nicht gefunden", f'Schuljahr "{year_label}" nicht gefunden.')
            return
        if not course_row:
            messagebox.showwarning("Nicht gefunden", f'Kurs "{course_name}" nicht gefunden.')
            return

        self._filter = (course_row["id"], year_row["id"], class_)
        self._render_content(course_row["id"], year_row["id"], class_, course_name, year_label)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    def _render_content(
        self,
        course_id: int, school_year_id: int, class_: str,
        course_name: str, year_label: str,
    ):
        for w in self._content.winfo_children():
            w.destroy()

        self._content.columnconfigure(0, weight=1)
        self._content.columnconfigure(1, weight=1)
        self._content.rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self._content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._build_weights_panel(left, course_id, school_year_id, class_, course_name, year_label)

        right = ctk.CTkFrame(self._content)
        right.grid(row=0, column=1, sticky="nsew")
        self._students_panel = right
        self._render_students(course_id, school_year_id, class_)

    # ------------------------------------------------------------------
    # Default weights panel (left)
    # ------------------------------------------------------------------

    def _build_weights_panel(
        self,
        parent,
        course_id: int, school_year_id: int, class_: str,
        course_name: str, year_label: str,
    ):
        ctk.CTkLabel(
            parent, text="Standard-Gewichtung",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(16, 2))

        ctk.CTkLabel(
            parent,
            text=f"{course_name}  ·  Klasse {class_}  ·  {year_label}",
            text_color="gray", font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=16, pady=(0, 14))

        cfg = course_configs.get_config(course_id, school_year_id, class_)
        defaults = {
            "exams":    cfg["weight_exams"]    if cfg else 0.0,
            "oral":     cfg["weight_oral"]     if cfg else 0.0,
            "homework": cfg["weight_homework"] if cfg else 0.0,
            "quizzes":  cfg["weight_quizzes"]  if cfg else 0.0,
        }

        self._weight_vars = {}
        for cat, label in CATEGORIES:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(row, text=label, width=130, anchor="w").pack(side="left")
            var = ctk.StringVar(value=_fmt(defaults[cat]))
            var.trace_add("write", lambda *_: self._update_sum())
            ctk.CTkEntry(row, textvariable=var, width=72, justify="right").pack(side="left", padx=(0, 4))
            ctk.CTkLabel(row, text="%").pack(side="left")
            self._weight_vars[cat] = var

        # Sum row
        sep = ctk.CTkFrame(parent, fg_color="transparent")
        sep.pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(sep, text="Summe:", width=130, anchor="w").pack(side="left")
        self._sum_label = ctk.CTkLabel(sep, text="0 %", width=72, anchor="e")
        self._sum_label.pack(side="left")
        ctk.CTkLabel(sep, text="%").pack(side="left")

        self._save_btn = ctk.CTkButton(
            parent, text="Speichern",
            command=lambda: self._save_config(course_id, school_year_id, class_),
        )
        self._save_btn.pack(padx=16, pady=(10, 20))

        self._update_sum()

    def _update_sum(self):
        if not self._sum_label:
            return
        total = self._weight_total()
        if total is None:
            self._sum_label.configure(text="—", text_color="gray")
            self._save_btn.configure(state="disabled")
        elif abs(total - 100.0) < 0.01:
            self._sum_label.configure(text=_fmt(total), text_color="#4CAF50")
            self._save_btn.configure(state="normal")
        else:
            self._sum_label.configure(text=_fmt(total), text_color="#f44336")
            self._save_btn.configure(state="disabled")

    def _weight_total(self) -> float | None:
        total = 0.0
        for var in self._weight_vars.values():
            try:
                total += float(var.get())
            except ValueError:
                return None
        return total

    def _save_config(self, course_id: int, school_year_id: int, class_: str):
        try:
            w = {cat: float(self._weight_vars[cat].get()) for cat in self._weight_vars}
        except ValueError:
            messagebox.showerror("Fehler", "Bitte nur Zahlen eingeben.")
            return
        course_configs.upsert_config(
            course_id, school_year_id, class_,
            w["exams"], w["oral"], w["homework"], w["quizzes"],
        )
        messagebox.showinfo("Gespeichert", "Standard-Gewichtung wurde gespeichert.")

    # ------------------------------------------------------------------
    # Student overrides panel (right)
    # ------------------------------------------------------------------

    def _render_students(self, course_id: int, school_year_id: int, class_: str):
        for w in self._students_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self._students_panel, text="Individuelle Gewichtungen",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(16, 2))
        ctk.CTkLabel(
            self._students_panel,
            text="Überschreibt die Standard-Gewichtung für einzelne Schüler.",
            text_color="gray", font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=16, pady=(0, 12))

        enrolled = enrollments_db.get_enrollments_by_filter(
            school_year_id=school_year_id,
            class_=class_,
            course_id=course_id,
        )

        scroll = ctk.CTkScrollableFrame(self._students_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        if not enrolled:
            ctk.CTkLabel(
                scroll,
                text="Keine Schüler für diese Kombination eingeschrieben.",
                text_color="gray",
            ).pack(pady=20, anchor="w", padx=8)
            return

        for e in enrolled:
            self._student_row(scroll, e, course_id, school_year_id, class_)

    def _student_row(self, parent, enrollment, course_id: int, school_year_id: int, class_: str):
        ov = weight_overrides.get_override(enrollment["id"])

        row = ctk.CTkFrame(parent, corner_radius=8)
        row.pack(fill="x", pady=3, padx=4)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=10)

        ctk.CTkLabel(
            info, text=enrollment["student_name"],
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(anchor="w")

        if ov:
            detail = (
                f"Schularbeiten {_fmt(ov['weight_exams'])}%  ·  "
                f"Mündlich {_fmt(ov['weight_oral'])}%  ·  "
                f"Hausübungen {_fmt(ov['weight_homework'])}%  ·  "
                f"Quizzes {_fmt(ov['weight_quizzes'])}%"
            )
            detail_color = ("gray30", "gray70")
        else:
            detail = "Standard-Gewichtung"
            detail_color = "gray"

        ctk.CTkLabel(
            info, text=detail,
            text_color=detail_color, font=ctk.CTkFont(size=12), anchor="w",
        ).pack(anchor="w")

        if ov and ov["note"]:
            ctk.CTkLabel(
                info, text=f"Begründung: {ov['note']}",
                text_color="gray", font=ctk.CTkFont(size=11, slant="italic"), anchor="w",
            ).pack(anchor="w")

        btn_row = ctk.CTkFrame(row, fg_color="transparent")
        btn_row.pack(side="right", padx=10, pady=10)

        if ov:
            ctk.CTkButton(
                btn_row, text="Bearbeiten", width=90, height=28,
                command=lambda eid=enrollment["id"]: self._open_override_dialog(
                    eid, course_id, school_year_id, class_
                ),
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                btn_row, text="Zurücksetzen", width=105, height=28,
                fg_color="transparent", border_width=1,
                text_color=("red3", "#ff6b6b"),
                command=lambda eid=enrollment["id"]: self._delete_override(
                    eid, course_id, school_year_id, class_
                ),
            ).pack(side="left")
        else:
            ctk.CTkButton(
                btn_row, text="Überschreiben", width=110, height=28,
                fg_color="transparent", border_width=1,
                command=lambda eid=enrollment["id"]: self._open_override_dialog(
                    eid, course_id, school_year_id, class_
                ),
            ).pack(side="left")

    def _open_override_dialog(
        self, enrollment_id: int,
        course_id: int, school_year_id: int, class_: str,
    ):
        ov = weight_overrides.get_override(enrollment_id)
        initial = (
            {
                "exams":    ov["weight_exams"],
                "oral":     ov["weight_oral"],
                "homework": ov["weight_homework"],
                "quizzes":  ov["weight_quizzes"],
                "note":     ov["note"] or "",
            }
            if ov else None
        )
        dlg = _WeightDialog(self, title="Gewichtung überschreiben", initial=initial)
        self.wait_window(dlg)
        if dlg.result:
            weight_overrides.upsert_override(
                enrollment_id,
                dlg.result["exams"],
                dlg.result["oral"],
                dlg.result["homework"],
                dlg.result["quizzes"],
                dlg.result["note"],
            )
            self._render_students(course_id, school_year_id, class_)

    def _delete_override(
        self, enrollment_id: int,
        course_id: int, school_year_id: int, class_: str,
    ):
        if messagebox.askyesno(
            "Zurücksetzen",
            "Individuelle Gewichtung löschen?\n"
            "Der Schüler verwendet dann wieder die Standard-Gewichtung.",
        ):
            weight_overrides.delete_override(enrollment_id)
            self._render_students(course_id, school_year_id, class_)


# ------------------------------------------------------------------
# Weight entry dialog (reused for default config and overrides)
# ------------------------------------------------------------------

class _WeightDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, initial: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.result: dict | None = None
        self.resizable(False, False)
        self.grab_set()

        if initial is None:
            initial = {cat: 0.0 for cat, _ in CATEGORIES}

        self._vars: dict[str, ctk.StringVar] = {}
        for cat, label in CATEGORIES:
            ctk.CTkLabel(self, text=label).pack(anchor="w", padx=24, pady=(12, 2))
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(padx=24, fill="x")
            var = ctk.StringVar(value=_fmt(initial[cat]))
            var.trace_add("write", lambda *_: self._update_sum())
            ctk.CTkEntry(row, textvariable=var, width=80, justify="right").pack(side="left", padx=(0, 4))
            ctk.CTkLabel(row, text="%").pack(side="left")
            self._vars[cat] = var

        sum_row = ctk.CTkFrame(self, fg_color="transparent")
        sum_row.pack(padx=24, pady=(14, 4), fill="x")
        ctk.CTkLabel(sum_row, text="Summe:", width=100, anchor="w").pack(side="left")
        self._sum_label = ctk.CTkLabel(sum_row, text="0", anchor="w")
        self._sum_label.pack(side="left")
        ctk.CTkLabel(sum_row, text="%").pack(side="left")

        ctk.CTkLabel(
            self, text="Begründung (optional):",
        ).pack(anchor="w", padx=24, pady=(14, 2))
        self._note_entry = ctk.CTkEntry(self, width=280, placeholder_text="z. B. Legasthenie-Ausgleich")
        self._note_entry.pack(padx=24, fill="x")
        if initial.get("note"):
            self._note_entry.insert(0, initial["note"])

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(padx=24, pady=20)
        self._save_btn = ctk.CTkButton(btns, text="Speichern", width=120, command=self._save)
        self._save_btn.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btns, text="Abbrechen", width=120, command=self.destroy,
            fg_color="transparent", border_width=1,
        ).pack(side="left")

        self._update_sum()
        self._center(parent)

    def _update_sum(self):
        total = self._total()
        if total is None:
            self._sum_label.configure(text="—", text_color="gray")
            self._save_btn.configure(state="disabled")
        elif abs(total - 100.0) < 0.01:
            self._sum_label.configure(text=_fmt(total), text_color="#4CAF50")
            self._save_btn.configure(state="normal")
        else:
            self._sum_label.configure(text=_fmt(total), text_color="#f44336")
            self._save_btn.configure(state="disabled")

    def _total(self) -> float | None:
        t = 0.0
        for var in self._vars.values():
            try:
                t += float(var.get())
            except ValueError:
                return None
        return t

    def _save(self):
        try:
            self.result = {cat: float(self._vars[cat].get()) for cat in self._vars}
        except ValueError:
            return
        self.result["note"] = self._note_entry.get().strip()
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
