import tkinter
import customtkinter as ctk
from datetime import date as _date
from database import course_configs, grades as grades_db
from database.categories import get_all_categories
from database.students import add_student
from database.enrollments import add_enrollment, delete_enrollment, get_enrollments_by_filter
from database.grade_events import add_event, get_event as _get_event
from calculation.grades import category_average, calculate_final_grade
from calculation.grade_input import parse_grade_input, format_grade
from i18n import t
import undo_stack
from undo_actions import AddEventAction

COL_NAME  = 200
COL_CAT   = 115   # wide enough for the longest default name ("Schularbeiten")
COL_FINAL =  90
COL_NOTIZ = 130   # note column in the detail strip
COL_DATUM = COL_NAME - COL_NOTIZ   # date column in the detail strip (= 70)

from theme import (
    INK, INK_MUTED,
    LINE as _GRID_LINE,         # thin rule between cells and rows
    LINE_HEAVY as _GRID_HEAVY,  # outer border + header/final rules
    HEADER_BAND as _HEADER_BG,  # column-header band
    PAPER_ROW as _ROW_BG,       # flat row "paper" (no zebra striping)
    DETAIL_BG as _DETAIL_BG,    # expanded detail strip
    ACCENT as _FINAL_COLOR,     # navy — the Endnote column
    ACCENT_SUBTLE,
    EDIT_ACTIVE as _EDIT_ACTIVE_COLOR,
    DANGER, DANGER_HOVER,
)


