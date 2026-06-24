import customtkinter as ctk
from i18n import t
from database.weight_presets import get_all_presets, rename_preset, delete_preset
from theme import INK, INK_MUTED, ACCENT_SUBTLE, DANGER, DANGER_HOVER


class SettingsModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("settings"))
        self.geometry("400x360")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=t("settings"), font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(24, 16), padx=24, anchor="w")

        # ── Preset management ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text=t("weight_presets"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(0, 8))

        self._preset_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=220
        )
        self._preset_frame.pack(fill="x", padx=24, pady=(0, 8))

        self._refresh_presets()

    # ── Preset management ──────────────────────────────────────────────────────

    def _refresh_presets(self):
        for w in self._preset_frame.winfo_children():
            w.destroy()

        presets = get_all_presets()
        if not presets:
            ctk.CTkLabel(
                self._preset_frame,
                text=t("no_presets_hint"),
                text_color=INK_MUTED,
                font=ctk.CTkFont(size=13),
            ).pack(pady=10, anchor="w")
            return

        for preset in presets:
            self._build_preset_row(dict(preset))

    def _build_preset_row(self, preset: dict):
        row = ctk.CTkFrame(self._preset_frame, fg_color="transparent")
        row.pack(fill="x", pady=3)

        ctk.CTkLabel(
            row, text=preset["name"],
            font=ctk.CTkFont(size=13), anchor="w",
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            row, text=t("rename"), width=100, height=26,
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            font=ctk.CTkFont(size=11),
            command=lambda p=preset: _RenameDialog(self, p, self._refresh_presets),
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            row, text=t("delete"), width=80, height=26,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont(size=11),
            text_color=DANGER,
            border_color=DANGER,
            command=lambda p=preset: _ConfirmDeleteDialog(self, p, self._refresh_presets),
        ).pack(side="right")


# ── Rename preset dialog ──────────────────────────────────────────────────────

class _RenameDialog(ctk.CTkToplevel):
    def __init__(self, parent, preset: dict, on_renamed):
        super().__init__(parent)
        self._preset = preset
        self._on_renamed = on_renamed
        self.title(t("rename_preset_title"))
        self.geometry("320x180")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=t("new_name_label"), font=ctk.CTkFont(size=13)
        ).pack(pady=(24, 6), padx=24, anchor="w")

        self._entry = ctk.CTkEntry(self)
        self._entry.pack(fill="x", padx=24)
        self._entry.insert(0, self._preset["name"])
        self._entry._entry.select_range(0, "end")
        self._entry.focus()
        self._entry.bind("<Return>", lambda _: self._submit())

        self._error = ctk.CTkLabel(self, text="", text_color=DANGER, height=20)
        self._error.pack(pady=(4, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(btn_row, text=t("rename"), command=self._submit).pack(side="right")

    def _submit(self):
        name = self._entry.get().strip()
        if not name:
            self._error.configure(text=t("name_required"))
            return
        rename_preset(self._preset["id"], name)
        self._on_renamed()
        self.destroy()


# ── Confirm delete dialog ─────────────────────────────────────────────────────

class _ConfirmDeleteDialog(ctk.CTkToplevel):
    def __init__(self, parent, preset: dict, on_deleted):
        super().__init__(parent)
        self._preset = preset
        self._on_deleted = on_deleted
        self.title(t("delete_preset_title"))
        self.geometry("340x165")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text=t("delete_preset_text", name=self._preset["name"]),
            font=ctk.CTkFont(size=13),
            justify="center",
        ).pack(pady=(30, 20), padx=24)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text=t("delete"),
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            command=self._confirm,
        ).pack(side="right")

    def _confirm(self):
        delete_preset(self._preset["id"])
        self._on_deleted()
        self.destroy()
