import customtkinter as ctk
from tkinter import messagebox

from database import students as students_db
from database import enrollments as enrollments_db
from database.courses import get_all_courses, get_or_create_course
from database.school_years import get_all_school_years, get_or_create_school_year


class StudentManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._selected_student_id: int | None = None
        self._build()
        self._refresh_student_list()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self):
        ctk.CTkLabel(
            self, text="Schülerverwaltung",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", pady=(0, 16))

        panels = ctk.CTkFrame(self, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=0, minsize=260)
        panels.columnconfigure(1, weight=1)
        panels.rowconfigure(0, weight=1)

        # Left panel
        left = ctk.CTkFrame(panels)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        lh = ctk.CTkFrame(left, fg_color="transparent")
        lh.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(
            lh, text="Schüler", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(
            lh, text="+ Neu", width=72, height=28,
            command=self._add_student_dialog,
        ).pack(side="right")

        self._student_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self._student_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))

        # Right panel
        self._right = ctk.CTkFrame(panels)
        self._right.grid(row=0, column=1, sticky="nsew")
        self._show_no_selection()

    # ------------------------------------------------------------------
    # Student list
    # ------------------------------------------------------------------

    def _refresh_student_list(self):
        for w in self._student_scroll.winfo_children():
            w.destroy()

        students = students_db.get_all_students()
        if not students:
            ctk.CTkLabel(
                self._student_scroll,
                text="Noch keine Schüler angelegt.",
                text_color="gray",
            ).pack(pady=16, padx=8, anchor="w")
            return

        for s in students:
            selected = s["id"] == self._selected_student_id
            row = ctk.CTkFrame(
                self._student_scroll,
                fg_color=("gray78", "gray30") if selected else "transparent",
                corner_radius=6,
            )
            row.pack(fill="x", pady=2)

            ctk.CTkButton(
                row, text=s["name"], anchor="w",
                fg_color="transparent",
                hover_color=("gray74", "gray26"),
                text_color=("gray10", "gray90"),
                command=lambda sid=s["id"]: self._select_student(sid),
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))

            ctk.CTkButton(
                row, text="✎", width=28, height=28,
                fg_color="transparent", hover_color=("gray74", "gray26"),
                command=lambda sid=s["id"], n=s["name"]: self._edit_student_dialog(sid, n),
            ).pack(side="right", padx=(0, 2))

            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color="transparent", hover_color=("gray74", "gray26"),
                text_color=("red3", "#ff6b6b"),
                command=lambda sid=s["id"], n=s["name"]: self._delete_student(sid, n),
            ).pack(side="right", padx=(0, 2))

    def _select_student(self, student_id: int):
        self._selected_student_id = student_id
        self._refresh_student_list()
        self._load_enrollments(student_id)

    # ------------------------------------------------------------------
    # Enrollment panel
    # ------------------------------------------------------------------

    def _show_no_selection(self):
        for w in self._right.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._right,
            text="← Schüler auswählen",
            text_color="gray",
            font=ctk.CTkFont(size=14),
        ).pack(expand=True)

    def _load_enrollments(self, student_id: int):
        for w in self._right.winfo_children():
            w.destroy()

        student = students_db.get_student_by_id(student_id)
        if student is None:
            self._show_no_selection()
            return

        # Header
        header = ctk.CTkFrame(self._right, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 4))
        ctk.CTkLabel(
            header, text=student["name"],
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header, text="+ Einschreibung", width=148, height=30,
            command=lambda: self._add_enrollment_dialog(student_id),
        ).pack(side="right")

        ctk.CTkLabel(
            self._right, text="Einschreibungen",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(self._right, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        enrollments = enrollments_db.get_enrollments_by_student(student_id)
        if not enrollments:
            ctk.CTkLabel(
                scroll,
                text="Noch keine Einschreibungen.",
                text_color="gray",
            ).pack(pady=20, anchor="w", padx=8)
        else:
            for e in enrollments:
                self._enrollment_row(scroll, e)

    def _enrollment_row(self, parent, enrollment):
        row = ctk.CTkFrame(parent, corner_radius=8)
        row.pack(fill="x", pady=4, padx=4)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=10)

        ctk.CTkLabel(
            info, text=enrollment["course_name"],
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info,
            text=f"Klasse {enrollment['class']}  ·  {enrollment['school_year_label']}",
            text_color="gray", font=ctk.CTkFont(size=12), anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            row, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=("gray74", "gray26"),
            text_color=("red3", "#ff6b6b"),
            command=lambda eid=enrollment["id"]: self._delete_enrollment(eid),
        ).pack(side="right", padx=10, pady=10)

    # ------------------------------------------------------------------
    # Student dialogs
    # ------------------------------------------------------------------

    def _add_student_dialog(self):
        dlg = _TextDialog(self, title="Schüler hinzufügen", prompt="Name:")
        self.wait_window(dlg)
        if dlg.result:
            students_db.add_student(dlg.result)
            self._refresh_student_list()

    def _edit_student_dialog(self, student_id: int, current_name: str):
        dlg = _TextDialog(self, title="Name ändern", prompt="Name:", initial=current_name)
        self.wait_window(dlg)
        if dlg.result and dlg.result != current_name:
            students_db.update_student(student_id, dlg.result)
            self._refresh_student_list()
            if self._selected_student_id == student_id:
                self._load_enrollments(student_id)

    def _delete_student(self, student_id: int, name: str):
        if not messagebox.askyesno(
            "Schüler löschen",
            f'Schüler "{name}" wirklich löschen?\n'
            "Alle Einschreibungen und Noten werden ebenfalls gelöscht.",
            icon="warning",
        ):
            return
        try:
            students_db.delete_student(student_id)
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc))
            return
        if self._selected_student_id == student_id:
            self._selected_student_id = None
            self._show_no_selection()
        self._refresh_student_list()

    # ------------------------------------------------------------------
    # Enrollment dialogs
    # ------------------------------------------------------------------

    def _add_enrollment_dialog(self, student_id: int):
        courses = [r["name"] for r in get_all_courses()]
        years = [r["label"] for r in get_all_school_years()]
        dlg = _EnrollmentDialog(self, courses=courses, years=years)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        course_name, class_, year_label = dlg.result
        try:
            cid = get_or_create_course(course_name)
            yid = get_or_create_school_year(year_label)
            enrollments_db.add_enrollment(student_id, cid, yid, class_)
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc))
            return
        self._load_enrollments(student_id)

    def _delete_enrollment(self, enrollment_id: int):
        if not messagebox.askyesno(
            "Einschreibung löschen",
            "Einschreibung wirklich löschen?\n"
            "Alle zugehörigen Noten werden ebenfalls gelöscht.",
            icon="warning",
        ):
            return
        try:
            enrollments_db.delete_enrollment(enrollment_id)
        except Exception as exc:
            messagebox.showerror("Fehler", str(exc))
            return
        if self._selected_student_id is not None:
            self._load_enrollments(self._selected_student_id)


