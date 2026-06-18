import customtkinter as ctk
from database import course_configs
from database.categories import get_all_categories
from database.weight_presets import (
    get_all_presets, get_preset_weights, add_preset, set_preset_weights,
)
from calculation.validation import validate_weights
from i18n import t


class WeightPanel(ctk.CTkFrame):
    def __init__(self, parent, on_weights_saved=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_id: int | None = None
        self._categories: list = []
        self._entries: list[ctk.CTkEntry] = []
        self._presets: dict[str, int] = {}
        self._expanded = True
        self._on_weights_saved = on_weights_saved

        self._build_header()
        self._build_body()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(6, 0))

        self._toggle_btn = ctk.CTkButton(
            header,
            text=t("hide_weights"),
            width=170, height=24,
            fg_color="transparent",
            border_width=0,
            hover_color=("gray78", "gray28"),
            text_color=("gray45", "gray60"),
            font=ctk.CTkFont(size=11),
            command=self._toggle,
        )
        self._toggle_btn.pack(side="left")

        # Shows the active preset name when the panel is collapsed
        self._preset_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
        )
        # Not packed yet — becomes visible only when the body is hidden

    # ── Collapsible body ──────────────────────────────────────────────────────

    def _build_body(self):
        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.pack(fill="x", padx=12, pady=(6, 10))

        # Preset row
        preset_row = ctk.CTkFrame(self._body, fg_color="transparent")
        preset_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            preset_row, text=t("load_preset"), font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 8))
        self._preset_menu = ctk.CTkOptionMenu(
            preset_row,
            values=[t("no_presets_option")],
            command=self._on_preset_selected,
            width=200,
            font=ctk.CTkFont(size=12),
        )
        self._preset_menu.pack(side="left")

        # Weight fields (rebuilt per config)
        self._fields_frame = ctk.CTkFrame(self._body, fg_color="transparent")
        self._fields_frame.pack(fill="x")

        # Bottom row: sum + buttons
        bottom = ctk.CTkFrame(self._body, fg_color="transparent")
        bottom.pack(fill="x", pady=(12, 0))

        self._sum_label = ctk.CTkLabel(
            bottom, text=t("sum_empty"),
            font=ctk.CTkFont(size=12),
            width=110, anchor="w",
        )
        self._sum_label.pack(side="left", padx=(0, 12))

        self._save_btn = ctk.CTkButton(
            bottom, text=t("save"), width=110, height=30,
            command=self._save, state="disabled",
        )
        self._save_btn.pack(side="left", padx=(0, 8))

        self._save_preset_btn = ctk.CTkButton(
            bottom, text=t("save_as_preset"), width=210, height=30,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont(size=12),
            command=self._open_save_preset_dialog,
        )
        # packed conditionally in _update_validation

    def _toggle(self):
        if self._expanded:
            self._body.pack_forget()
            self._toggle_btn.configure(text=t("show_weights"))
            self._preset_label.pack(side="left", padx=(12, 0))
        else:
            self._body.pack(fill="x", padx=12, pady=(6, 10))
            self._toggle_btn.configure(text=t("hide_weights"))
            self._preset_label.pack_forget()
        self._expanded = not self._expanded

    # ── Config loading ────────────────────────────────────────────────────────

    def load_config(self, config_id: int | None):
        self._config_id = config_id
        self._rebuild_fields()
        self._reload_presets()

    def _rebuild_fields(self):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        self._entries = []

        if self._config_id is None:
            self._update_validation()
            return

        self._categories = get_all_categories()
        weights = course_configs.get_weights(self._config_id)

        for cat in self._categories:
            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row, text=cat["name"], width=110, anchor="w",
                font=ctk.CTkFont(size=13),
            ).pack(side="left")

            entry = ctk.CTkEntry(row, width=80, justify="right", font=ctk.CTkFont(size=13))
            entry.insert(0, _fmt(weights.get(cat["id"], 0.0)))
            entry.pack(side="left")
            entry.bind("<KeyRelease>", lambda _e: (self._update_validation(), self._update_preset_label()))

            ctk.CTkLabel(row, text="%", font=ctk.CTkFont(size=13)).pack(
                side="left", padx=(4, 0)
            )
            self._entries.append(entry)

        self._update_validation()

    def _reload_presets(self):
        presets = get_all_presets()
        self._presets = {p["name"]: p["id"] for p in presets}
        if presets:
            values = [t("choose_preset_option")] + [p["name"] for p in presets]
        else:
            values = [t("no_presets_option")]
        self._preset_menu.configure(values=values)

        # If the current config weights already match a preset, show that preset name.
        # This makes the dropdown reflect the applied preset after a class switch or restart.
        selected = values[0]
        current = self._read_entries()
        if current and presets:
            for p in presets:
                pw = get_preset_weights(p["id"])
                if all(abs(current.get(cid, 0) - pw.get(cid, 0)) < 0.01 for cid in current):
                    selected = p["name"]
                    break
        self._preset_menu.set(selected)
        self._update_preset_label()

    def _update_preset_label(self):
        name = self._preset_menu.get()
        if name in (t("choose_preset_option"), t("no_presets_option"), ""):
            text = t("custom_weights") if self._config_id is not None else ""
        else:
            text = name
        self._preset_label.configure(text=text)

    # ── Preset selection ──────────────────────────────────────────────────────

    def _on_preset_selected(self, name: str):
        preset_id = self._presets.get(name)
        if preset_id is None or not self._entries:
            return
        weights = get_preset_weights(preset_id)
        for entry, cat in zip(self._entries, self._categories):
            entry.delete(0, "end")
            entry.insert(0, _fmt(weights.get(cat["id"], 0.0)))
        self._update_validation()
        self._update_preset_label()

    # ── Live validation ───────────────────────────────────────────────────────

    def _read_entries(self) -> dict[int, float] | None:
        result = {}
        for entry, cat in zip(self._entries, self._categories):
            try:
                result[cat["id"]] = float(entry.get().replace(",", "."))
            except ValueError:
                return None
        return result

    def _update_validation(self):
        weights = self._read_entries()

        if not weights:
            self._sum_label.configure(text=t("sum_empty"), text_color=("gray40", "gray60"))
            self._save_btn.configure(state="disabled")
            self._save_preset_btn.pack_forget()
            return

        total = sum(weights.values())
        valid = validate_weights(weights)
        color = ("green3", "green2") if valid else ("red3", "red2")
        total_str = str(int(total)) if total == int(total) else f"{total:.1f}"
        self._sum_label.configure(text=t("sum_value", total=total_str), text_color=color)
        self._save_btn.configure(state="normal" if valid else "disabled")

        if valid and not self._matches_any_preset(weights):
            if not self._save_preset_btn.winfo_ismapped():
                self._save_preset_btn.pack(side="left")
        else:
            self._save_preset_btn.pack_forget()

    def _matches_any_preset(self, weights: dict[int, float]) -> bool:
        for preset_id in self._presets.values():
            pw = get_preset_weights(preset_id)
            if all(abs(weights.get(cid, 0) - pw.get(cid, 0)) < 0.01 for cid in weights):
                return True
        return False

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        if self._config_id is None:
            return
        weights = self._read_entries()
        if weights is None or not validate_weights(weights):
            return
        course_configs.set_weights(self._config_id, weights)
        self._update_validation()
        if self._on_weights_saved:
            self._on_weights_saved()

    def _open_save_preset_dialog(self):
        weights = self._read_entries()
        if weights is None or not validate_weights(weights):
            return
        SavePresetDialog(self, weights=weights, on_saved=self._on_preset_saved)

    def _on_preset_saved(self):
        self._reload_presets()
        self._update_validation()


