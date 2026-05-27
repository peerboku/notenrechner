import customtkinter as ctk
from database import course_configs
from database.courses import get_or_create_course
from database.school_years import get_or_create_school_year


class NewClassModal(ctk.CTkToplevel):
    def __init__(self, parent, on_created):
        super().__init__(parent)
        self._on_created = on_created

        self.title("New Class")
        self.geometry("400x300")
        self.resizable(False, False)
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="New Class", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(24, 16))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28)
        form.columnconfigure(1, weight=1)

        fields = [
            ("Class",       "e.g. 4B",      "_class_entry"),
            ("Course",      "e.g. English", "_course_entry"),
            ("School Year", "e.g. 2025/26", "_year_entry"),
        ]
        for row_idx, (label, placeholder, attr) in enumerate(fields):
            ctk.CTkLabel(form, text=label, anchor="w").grid(
                row=row_idx, column=0, sticky="w", pady=6, padx=(0, 12)
            )
            entry = ctk.CTkEntry(form, placeholder_text=placeholder)
            entry.grid(row=row_idx, column=1, sticky="ew", pady=6)
            setattr(self, attr, entry)

        self._error_label = ctk.CTkLabel(self, text="", text_color="red", height=22)
        self._error_label.pack(pady=(8, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(4, 24))

        ctk.CTkButton(
            btn_row, text="Cancel",
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text="Create",
            command=self._submit,
        ).pack(side="right")

        self._class_entry.focus()

    def _submit(self):
        class_label = self._class_entry.get().strip()
        course_name  = self._course_entry.get().strip()
        year_label   = self._year_entry.get().strip()

        if not class_label:
            self._error_label.configure(text="Class label is required.")
            return
        if not course_name:
            self._error_label.configure(text="Course is required.")
            return
        if not year_label:
            self._error_label.configure(text="School year is required.")
            return

        course_id = get_or_create_course(course_name)
        year_id   = get_or_create_school_year(year_label)
        config_id = course_configs.upsert_config(course_id, year_id, class_label)

        label = f"{class_label} · {course_name} · {year_label}"
        self._on_created(config_id, label)
        self.destroy()