class StudentListPanel(ctk.CTkFrame):
    def __init__(self, parent, on_view_grades=None, on_event_saved=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_view_grades = on_view_grades
        self._on_event_saved = on_event_saved
        self._config_id: int | None = None
        self._config_data = None
        self._active_cats: list = []

        # Edit-mode state
        self._edit_mode = False
        self._edit_cat: dict | None = None
        self._edit_inputs: list[tuple[int, object]] = []
        self._date_entry: ctk.CTkEntry | None = None
        self._note_entry: ctk.CTkEntry | None = None

        # Expand/collapse state
        self._expanded_eid: int | None = None

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Action bar (contents swapped between normal / edit mode)
        self._action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self._action_bar.pack(fill="x", padx=16, pady=(12, 8))
        self._set_action_bar_normal()

        # Ruled table (gradebook look): one bordered box holding header + rows
        self._table = ctk.CTkFrame(
            self, fg_color=_ROW_BG, corner_radius=0,
            border_width=1, border_color=_GRID_HEAVY,
        )
        self._table.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        # Column-header band, closed by a heavy rule
        self._header_frame = ctk.CTkFrame(self._table, fg_color=_HEADER_BG, corner_radius=0)
        self._header_frame.pack(fill="x")
        ctk.CTkFrame(self._table, height=2, fg_color=_GRID_HEAVY, corner_radius=0).pack(fill="x")

        # Scrollable rows (the ruled paper)
        self._scroll = ctk.CTkScrollableFrame(self._table, fg_color=_ROW_BG, corner_radius=0)
        self._scroll.pack(fill="both", expand=True)

        # Bottom save bar (hidden until edit mode)
        self._bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        # Not packed yet
        ctk.CTkButton(
            self._bottom_bar, text=t("cancel"),
            width=100, fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self._cancel_edit,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            self._bottom_bar, text=t("save"), width=100,
            command=self._save_event,
        ).pack(side="right")

        # Add student (saved as self._add_row so edit mode can reorder it).
        # Shows a button by default; clicking it swaps in the name entry.
        self._add_row = ctk.CTkFrame(self, fg_color="transparent")
        self._add_row.pack(fill="x", padx=16, pady=(0, 12))
        self._add_btn = ctk.CTkButton(
            self._add_row, text=t("add_student"), width=COL_NAME,
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            state="disabled",
            command=self._show_add_entry,
        )
        self._add_btn.pack(side="left")
        self._add_entry = ctk.CTkEntry(
            self._add_row, placeholder_text=t("student_name_placeholder"), width=COL_NAME
        )
        # Not packed until the button is clicked
        self._add_entry.bind("<Return>", self._on_add_student)
        self._add_entry.bind("<Escape>", lambda _e: self._show_add_button())
        self._add_entry.bind("<FocusOut>", self._on_add_entry_focus_out)

    def _show_add_entry(self):
        self._add_btn.pack_forget()
        self._add_entry.pack(side="left")
        self._add_entry.focus_set()

    def _show_add_button(self):
        self._add_entry.delete(0, "end")
        self._add_entry.pack_forget()
        self._add_btn.pack(side="left")

    def _on_add_entry_focus_out(self, _event=None):
        if not self._add_entry.get().strip():
            self._show_add_button()

    # ── Action bar states ─────────────────────────────────────────────────────

    def _set_action_bar_normal(self):
        for w in self._action_bar.winfo_children():
            w.destroy()
        self._date_entry = None
        self._note_entry = None
        if self._config_id is not None:
            ctk.CTkLabel(
                self._action_bar,
                text=t("header_click_hint"),
                font=ctk.CTkFont(size=12),
                text_color=INK_MUTED,
            ).pack(side="left")

    def _set_action_bar_edit(self):
        for w in self._action_bar.winfo_children():
            w.destroy()

        # Left side: category name + date + note + notation hint
        left = ctk.CTkFrame(self._action_bar, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left,
            text=t("editing", name=self._edit_cat["name"]),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=_EDIT_ACTIVE_COLOR,
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            left, text=t("date_label"),
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=(0, 4))
        self._date_entry = ctk.CTkEntry(left, width=110, font=ctk.CTkFont(size=12))
        self._date_entry.insert(0, _date.today().strftime("%d.%m.%Y"))
        self._date_entry.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            left, text=t("note_label"),
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=(0, 4))
        self._note_entry = ctk.CTkEntry(
            left, width=160, font=ctk.CTkFont(size=12),
            placeholder_text=t("optional"),
        )
        self._note_entry.pack(side="left", padx=(0, 16))

        if self._edit_cat["input_type"] == "continuous":
            ctk.CTkLabel(
                left,
                text=t("notation_hint_short"),
                font=ctk.CTkFont(size=11),
                text_color=INK_MUTED,
            ).pack(side="left")

        # Right side: cancel + save
        ctk.CTkButton(
            self._action_bar, text=t("cancel"),
            width=100, fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self._cancel_edit,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            self._action_bar, text=t("save"), width=100,
            command=self._save_event,
        ).pack(side="right")

    # ── Public API ────────────────────────────────────────────────────────────

    def load_config(self, config_id: int | None):
        if self._edit_mode:
            self._exit_edit_mode()
        undo_stack.clear()
        self._config_id = config_id
        if config_id is None:
            self._config_data = None
            self._active_cats = []
        else:
            self._config_data = course_configs.get_config_by_id(config_id)
            self._active_cats = _active_categories(config_id)
        self._add_btn.configure(state="normal" if config_id is not None else "disabled")
        self._set_action_bar_normal()
        self._rebuild_header()
        self._rebuild_rows()

    def refresh(self):
        if self._config_id is not None:
            self._active_cats = _active_categories(self._config_id)
            self._rebuild_header()
        self._rebuild_rows()

    # ── Edit mode ─────────────────────────────────────────────────────────────

    def _enter_edit_mode(self, cat: dict):
        self._edit_mode = True
        self._edit_cat = dict(cat)
        self._edit_inputs = []
        self._set_action_bar_edit()
        self._show_add_button()
        self._add_btn.configure(state="disabled")
        self._rebuild_header()
        self._rebuild_rows()
        # Insert bottom bar between scroll and add_row (avoid after=/before= — CTkScrollableFrame
        # delegates pack() to an internal _parent_frame, so self._scroll isn't in the pack manager)
        self._add_row.pack_forget()
        self._bottom_bar.pack(fill="x", padx=16, pady=(0, 4))
        self._add_row.pack(fill="x", padx=16, pady=(0, 12))

    def _exit_edit_mode(self):
        self._edit_mode = False
        self._edit_cat = None
        self._edit_event_data = None
        self._edit_inputs = []
        self._set_action_bar_normal()
        self._bottom_bar.pack_forget()
        if self._config_id is not None:
            self._add_btn.configure(state="normal")
        self._rebuild_header()
        self._rebuild_rows()

    def _cancel_edit(self):
        self._exit_edit_mode()

    # ── Save event ────────────────────────────────────────────────────────────

    def _save_event(self):
        if not self._edit_cat:
            return

        label_to_value: dict[str, float] = {}
        if self._edit_cat["input_type"] == "discrete" and self._edit_cat["discrete_values"]:
            label_to_value = {
                label: float(value)
                for label, value in _discrete_pairs(self._edit_cat)
            }

        entries: list[tuple[int, float | None]] = []
        blank_count = 0

        for enrollment_id, widget in self._edit_inputs:
            if isinstance(widget, ctk.CTkSegmentedButton):
                value = label_to_value.get(widget.get())
            else:
                value = parse_grade_input(widget.get())
            entries.append((enrollment_id, value))
            if value is None:
                blank_count += 1

        if blank_count > 0:
            _ConfirmSaveDialog(
                self, blank_count=blank_count,
                on_confirmed=lambda: self._do_save(entries),
            )
        else:
            self._do_save(entries)

    def _do_save(self, entries: list[tuple[int, float | None]]):
        cat_id = self._edit_cat["id"]
        date   = self._date_entry.get().strip() or None if self._date_entry else None
        note   = self._note_entry.get().strip() or None if self._note_entry else None

        event_id = add_event(
            course_config_id=self._config_id,
            category_id=cat_id,
            date=date,
            note=note,
        )
        grade_snapshots = []
        for enrollment_id, value in entries:
            if value is not None:
                grades_db.add_grade(
                    enrollment_id=enrollment_id,
                    category_id=cat_id,
                    value=value,
                    date=date,
                    event_id=event_id,
                )
                grade_snapshots.append({
                    "enrollment_id": enrollment_id,
                    "category_id": cat_id,
                    "value": value,
                    "date": date,
                })

        undo_stack.push(AddEventAction(
            event_id=event_id,
            event_snapshot={
                "course_config_id": self._config_id,
                "category_id": cat_id,
                "date": date,
                "note": note,
            },
            grade_snapshots=grade_snapshots,
        ))
        self._exit_edit_mode()
        if self._on_event_saved:
            self._on_event_saved()

    # ── Header ────────────────────────────────────────────────────────────────

    def _rebuild_header(self):
        for w in self._header_frame.winfo_children():
            w.destroy()

        _header_label(self._header_frame, t("name_column"), COL_NAME, anchor="w", padx=(8, 0))
        for cat in self._active_cats:
            active = self._edit_mode and self._edit_cat and cat["id"] == self._edit_cat["id"]
            dim    = self._edit_mode and not active
            _vline(self._header_frame)
            if not self._edit_mode:
                _header_cat_button(
                    self._header_frame, cat,
                    command=lambda c=dict(cat): self._enter_edit_mode(c),
                )
            else:
                _header_label(self._header_frame, cat["name"], COL_CAT,
                              highlight=active, dim=dim)
        _vline(self._header_frame, _GRID_HEAVY)
        _header_label(self._header_frame, t("final_column"), COL_FINAL, final=True)

    # ── Rows ──────────────────────────────────────────────────────────────────

    def _rebuild_rows(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._edit_inputs = []

        if self._config_data is None:
            return

        enrollments = get_enrollments_by_filter(
            school_year_id=self._config_data["school_year_id"],
            class_=self._config_data["class"],
            course_id=self._config_data["course_id"],
        )

        if not enrollments:
            empty = ctk.CTkFrame(self._scroll, fg_color="transparent")
            empty.pack(pady=40)
            ctk.CTkLabel(
                empty,
                text=t("no_students"),
                text_color=INK_MUTED,
                font=ctk.CTkFont(size=14),
            ).pack()
            if not self._edit_mode:
                ctk.CTkButton(
                    empty, text=t("add_student"), width=180, height=36,
                    command=self._show_add_entry,
                ).pack(pady=(14, 0))
            return

        for enrollment in enrollments:
            self._build_row(enrollment, _ROW_BG)

        if self._edit_mode:
            self._wire_navigation()

    def _build_row(self, enrollment, bg):
        eid = enrollment["id"]
        is_expanded = (eid == self._expanded_eid) and not self._edit_mode

        grades = grades_db.get_grades(eid)
        by_cat: dict[int, list[float]] = {}
        for g in grades:
            by_cat.setdefault(g["category_id"], []).append(g["value"])

        row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=0)
        row.pack(fill="x")

        # Name cell — click toggles the detail strip
        name_lbl = ctk.CTkLabel(
            row, text=enrollment["student_name"], width=COL_NAME, anchor="w",
            font=ctk.CTkFont(size=13), text_color=INK,
            cursor="hand2" if not self._edit_mode else "",
        )
        name_lbl.pack(side="left", padx=(8, 0), pady=6)
        if not self._edit_mode:
            name_lbl._label.bind("<Button-1>", lambda _e, i=eid: self._toggle_detail(i))

        for cat in self._active_cats:
            cat = dict(cat)
            active = self._edit_mode and self._edit_cat and cat["id"] == self._edit_cat["id"]
            dim    = self._edit_mode and not active

            _vline(row)
            if active:
                widget = _input_widget(row, cat)
                self._edit_inputs.append((eid, widget))
            else:
                avg = category_average(by_cat.get(cat["id"], []))
                _cell(row, f"{avg:.1f}" if avg is not None else "—", COL_CAT, dim=dim)

        _vline(row, _GRID_HEAVY)

        try:
            final = calculate_final_grade(eid)
        except ValueError:
            final = None
        _cell(row, str(final) if final is not None else "—", COL_FINAL,
              bold=True, final=True)

        # ⋯ action menu button — far right, only in normal mode
        if not self._edit_mode:
            menu_btn = ctk.CTkButton(
                row, text="⋯", width=28, height=28,
                fg_color="transparent",
                hover_color=ACCENT_SUBTLE,
                font=ctk.CTkFont(size=15),
                text_color=INK_MUTED,
            )
            menu_btn.configure(
                command=lambda b=menu_btn: self._show_action_menu(eid, b)
            )
            menu_btn.pack(side="right", padx=(0, 4))

        if is_expanded:
            self._build_detail_strip(grades, _DETAIL_BG)

        # Horizontal rule closing this row block (below any detail strip)
        ctk.CTkFrame(
            self._scroll, height=1, fg_color=_GRID_LINE, corner_radius=0
        ).pack(fill="x")

    def _toggle_detail(self, eid: int):
        self._expanded_eid = None if self._expanded_eid == eid else eid
        self._rebuild_rows()

    def _show_action_menu(self, enrollment_id: int, btn):
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu = tkinter.Menu(self, tearoff=0)
        if self._on_view_grades:
            menu.add_command(
                label=t("view_grades"),
                command=lambda: self._on_view_grades(enrollment_id),
            )
            menu.add_separator()
        menu.add_command(
            label=t("remove"),
            foreground=DANGER[0],
            command=lambda: _ConfirmRemoveDialog(
                self, enrollment_id, on_confirmed=self._rebuild_rows,
            ),
        )
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _build_detail_strip(self, grades, strip_bg):
        strip = ctk.CTkFrame(self._scroll, fg_color=strip_bg, corner_radius=0)
        strip.pack(fill="x")

        if not grades:
            return

        active_cats = [dict(c) for c in self._active_cats]
        vtl_maps: dict[int, dict[float, str]] = {}
        for cat in active_cats:
            if cat["input_type"] == "discrete" and cat["discrete_values"]:
                vtl_maps[cat["id"]] = {float(v): lbl for lbl, v in _discrete_pairs(cat)}

        # Load event info (note + date) for grades that belong to an event
        event_cache: dict[int, dict] = {}
        for g in grades:
            ev_id = g["event_id"]
            if ev_id and ev_id not in event_cache:
                ev = _get_event(ev_id)
                event_cache[ev_id] = dict(ev) if ev else {}

        # Build one candidate row per event (or per individual grade).
        # Grades from the same event share one row; individual grades each get one.
        candidates: list[dict] = []
        seen_keys: dict = {}
        for g in grades:
            ev_id = g["event_id"]
            ev = event_cache.get(ev_id, {}) if ev_id else {}
            eff_date = ev.get("date") or g["date"] or ""
            note = ev.get("note") or g["note"] or ""
            row_key = ev_id if ev_id else f"ind_{g['id']}"

            if row_key not in seen_keys:
                row = {"date": eff_date, "note": "", "by_cat": {}}
                seen_keys[row_key] = row
                candidates.append(row)

            grp = seen_keys[row_key]
            if note and not grp["note"]:
                grp["note"] = note
            cat_id = g["category_id"]
            vtl = vtl_maps.get(cat_id)
            raw = float(g["value"])
            grp["by_cat"][cat_id] = vtl[raw] if vtl and raw in vtl else format_grade(raw)

        # Merge candidate rows that share the same date and don't conflict on any category.
        # Keeps the nice "all categories for one date in one row" view while still
        # showing separate rows when the same category appears twice on the same date.
        candidates.sort(key=lambda r: _date_sort_key(r["date"]), reverse=True)
        rows: list[dict] = []
        for cand in candidates:
            merged = False
            for existing in rows:
                if existing["date"] == cand["date"]:
                    if not any(cid in existing["by_cat"] for cid in cand["by_cat"]):
                        existing["by_cat"].update(cand["by_cat"])
                        if not existing["note"] and cand["note"]:
                            existing["note"] = cand["note"]
                        merged = True
                        break
            if not merged:
                rows.append(dict(cand))

        muted_c  = INK_MUTED
        normal_c = INK
        header_c = INK_MUTED

        # Header sub-row (Notiz | Datum | category names) — columns aligned with
        # the main table so the grid lines line up under their headers
        _detail_subrow(
            strip,
            t("note_label").rstrip(":"), t("date_label").rstrip(":"),
            {c["id"]: c["name"] for c in active_cats}, active_cats,
            note_color=header_c, date_color=header_c,
            cat_color_fn=lambda _cid, _v: header_c,
        )
        ctk.CTkFrame(strip, height=1, fg_color=_GRID_LINE, corner_radius=0).pack(fill="x")

        for ri, row_data in enumerate(rows):
            if ri > 0:
                ctk.CTkFrame(
                    strip, height=1, fg_color=_GRID_LINE, corner_radius=0,
                ).pack(fill="x")

            note_text = row_data["note"]
            date_display = _short_date(row_data["date"]) if row_data["date"] else "—"
            vals = {c["id"]: row_data["by_cat"].get(c["id"], "") for c in active_cats}
            _detail_subrow(
                strip, note_text, date_display, vals, active_cats,
                note_color=normal_c if note_text else muted_c,
                date_color=muted_c,
                cat_color_fn=lambda _cid, v: normal_c if v else muted_c,
            )

    def _wire_navigation(self):
        """Bind Return on continuous entries to focus the next student's input."""
        continuous = [
            (eid, w) for eid, w in self._edit_inputs
            if isinstance(w, ctk.CTkEntry)
        ]
        for i, (_, entry) in enumerate(continuous):
            if i + 1 < len(continuous):
                nxt = continuous[i + 1][1]
                entry._entry.bind("<Return>", lambda _e, n=nxt: n.focus_set())

    # ── Add student ───────────────────────────────────────────────────────────

    def _on_add_student(self, _event=None):
        name = self._add_entry.get().strip()
        if not name or self._config_data is None:
            return
        student_id = add_student(name)
        add_enrollment(
            student_id,
            self._config_data["course_id"],
            self._config_data["school_year_id"],
            self._config_data["class"],
        )
        self._add_entry.delete(0, "end")
        self._rebuild_rows()



