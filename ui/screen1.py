import sys
import tkinter
import customtkinter as ctk
from database import course_configs
from i18n import t
import undo_stack


class Screen1Frame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._app = app
        self._selected_config_id: int | None = None
        self._config_map: dict[str, int] = {}

        self._build_top_bar()
        self._build_panels_row()
        self._build_separator()
        self._build_student_list()
        self._refresh_class_selector()
        self._bind_shortcuts()

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, fg_color=("gray88", "gray17"), corner_radius=0)
        bar.pack(fill="x")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        # Right-side buttons — packed right-to-left, so gear ends up rightmost
        ctk.CTkButton(
            inner,
            text="⚙",
            width=48, height=48,
            fg_color="transparent",
            font=ctk.CTkFont(size=32),
            command=self._open_settings_modal,
        ).pack(side="right")

        ctk.CTkLabel(inner, text=t("class_label"), font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 8)
        )

        self._class_var = ctk.StringVar(value=t("no_class_yet"))
        self._class_menu = ctk.CTkComboBox(
            inner,
            variable=self._class_var,
            values=[t("no_class_yet")],
            command=self._on_class_selected,
            width=300,
            font=ctk.CTkFont(size=13),
        )
        self._class_menu.pack(side="left")

        ctk.CTkButton(
            inner,
            text=t("new_class"),
            width=110,
            command=self._open_new_class_modal,
        ).pack(side="left", padx=(12, 0))

    # ── Panels row (weights + events side by side) ────────────────────────────

    def _build_panels_row(self):
        from ui.weight_panel import WeightPanel
        from ui.events_panel import EventsPanel

        row = ctk.CTkFrame(self, fg_color=("gray86", "gray18"), corner_radius=0)
        row.pack(fill="x")

        self._weight_panel = WeightPanel(
            row,
            on_weights_saved=self._on_weights_saved,
            fg_color="transparent",
            corner_radius=0,
        )
        self._weight_panel.pack(side="left", fill="both", expand=True)

        ctk.CTkFrame(
            row, width=1, fg_color=("gray75", "gray30"), corner_radius=0
        ).pack(side="left", fill="y")

        self._events_panel = EventsPanel(
            row,
            on_event_deleted=self._on_event_deleted,
            fg_color="transparent",
            corner_radius=0,
        )
        self._events_panel.pack(side="left", fill="both", expand=True)

    def _build_separator(self):
        ctk.CTkFrame(
            self, height=2, fg_color=("gray65", "gray35"), corner_radius=0
        ).pack(fill="x")

    # ── Student list ──────────────────────────────────────────────────────────

    def _build_student_list(self):
        from ui.student_list import StudentListPanel
        self._student_list = StudentListPanel(
            self,
            on_event_saved=self._on_event_saved,
            fg_color="transparent",
        )
        self._student_list.pack(fill="both", expand=True)

    # ── Class selector ────────────────────────────────────────────────────────

    def _refresh_class_selector(self, select_label: str | None = None):
        configs = course_configs.get_all_configs()
        self._config_map = {}

        if not configs:
            self._class_menu.configure(values=[t("no_class_yet")])
            self._class_var.set(t("no_class_yet"))
            self._selected_config_id = None
            self._weight_panel.load_config(None)
            self._events_panel.load_config(None)
            self._student_list.load_config(None)
            return

        labels = []
        for cfg in configs:
            label = f"{cfg['class']} · {cfg['course_name']} · {cfg['school_year_label']}"
            labels.append(label)
            self._config_map[label] = cfg["id"]

        self._class_menu.configure(values=labels)
        target = select_label if select_label in self._config_map else labels[0]
        self._class_var.set(target)
        self._on_class_selected(target)

    def _on_class_selected(self, label: str):
        config_id = self._config_map.get(label)
        if config_id is None:
            return
        self._selected_config_id = config_id
        self._weight_panel.load_config(config_id)
        self._events_panel.load_config(config_id)
        self._student_list.load_config(config_id)

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
        self._refresh_class_selector(select_label=label)

    # ── Settings modal ────────────────────────────────────────────────────────

    def _open_settings_modal(self):
        from ui.settings_modal import SettingsModal
        SettingsModal(self)

    # ── Keyboard shortcuts ────────────────────────────────────────────────────

    def _bind_shortcuts(self):
        self._app.bind("<Control-z>", self._undo)
        self._app.bind("<Control-y>", self._redo)
        self._app.bind("<Control-Z>", self._redo)   # Ctrl+Shift+Z
        if sys.platform == "darwin":
            self._app.bind("<Command-z>", self._undo)
            self._app.bind("<Command-Z>", self._redo)  # Cmd+Shift+Z

    def _undo(self, _event=None):
        # Don't intercept when a text entry owns focus (let it handle its own undo)
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
