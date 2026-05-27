import customtkinter as ctk
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        from database.schema import init_db
        init_db()

        self.title("Notenrechner")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self._show_screen1()

    def _show_screen1(self):
        from ui.screen1 import Screen1Frame
        frame = Screen1Frame(self, self)
        frame.pack(fill="both", expand=True)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