# ── Confirm save dialog ───────────────────────────────────────────────────────

class _ConfirmSaveDialog(ctk.CTkToplevel):
    def __init__(self, parent, blank_count: int, on_confirmed):
        super().__init__(parent)
        self._on_confirmed = on_confirmed
        self.title(t("confirm_save_title"))
        self.geometry("380x190")
        self.resizable(False, False)
        self.grab_set()

        if blank_count == 1:
            text = t("confirm_blank_one")
        else:
            text = t("confirm_blank_many", count=blank_count)
        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            justify="center",
        ).pack(pady=(36, 20), padx=24)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text=t("save_anyway"),
            command=self._confirm,
        ).pack(side="right")

    def _confirm(self):
        self._on_confirmed()
        self.destroy()


# ── Confirm remove dialog ─────────────────────────────────────────────────────

class _ConfirmRemoveDialog(ctk.CTkToplevel):
    def __init__(self, parent, enrollment_id: int, on_confirmed):
        super().__init__(parent)
        self._enrollment_id = enrollment_id
        self._on_confirmed = on_confirmed
        self.title(t("remove_student_title"))
        self.geometry("380x175")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text=t("remove_student_text"),
            font=ctk.CTkFont(size=13),
            justify="center",
        ).pack(pady=(32, 20), padx=24)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkButton(
            btn_row, text=t("cancel"),
            fg_color="transparent", border_width=1,
            text_color=INK, hover_color=ACCENT_SUBTLE,
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text=t("remove"),
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            command=self._confirm,
        ).pack(side="right")

    def _confirm(self):
        delete_enrollment(self._enrollment_id)
        undo_stack.clear()   # removing a student cascades grades, invalidating any open undo history
        self._on_confirmed()
        self.destroy()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _active_categories(config_id: int) -> list:
    weights = course_configs.get_weights(config_id)
    return [c for c in get_all_categories() if weights.get(c["id"], 0) > 0]


