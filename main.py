import customtkinter as ctk
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_NAV = [
    ("Dashboard",         "show_dashboard"),
    ("Schüler",           "show_student_management"),
    ("Kurskonfiguration", "show_course_config"),
    ("Noten eingeben",    "show_grade_entry"),
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        from database.schema import init_db
        init_db()

        self.title("Notenrechner")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self._current_frame = None
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._build_layout()
        self.show_student_management()

    def _build_layout(self):
        self._sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self._sidebar, text="Notenrechner",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(28, 20), padx=16)

        for label, method in _NAV:
            btn = ctk.CTkButton(
                self._sidebar, text=label, anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "gray28"),
                height=36,
                command=getattr(self, method),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._nav_buttons[label] = btn

        self._content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._content.pack(side="left", fill="both", expand=True)

    def _switch(self, frame_cls, nav_label: str, **kwargs):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame_cls(self._content, self, **kwargs)
        self._current_frame.pack(fill="both", expand=True, padx=24, pady=24)
        for label, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=("gray80", "gray32") if label == nav_label else "transparent"
            )

    def _placeholder(self, nav_label: str):
        if self._current_frame is not None:
            self._current_frame.destroy()
        frame = ctk.CTkFrame(self._content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(
            frame,
            text=f"{nav_label}\n(noch nicht implementiert)",
            font=ctk.CTkFont(size=18),
            text_color="gray",
        ).pack(expand=True)
        self._current_frame = frame
        for label, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=("gray80", "gray32") if label == nav_label else "transparent"
            )

    def show_student_management(self):
        from ui.student_management import StudentManagementFrame
        self._switch(StudentManagementFrame, "Schüler")

    def show_dashboard(self):
        self._placeholder("Dashboard")

    def show_course_config(self):
        self._placeholder("Kurskonfiguration")

    def show_grade_entry(self):
        self._placeholder("Noten eingeben")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
