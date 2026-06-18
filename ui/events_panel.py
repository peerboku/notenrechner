import customtkinter as ctk
import undo_stack
from i18n import t
from database.grade_events import get_events_with_category, delete_event
from database.grades import delete_grades_by_event


class EventsPanel(ctk.CTkFrame):
    def __init__(self, parent, on_event_deleted=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._config_id: int | None = None
        self._on_event_deleted = on_event_deleted

        self._build_header()
        self._build_body()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(6, 0))

        ctk.CTkLabel(
            header,
            text=t("hide_events"),
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray60"),
        ).pack(side="left")

        self._count_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        )
        self._count_label.pack(side="left", padx=(6, 0))

    # ── Body (always visible) ─────────────────────────────────────────────────

    def _build_body(self):
        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.pack(fill="x", padx=12, pady=(6, 10))

        self._scroll = ctk.CTkScrollableFrame(
            self._body, height=160, fg_color="transparent",
        )
        self._scroll.pack(fill="x")

    # ── Config loading ────────────────────────────────────────────────────────

    def load_config(self, config_id: int | None):
        self._config_id = config_id
        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        if self._config_id is None:
            self._count_label.configure(text="")
            return

        events = [dict(e) for e in get_events_with_category(self._config_id)]
        count = len(events)
        if count == 0:
            self._count_label.configure(text=t("events_none"))
        elif count == 1:
            self._count_label.configure(text=t("events_one"))
        else:
            self._count_label.configure(text=t("events_many", count=count))

        if not events:
            ctk.CTkLabel(
                self._scroll,
                text=t("no_events"),
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60"),
                anchor="w",
            ).pack(fill="x", pady=4)
            return

        for ev in events:
            self._build_event_row(ev)

    def _build_event_row(self, ev: dict):
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", pady=2)

        parts = [ev["category_name"]]
        if ev.get("date"):
            parts.append(ev["date"])
        if ev.get("note"):
            parts.append(ev["note"])
        label_text = " · ".join(parts)

        ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row,
            text=t("delete"),
            width=80, height=24,
            fg_color="transparent",
            border_width=1,
            font=ctk.CTkFont(size=11),
            text_color=("red4", "red3"),
            border_color=("red4", "red3"),
            hover_color=("misty rose", "gray25"),
            command=lambda eid=ev["id"], lbl=label_text: self._confirm_delete(eid, lbl),
        ).pack(side="right")

    # ── Delete ────────────────────────────────────────────────────────────────

    def _confirm_delete(self, event_id: int, label: str):
        _ConfirmDeleteEventDialog(
            self,
            label=label,
            on_confirm=lambda: self._do_delete(event_id),
        )

    def _do_delete(self, event_id: int):
        delete_grades_by_event(event_id)
        delete_event(event_id)
        undo_stack.clear()
        self.refresh()
        if self._on_event_deleted:
            self._on_event_deleted()


# ── Confirm delete dialog ─────────────────────────────────────────────────────

class _ConfirmDeleteEventDialog(ctk.CTkToplevel):
    def __init__(self, parent, label: str, on_confirm):
        super().__init__(parent)
        self._on_confirm = on_confirm

        self.title(t("delete_event_title"))
        self.geometry("380x210")
        self.resizable(False, False)
        self.grab_set()
        self._build(label)

    def _build(self, label: str):
        ctk.CTkLabel(
            self,
            text=t("delete_event_text"),
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(24, 8), padx=24)

        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            wraplength=330,
        ).pack(padx=24)

        ctk.CTkLabel(
            self,
            text=t("cannot_be_undone"),
            font=ctk.CTkFont(size=11),
            text_color=("red4", "red3"),
        ).pack(pady=(6, 16))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkButton(
            btn_row,
            text=t("cancel"),
            fg_color="transparent",
            border_width=1,
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text=t("delete"),
            fg_color=("red4", "red3"),
            hover_color=("red3", "red2"),
            command=self._confirm,
        ).pack(side="right")

    def _confirm(self):
        self._on_confirm()
        self.destroy()