def _discrete_pairs(cat) -> list[tuple[str, str]]:
    """Return (display_label, value_string) pairs for a discrete category.

    Falls back to the raw values as labels when no labels are configured
    or the label count doesn't match.
    """
    values = [v.strip() for v in cat["discrete_values"].split(",")]
    labels_raw = cat["discrete_labels"] if "discrete_labels" in cat.keys() else None
    labels = [l.strip() for l in labels_raw.split(",")] if labels_raw else values
    if len(labels) != len(values):
        labels = values
    return list(zip(labels, values))


def _input_widget(parent, cat: dict):
    """Return a grade input widget appropriate for the category input type."""
    if cat["input_type"] == "discrete" and cat["discrete_values"]:
        labels = [label for label, _ in _discrete_pairs(cat)]
        seg = ctk.CTkSegmentedButton(
            parent, values=labels, width=COL_CAT, dynamic_resizing=False
        )
        seg.set("")   # nothing selected = skipped
        seg.pack(side="left", padx=2, pady=4)
        return seg
    else:
        entry = ctk.CTkEntry(parent, width=COL_CAT, justify="center")
        entry.pack(side="left", padx=2, pady=4)
        _wire_grade_entry_feedback(entry)
        return entry


def _wire_grade_entry_feedback(entry: ctk.CTkEntry) -> None:
    """Live-validate teacher notation: red border while invalid, and convert
    shorthand ("2+", "2-3", "2,5") to its numeric value when focus leaves."""
    default_border = entry.cget("border_color")

    def _on_key(_e):
        text = entry.get().strip()
        invalid = bool(text) and parse_grade_input(text) is None
        entry.configure(border_color=DANGER if invalid else default_border)

    def _on_focus_out(_e):
        text = entry.get().strip()
        value = parse_grade_input(text)
        if value is not None:
            normalized = format_grade(value)
            if normalized != text:
                entry.delete(0, "end")
                entry.insert(0, normalized)

    entry.bind("<KeyRelease>", _on_key)
    entry.bind("<FocusOut>", _on_focus_out)