# ── Save Preset dialog ────────────────────────────────────────────────────────

class SavePresetDialog(ctk.CTkToplevel):
    def __init__(self, parent, weights: dict[int, float], on_saved):
        super().__init__(parent)
        self._weights = weights
        self._on_saved = on_saved

        self.title(t("save_preset_title"))
        self.geometry("320x190")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text=t("preset_name_label"), font=ctk.CTkFont(size=13)
        ).pack(pady=(24, 8), padx=24, anchor="w")

        self._name_entry = ctk.CTkEntry(self, placeholder_text=t("preset_name_placeholder"))
        self._name_entry.pack(fill="x", padx=24)
        self._name_entry.focus()
        self._name_entry.bind("<Return>", lambda _: self._submit())

        self._error_label = ctk.CTkLabel(self, text="", text_color="red", height=22)
        self._error_label.pack(pady=(4, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(4, 20))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(btn_row, text=t("save"), command=self._submit).pack(side="right")

    def _submit(self):
        name = self._name_entry.get().strip()
        if not name:
            self._error_label.configure(text=t("name_required"))
            return
        preset_id = add_preset(name)
        set_preset_weights(preset_id, self._weights)
        self._on_saved()
        self.destroy()


def _fmt(w: float) -> str:
    return str(int(w)) if w == int(w) else str(w)
