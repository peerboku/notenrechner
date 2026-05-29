import customtkinter as ctk
from database import course_configs


class Screen1Frame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self._app = app
        self._selected_config_id: int | None = None
        self._config_map: dict[str, int] = {}

        self._build_top_bar()
        self._build_weight_panel()
        self._build_separator()
        self._build_student_list()
        self._refresh_class_selector()

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, fg_color=("gray88", "gray17"), corner_radius=0)
        bar.pack(fill="x")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        # Gear icon — packed right first so it claims its space before left items fill in
        ctk.CTkButton(
            inner,
            text="⚙",
            width=48, height=48,
            fg_color="transparent",
            font=ctk.CTkFont(size=32),
            command=self._open_settings_modal,
        ).pack(side="right")

        ctk.CTkLabel(inner, text="Class:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(0, 8)
        )

        self._class_var = ctk.StringVar(value="— no class yet —")
        self._class_menu = ctk.CTkComboBox(
            inner,
            variable=self._class_var,
            values=["— no class yet —"],
            command=self._on_class_selected,
            width=300,
            font=ctk.CTkFont(size=13),
        )
        self._class_menu.pack(side="left")

        ctk.CTkButton(
            inner,
            text="New Class",
            width=110,
            command=self._open_new_class_modal,
        ).pack(side="left", padx=(12, 0))

    # ── Weight panel ──────────────────────────────────────────────────────────

    def _build_weight_panel(self):
        from ui.weight_panel import WeightPanel
        self._weight_panel = WeightPanel(
            self,
            on_weights_saved=self._on_weights_saved,
            fg_color=("gray92", "gray20"),
            corner_radius=0,
        )
        self._weight_panel.pack(fill="x")

    def _build_separator(self):
        ctk.CTkFrame(
            self, height=1, fg_color=("gray75", "gray30"), corner_radius=0
        ).pack(fill="x")

    # ── Student list ──────────────────────────────────────────────────────────

    def _build_student_list(self):
        from ui.student_list import StudentListPanel
        self._student_list = StudentListPanel(self, fg_color="transparent")
        self._student_list.pack(fill="both", expand=True)

    # ── Class selector ────────────────────────────────────────────────────────

    def _refresh_class_selector(self, select_label: str | None = None):
        configs = course_configs.get_all_configs()
        self._config_map = {}

        if not configs:
            self._class_menu.configure(values=["— no class yet —"])
            self._class_var.set("— no class yet —")
            self._selected_config_id = None
            self._weight_panel.load_config(None)
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
        self._student_list.load_config(config_id)

    def _on_weights_saved(self):
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
