import sys
import tkinter
import customtkinter as ctk
from database import course_configs
from i18n import t
import undo_stack
from theme import (
    INK, INK_MUTED, LINE, LINE_HEAVY, PAPER_PANEL, HEADER_BAND, ACCENT_SUBTLE,
)

_SIDEBAR_W = 220


class Screen1Frame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._app = app
        self._selected_config_id: int | None = None
        self._sidebar_btns: dict[int, ctk.CTkButton] = {}

        self._build_top_bar()
        self._build_body()
        self._refresh_sidebar()
        self._bind_shortcuts()

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, fg_color=HEADER_BAND, corner_radius=0)
        bar.pack(fill="x")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkButton(
            inner,
            text="⚙",
            width=48, height=48,
            fg_color="transparent",
            text_color=INK, hover_color=ACCENT_SUBTLE,
            font=ctk.CTkFont(size=32),
            command=self._open_settings_modal,
        ).pack(side="right")

        ctk.CTkLabel(
            inner, text="Notenrechner",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

    # ── Body (sidebar + right content) ────────────────────────────────────────

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        ctk.CTkFrame(
            body, width=1, fg_color=LINE_HEAVY, corner_radius=0
        ).pack(side="left", fill="y")

        right = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self._build_panels_row(right)
        self._build_separator(right)
        self._build_student_list(right)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(
            parent, width=_SIDEBAR_W,
            fg_color=PAPER_PANEL, corner_radius=0,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self._sidebar_scroll = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent", corner_radius=0,
        )
        self._sidebar_scroll.pack(fill="both", expand=True)

        ctk.CTkFrame(
            sidebar, height=1, fg_color=LINE, corner_radius=0
        ).pack(fill="x")

        ctk.CTkButton(
            sidebar,
            text=f"+ {t('new_class')}",
            height=36,
            fg_color="transparent",
            hover_color=ACCENT_SUBTLE,
            text_color=INK,
            font=ctk.CTkFont(size=12),
            command=self._open_new_class_modal,
        ).pack(fill="x", padx=6, pady=6)

    def _refresh_sidebar(self, select_config_id: int | None = None):
        for w in self._sidebar_scroll.winfo_children():
            w.destroy()
        self._sidebar_btns.clear()

        configs = course_configs.get_all_configs()

        if not configs:
            ctk.CTkLabel(
                self._sidebar_scroll,
                text=t("no_class_yet"),
                font=ctk.CTkFont(size=11),
                text_color=INK_MUTED,
                wraplength=_SIDEBAR_W - 24,
            ).pack(padx=12, pady=16)
            self._selected_config_id = None
            self._weight_panel.load_config(None)
            self._events_panel.load_config(None)
            self._student_list.load_config(None)
            return

        # Determine which config to select
        all_ids = {cfg["id"] for cfg in configs}
        target_id = select_config_id or self._selected_config_id
        if target_id not in all_ids:
            target_id = configs[0]["id"]

        for cfg in configs:
            cfg_id = cfg["id"]
            label = f"{cfg['class']} · {cfg['course_name']} · {cfg['school_year_label']}"
            is_sel = cfg_id == target_id

            btn = ctk.CTkButton(
                self._sidebar_scroll,
                text=label,
                anchor="w",
                height=34,
                fg_color=ACCENT_SUBTLE if is_sel else "transparent",
                hover_color=HEADER_BAND,
                text_color=INK,
                font=ctk.CTkFont(size=12, weight="bold" if is_sel else "normal"),
                corner_radius=6,
                command=lambda cid=cfg_id: self._select_config(cid),
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._sidebar_btns[cfg_id] = btn

        self._select_config(target_id)

    def _select_config(self, config_id: int):
        # Update button highlight states
        for cid, btn in self._sidebar_btns.items():
            is_sel = cid == config_id
            btn.configure(
                fg_color=ACCENT_SUBTLE if is_sel else "transparent",
                font=ctk.CTkFont(size=12, weight="bold" if is_sel else "normal"),
            )

        if config_id == self._selected_config_id:
            return

        self._selected_config_id = config_id
        self._weight_panel.load_config(config_id)
        self._events_panel.load_config(config_id)
        self._student_list.load_config(config_id)

    # ── Panels row (weights + events side by side) ────────────────────────────

    def _build_panels_row(self, parent):
        from ui.weight_panel import WeightPanel
        from ui.events_panel import EventsPanel

        row = ctk.CTkFrame(parent, fg_color=PAPER_PANEL, corner_radius=0)
        row.pack(fill="x")

        self._weight_panel = WeightPanel(
            row,
            on_weights_saved=self._on_weights_saved,
            fg_color="transparent",
            corner_radius=0,
        )
        self._weight_panel.pack(side="left", fill="both", expand=True)

        ctk.CTkFrame(
            row, width=1, fg_color=LINE, corner_radius=0
        ).pack(side="left", fill="y")

        self._events_panel = EventsPanel(
            row,
            on_event_deleted=self._on_event_deleted,
            fg_color="transparent",
            corner_radius=0,
        )
        self._events_panel.pack(side="left", fill="both", expand=True)

    def _build_separator(self, parent):
        ctk.CTkFrame(
            parent, height=2, fg_color=LINE_HEAVY, corner_radius=0
        ).pack(fill="x")

    # ── Student list ──────────────────────────────────────────────────────────

    def _build_student_list(self, parent):
        from ui.student_list import StudentListPanel
        self._student_list = StudentListPanel(
            parent,
            on_event_saved=self._on_event_saved,
            fg_color="transparent",
        )
        self._student_list.pack(fill="both", expand=True)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_weights_saved(self):
        self._student_list.refresh()

    def _on_event_saved(self):
        self._events_panel.refresh()

    def _on_event_deleted(self):
        self._student_list.refresh()

    # ── New Class modal ───────────────────────────────────────────────────────

    def _open_new_class_modal(self):
        from ui.new_class_modal import NewClassModal
        modal = NewClassModal(self, on_created=self._on_class_created)
        modal.grab_set()

    def _on_class_created(self, config_id: int, label: str):
        self._refresh_sidebar(select_config_id=config_id)

    # ── Settings modal ────────────────────────────────────────────────────────

    def _open_settings_modal(self):
        from ui.settings_modal import SettingsModal
        SettingsModal(self)

    # ── Keyboard shortcuts ────────────────────────────────────────────────────

    def _bind_shortcuts(self):
        self._app.bind("<Control-z>", self._undo)
        self._app.bind("<Control-y>", self._redo)
        self._app.bind("<Control-Z>", self._redo)
        if sys.platform == "darwin":
            self._app.bind("<Command-z>", self._undo)
            self._app.bind("<Command-Z>", self._redo)

    def _undo(self, _event=None):
        focused = self._app.focus_get()
        if isinstance(focused, tkinter.Entry):
            return
        if undo_stack.undo():
            self._student_list.refresh()
            self._events_panel.refresh()

    def _redo(self, _event=None):
        focused = self._app.focus_get()
        if isinstance(focused, tkinter.Entry):
            return
        if undo_stack.redo():
            self._student_list.refresh()
            self._events_panel.refresh()
