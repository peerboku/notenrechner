import tkinter as tk
from tkinter import ttk, messagebox
import os
import json


class MainMenu(tk.Frame):
    def __init__(self, parent: tk.Tk, app) -> None:
        super().__init__(parent)
        self.app = app
        self._subjects: list = []
        self._build()

    def _build(self) -> None:
        header = tk.Frame(self, pady=30)
        header.pack(fill=tk.X)
        tk.Label(header, text="Menü",
                 font=("Helvetica", 28, "bold")).pack()
        tk.Label(header, text="Karteikarten für die Prüfungsvorbereitung",
                 font=("Helvetica", 12), fg="#aaaaaa").pack()

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=40)

        self._subjects = self._scan_subjects()

        if not self._subjects:
            tk.Label(
                self,
                text="Kein Fach gefunden. Bitte .json-Datei in data/ anlegen.",
                font=("Helvetica", 13), fg="#aaaaaa",
            ).pack(pady=50)
            return

        # Subject listbox
        sel = tk.Frame(self, pady=20)
        sel.pack()
        tk.Label(sel, text="Fach auswählen:",
                 font=("Helvetica", 13)).grid(row=0, column=0, padx=10, sticky=tk.NE, pady=4)

        lb_frame = tk.Frame(sel)
        lb_frame.grid(row=0, column=1, padx=10)

        self._listbox = tk.Listbox(
            lb_frame, selectmode=tk.EXTENDED,
            font=("Helvetica", 12), width=34,
            height=min(len(self._subjects), 6),
            activestyle="none", cursor="hand2",
        )
        self._listbox.pack(side=tk.LEFT)
        sb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL, command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=sb.set)
        if len(self._subjects) > 6:
            sb.pack(side=tk.LEFT, fill=tk.Y)

        for s in self._subjects:
            self._listbox.insert(tk.END, s)

        # Restore previous selection
        if self.app.last_subjects:
            for i, s in enumerate(self._subjects):
                if s in self.app.last_subjects:
                    self._listbox.selection_set(i)
        else:
            self._listbox.selection_set(0)

        tk.Label(sel, text="Strg/Cmd+Klick für mehrere Fächer",
                 fg="#aaaaaa", font=("Helvetica", 9)).grid(
            row=1, column=1, sticky=tk.W, padx=10)

        # Buttons
        btn_area = tk.Frame(self)
        btn_area.pack(pady=10)
        _btn = dict(width=26, font=("Helvetica", 13), pady=6, relief=tk.FLAT, cursor="hand2")
        tk.Button(btn_area, text="▶   Abfrage starten",
                  bg="#4CAF50", activebackground="#45a049",
                  command=self._start_quiz, **_btn).pack(pady=8)
        tk.Button(btn_area, text="✎   Fragen verwalten",
                  bg="#2196F3", activebackground="#1976D2",
                  command=self._open_editor, **_btn).pack(pady=8)
        tk.Button(btn_area, text="📊   Statistik",
                  bg="#9C27B0", activebackground="#7B1FA2",
                  command=self._open_statistik, **_btn).pack(pady=8)

        tk.Button(self, text="Fächerliste neu laden", font=("Helvetica", 9),
                  fg="#aaaaaa", relief=tk.FLAT, cursor="hand2",
                  command=lambda: self.app.show_main_menu()).pack(pady=(20, 0))

    def _scan_subjects(self) -> list:
        try:
            return sorted(f[:-5] for f in os.listdir(self.app.data_dir)
                          if f.endswith(".json"))
        except OSError:
            return []

    def _selected_subjects(self) -> list:
        return [self._subjects[i] for i in self._listbox.curselection()]

    def _save_selection(self) -> None:
        self.app.last_subjects = self._selected_subjects()

    def _start_quiz(self) -> None:
        selected = self._selected_subjects()
        if not selected:
            messagebox.showwarning("Kein Fach", "Bitte mindestens ein Fach auswählen.")
            return
        self._save_selection()
        paths = {s: os.path.join(self.app.data_dir, s + ".json") for s in selected}
        FilterDialog(self, paths, self.app)

    def _open_editor(self) -> None:
        selected = self._selected_subjects()
        if len(selected) != 1:
            messagebox.showwarning("Einzelnes Fach",
                                   "Bitte genau ein Fach für 'Fragen verwalten' auswählen.")
            return
        self._save_selection()
        self.app.show_editor(os.path.join(self.app.data_dir, selected[0] + ".json"))

    def _open_statistik(self) -> None:
        selected = self._selected_subjects()
        if len(selected) != 1:
            messagebox.showwarning("Einzelnes Fach",
                                   "Bitte genau ein Fach für 'Statistik' auswählen.")
            return
        self._save_selection()
        self.app.show_statistik(os.path.join(self.app.data_dir, selected[0] + ".json"))


class FilterDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, paths: dict, app) -> None:
        super().__init__(parent)
        self.paths = paths   # {subject_name: file_path}
        self.app = app
        self.title("Abfrage starten")
        self.resizable(False, False)
        self.grab_set()
        self._filter_var = tk.StringVar(value="alle")
        self._all_questions: list = []
        self._path_map: dict = {}
        self._tag_listbox: tk.Listbox | None = None
        self._load_questions()
        self._build()
        self.update_idletasks()
        x = parent.winfo_rootx() + 180
        y = parent.winfo_rooty() + 140
        self.geometry(f"+{x}+{y}")

    def _load_questions(self) -> None:
        for subject, path in self.paths.items():
            try:
                with open(path, encoding="utf-8") as fh:
                    qs = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue
            for q in qs:
                self._path_map[q["id"]] = path
            self._all_questions.extend(qs)

    def _build(self) -> None:
        subjects_label = ", ".join(self.paths.keys())
        tk.Label(self, text=f"Fach: {subjects_label}",
                 font=("Helvetica", 11), fg="#aaaaaa").pack(padx=24, pady=(14, 2))
        tk.Label(self, text="Welche Fragen sollen abgefragt werden?",
                 font=("Helvetica", 13, "bold")).pack(padx=24, pady=(0, 8))

        for label, value in (
            ("Alle Fragen", "alle"),
            ("Nur falsch beantwortet (letzter Versuch falsch)", "falsch"),
            ("Noch nie geübt", "neu"),
        ):
            tk.Radiobutton(self, text=label, variable=self._filter_var, value=value,
                           font=("Helvetica", 12)).pack(anchor=tk.W, padx=36, pady=4)

        # Tag filter
        all_tags = sorted({t for q in self._all_questions for t in q.get("tags", [])})
        if all_tags:
            tk.Frame(self, height=1, bg="#444").pack(fill=tk.X, padx=20, pady=(12, 4))
            tk.Label(self, text="Nach Tags filtern (optional):",
                     font=("Helvetica", 11, "bold")).pack(anchor=tk.W, padx=24)
            tk.Label(self, text="Kein Tag gewählt = alle Tags",
                     fg="#aaaaaa", font=("Helvetica", 9)).pack(anchor=tk.W, padx=24)

            lb_frame = tk.Frame(self)
            lb_frame.pack(fill=tk.X, padx=24, pady=(4, 0))
            self._tag_listbox = tk.Listbox(
                lb_frame, selectmode=tk.EXTENDED,
                font=("Helvetica", 11),
                height=min(len(all_tags), 5),
                activestyle="none",
            )
            self._tag_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if len(all_tags) > 5:
                tsb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL,
                                    command=self._tag_listbox.yview)
                self._tag_listbox.configure(yscrollcommand=tsb.set)
                tsb.pack(side=tk.LEFT, fill=tk.Y)
            for tag in all_tags:
                self._tag_listbox.insert(tk.END, tag)

        tk.Frame(self, height=1, bg="#444").pack(fill=tk.X, padx=20, pady=(12, 0))

        btn_row = tk.Frame(self, pady=12)
        btn_row.pack()
        tk.Button(btn_row, text="Starten", width=14, bg="#4CAF50",
                  font=("Helvetica", 12), command=self._launch).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_row, text="Abbrechen", width=14, font=("Helvetica", 12),
                  command=self.destroy).pack(side=tk.LEFT, padx=8)

    def _launch(self) -> None:
        questions = list(self._all_questions)

        f = self._filter_var.get()
        if f == "falsch":
            questions = [q for q in questions
                         if q.get("historie") and not q["historie"][-1]["richtig"]]
        elif f == "neu":
            questions = [q for q in questions if not q.get("historie")]

        # Tag filter
        if self._tag_listbox is not None:
            sel_indices = self._tag_listbox.curselection()
            if sel_indices:
                selected_tags = {self._tag_listbox.get(i) for i in sel_indices}
                questions = [q for q in questions
                             if selected_tags & set(q.get("tags", []))]

        if not questions:
            messagebox.showinfo("Keine Fragen",
                                "Für den gewählten Filter wurden keine Fragen gefunden.")
            return

        self.destroy()
        self.app.show_quiz(questions, self._path_map)