# ------------------------------------------------------------------
# Reusable dialogs
# ------------------------------------------------------------------

class _TextDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, prompt: str, initial: str = ""):
        super().__init__(parent)
        self.title(title)
        self.result: str | None = None
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text=prompt).pack(anchor="w", padx=24, pady=(20, 4))
        self._entry = ctk.CTkEntry(self, width=300)
        self._entry.pack(padx=24)
        self._entry.insert(0, initial)
        self._entry.focus()
        self._entry.bind("<Return>", lambda _e: self._save())

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
        val = self._entry.get().strip()
        if not val:
            return
        self.result = val
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class _EnrollmentDialog(ctk.CTkToplevel):
    def __init__(self, parent, courses: list[str], years: list[str]):
        super().__init__(parent)
        self.title("Einschreibung hinzufügen")
        self.result: tuple | None = None
        self.resizable(False, False)
        self.grab_set()

        def row(label: str):
            ctk.CTkLabel(self, text=label).pack(anchor="w", padx=24, pady=(12, 2))

        row("Kurs:")
        self._course = ctk.CTkComboBox(self, values=courses, width=320)
        self._course.set("")
        self._course.pack(padx=24)

        row("Klasse (z. B. 4B):")
        self._class = ctk.CTkEntry(self, width=320)
        self._class.pack(padx=24)

        row("Schuljahr (z. B. 2024/25):")
        self._year = ctk.CTkComboBox(self, values=years, width=320)
        self._year.set("")
        self._year.pack(padx=24)

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
        course = self._course.get().strip()
        class_ = self._class.get().strip()
        year = self._year.get().strip()
        if not course or not class_ or not year:
            messagebox.showwarning(
                "Fehlende Angaben", "Bitte alle Felder ausfüllen.", parent=self
            )
            return
        self.result = (course, class_, year)
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
