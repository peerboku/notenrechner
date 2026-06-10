import customtkinter as ctk
from i18n import t


class AddEventModal(ctk.CTkToplevel):
    def __init__(self, parent, categories: list, on_confirmed):
        super().__init__(parent)
        self._categories = categories
        self._on_confirmed = on_confirmed

        self.title(t("enter_grades"))
        self.geometry("400x300")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=t("enter_grades"), font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(24, 16))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28)
        form.columnconfigure(1, weight=1)

        # Category — required
        ctk.CTkLabel(form, text=t("category"), anchor="w").grid(
            row=0, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        cat_names = [c["name"] for c in self._categories]
        self._cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")
        ctk.CTkOptionMenu(
            form, variable=self._cat_var, values=cat_names
        ).grid(row=0, column=1, sticky="ew", pady=6)

        # Date — optional
        ctk.CTkLabel(form, text=t("date"), anchor="w").grid(
            row=1, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        self._date_entry = ctk.CTkEntry(
            form, placeholder_text=t("date_placeholder")
        )
        self._date_entry.grid(row=1, column=1, sticky="ew", pady=6)

        # Note — optional
        ctk.CTkLabel(form, text=t("note"), anchor="w").grid(
            row=2, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        self._note_entry = ctk.CTkEntry(form, placeholder_text=t("optional"))
        self._note_entry.grid(row=2, column=1, sticky="ew", pady=6)

        self._error_label = ctk.CTkLabel(self, text="", text_color="red", height=20)
        self._error_label.pack(pady=(8, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(4, 24))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(btn_row, text=t("start"), command=self._submit).pack(side="right")

    def _submit(self):
        cat_name = self._cat_var.get()
        cat = next((c for c in self._categories if c["name"] == cat_name), None)
        if cat is None:
            self._error_label.configure(text=t("select_category"))
            return
        date = self._date_entry.get().strip() or None
        note = self._note_entry.get().strip() or None
        self._on_confirmed(cat, date, note)
        self.destroy()