def _short_date(date_str: str) -> str:
    """Trim "28.05.2026" → "28.05" for compact display in the detail strip."""
    parts = date_str.split(".")
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else date_str


def _date_sort_key(date_str: str | None) -> str:
    """Convert DD.MM.YYYY → YYYY-MM-DD for correct chronological string sort."""
    if not date_str:
        return ""
    parts = date_str.split(".")
    return f"{parts[2]}-{parts[1]}-{parts[0]}" if len(parts) == 3 else date_str



def _header_cat_button(parent, cat, command):
    """Clickable category column header used in normal (non-edit) mode.

    Wrapped in a fixed-width frame (pack_propagate off) so the button can't grow
    to fit long text — that growth is what threw the column grid out of alignment.
    """
    cell = ctk.CTkFrame(parent, width=COL_CAT, height=33,
                        fg_color="transparent", corner_radius=0)
    cell.pack(side="left")
    cell.pack_propagate(False)
    ctk.CTkButton(
        cell,
        text=cat["name"],
        fg_color="transparent",
        hover_color=ACCENT_SUBTLE,
        text_color=INK,
        font=ctk.CTkFont(size=12, weight="bold"),
        corner_radius=0,
        command=command,
    ).pack(fill="both", expand=True)


def _divider(parent):
    ctk.CTkFrame(
        parent, width=1, height=20, corner_radius=0,
        fg_color=_GRID_LINE,
    ).pack(side="left", padx=(8, 0))


