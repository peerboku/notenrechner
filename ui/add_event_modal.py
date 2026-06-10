import customtkinter as ctk


class AddEventModal(ctk.CTkToplevel):
    def __init__(self, parent, categories: list, on_confirmed):
        super().__init__(parent)
        self._categories = categories
        self._on_confirmed = on_confirmed

        self.title("Enter Grades")
        self.geometry("400x300")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="Enter Grades", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(24, 16))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28)
        form.columnconfigure(1, weight=1)

        # Category — required
        ctk.CTkLabel(form, text="Category", anchor="w").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        cat_names = [c["name"] for c in self._categories]
        self._cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")
        ctk.CTkOptionMenu(
            form, variable=self._cat_var, values=cat_names
        ).grid(row=0, column=1, sticky="ew", pady=6)

        # Date — optional
        ctk.CTkLabel(form, text="Date", anchor="w").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        self._date_entry = ctk.CTkEntry(
            form, placeholder_text="e.g. 28.05.2026  (optional)"
        )
        self._date_entry.grid(row=1, column=1, sticky="ew", pady=6)

        # Note — optional
        ctk.CTkLabel(form, text="Note", anchor="w").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        self._note_entry = ctk.CTkEntry(form, placeholder_text="optional")
        self._note_entry.grid(row=2, column=1, sticky="ew", pady=6)

        self._error_label = ctk.CTkLabel(self, text="", text_color="red", height=20)
        self._error_label.pack(pady=(8, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(4, 24))
        ctk.CTkButton(
            btn_row, text="Cancel",
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(btn_row, text="Start", command=self._submit).pack(side="right")

    def _submit(self):
        cat_name = self._cat_var.get()
        cat = next((c for c in self._categories if c["name"] == cat_name), None)
        if cat is None:
            self._error_label.configure(text="Please select a category.")
            return
        date = self._date_entry.get().strip() or None
        note = self._note_entry.get().strip() or None
        self._on_confirmed(cat, date, note)
        self.destroy()
