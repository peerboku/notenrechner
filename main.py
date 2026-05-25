import tkinter as tk
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, BASE_DIR)

class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Notenrechner")
        self.root.minsize(800, 600)
        self.root.geometry("1050x720")
        os.makedirs(DATA_DIR, exist_ok=True)
        self.data_dir = DATA_DIR
        self.last_subjects: list = []
        self._current_frame: tk.Frame | None = None
        self.show_main_menu()

    def _switch(self, frame_cls, **kwargs) -> None:
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame_cls(self.root, self, **kwargs)
        self._current_frame.pack(fill=tk.BOTH, expand=True)

    def show_main_menu(self) -> None:
        from ui.main_menu import MainMenu
        self._switch(MainMenu)

def main() -> None:
    root = tk.Tk()
    root.option_add("*foreground", "#e8e8e8")
    root.option_add("*background", "#1e1e1e")
    root.option_add("*Button.foreground", "#1a1a1a")
    root.option_add("*Text.foreground", "#1a1a1a")
    root.option_add("*Entry.foreground", "#1a1a1a")
    root.option_add("*Entry.insertBackground", "#1a1a1a")
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()