def _vline(parent, color=_GRID_LINE):
    """Vertical grid rule spanning the full height of a table row.

    height=1 (not the CTkFrame default of 200) so the row's labels determine its
    height; fill="y" then stretches the rule to match.
    """
    ctk.CTkFrame(
        parent, width=1, height=1, fg_color=color, corner_radius=0
    ).pack(side="left", fill="y")


def _hline(parent, color=_GRID_LINE, height=1):
    """Horizontal grid rule spanning the full width."""
    ctk.CTkFrame(
        parent, height=height, fg_color=color, corner_radius=0
    ).pack(fill="x")


def _detail_subrow(parent, note_text, date_text, values_by_cid, active_cats,
                   note_color, date_color, cat_color_fn):
    """One ruled row of the expanded detail strip.

    The Notiz (130) + Datum (70) cells together occupy exactly COL_NAME, so the
    vertical rules and category cells line up pixel-for-pixel with the main table.
    """
    rowf = ctk.CTkFrame(parent, fg_color="transparent")
    rowf.pack(fill="x")

    ctk.CTkLabel(
        rowf, text=note_text, width=COL_NOTIZ, anchor="w",
        font=ctk.CTkFont(size=12), text_color=note_color,
    ).pack(side="left", padx=(8, 0))
    ctk.CTkLabel(
        rowf, text=date_text, width=COL_DATUM, anchor="e",
        font=ctk.CTkFont(size=12), text_color=date_color,
    ).pack(side="left")

    for cat in active_cats:
        _vline(rowf)
        val = values_by_cid.get(cat["id"], "")
        ctk.CTkLabel(
            rowf, text=val, width=COL_CAT, anchor="center",
            font=ctk.CTkFont(size=12), text_color=cat_color_fn(cat["id"], val),
        ).pack(side="left")


def _header_label(parent, text, width, anchor="center", padx=(0, 0),
                  final=False, highlight=False, dim=False):
    if highlight:
        color = _EDIT_ACTIVE_COLOR
    elif dim:
        color = INK_MUTED
    elif final:
        color = _FINAL_COLOR
    else:
        color = INK
    ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=color,
    ).pack(side="left", padx=padx, pady=6)


def _cell(parent, text, width, anchor="center", bold=False, padx=(0, 0),
          final=False, dim=False) -> ctk.CTkLabel:
    if dim:
        color = INK_MUTED
    elif final:
        color = _FINAL_COLOR
    else:
        color = INK
    lbl = ctk.CTkLabel(
        parent, text=text, width=width, anchor=anchor,
        font=ctk.CTkFont(size=13, weight="bold" if bold else "normal"),
        text_color=color,
    )
    lbl.pack(side="left", padx=padx, pady=6)
    return lbl


