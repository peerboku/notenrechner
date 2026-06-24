"""Central color palette — warm paper-gradebook look with a single navy accent.

All colors are (light, dark) tuples. The app ships in light ("paper") mode; the
dark values keep dark mode usable if it is offered as an option later.

Use the named constants directly in widget code (CustomTkinter accepts
(light, dark) tuples), and call apply_theme() once at startup to recolor the
default-styled widgets (buttons, entries, dropdowns, scrollbars).

The accent (navy) means exactly one thing everywhere: the primary action /
the value that matters (Save, the selected class, the Endnote column). It is
never reused as a decorative or label color. Destructive actions use DANGER.
"""

import customtkinter as ctk

# ── Surfaces (cream paper) ─────────────────────────────────────────────────────
PAPER       = ("#F4EFE4", "#1C1B18")   # window background
PAPER_ROW   = ("#FBF8F0", "#201F1B")   # table rows / fresh paper
PAPER_PANEL = ("#ECE5D5", "#26241F")   # sidebar and side panels
HEADER_BAND = ("#E6DECB", "#2B2823")   # column-header band
DETAIL_BG   = ("#EFE8D7", "#191815")   # expanded detail strip
INPUT_BG    = ("#FCFAF3", "#2A2823")   # text entry fields

# ── Ink (text) ─────────────────────────────────────────────────────────────────
INK         = ("#2B2620", "#E8E2D4")
INK_MUTED   = ("#8A7F66", "#9A917D")

# ── Grid lines ─────────────────────────────────────────────────────────────────
LINE        = ("#CFC5AE", "#3A372F")
LINE_HEAVY  = ("#AC9F80", "#4A4639")

# ── Accent (navy) — one color, one meaning: the primary action ─────────────────
ACCENT       = ("#1E3A5F", "#5B8FC7")
ACCENT_HOVER = ("#16304F", "#4D7FB5")
ON_ACCENT    = ("#F7F3E8", "#0F2236")   # text/icon on an accent fill
ACCENT_SUBTLE = ("#DCE4EE", "#233649")  # selected-item / hover tint

# ── Danger (destructive) — deliberately distinct from the accent ───────────────
DANGER       = ("#9B3B3B", "#C25A5A")
DANGER_HOVER = ("#843131", "#A84A4A")

# ── OK / valid (positive validation feedback, e.g. weight sum = 100%) ──────────
OK           = ("#3F6B3F", "#7CB07C")

# ── Edit-in-progress highlight (transient state, not the accent) ───────────────
EDIT_ACTIVE  = ("#B5701A", "#E0962E")   # amber: the column currently being filled


def _pair(t):
    return [t[0], t[1]]


def apply_theme():
    """Push the palette into CustomTkinter's default widget styling.

    Call after set_default_color_theme() and before creating widgets. Guarded so
    a future CTk version dropping a key won't crash startup.
    """
    th = ctk.ThemeManager.theme

    def setk(widget, **kv):
        block = th.get(widget)
        if not block:
            return
        for key, val in kv.items():
            if key in block:
                block[key] = val

    setk("CTk", fg_color=_pair(PAPER))
    setk("CTkToplevel", fg_color=_pair(PAPER))
    setk("CTkFrame",
         fg_color=_pair(PAPER_PANEL), top_fg_color=_pair(PAPER_PANEL),
         border_color=_pair(LINE))
    setk("CTkButton",
         fg_color=_pair(ACCENT), hover_color=_pair(ACCENT_HOVER),
         border_color=_pair(LINE_HEAVY), text_color=_pair(ON_ACCENT))
    setk("CTkLabel", text_color=_pair(INK))
    setk("CTkEntry",
         fg_color=_pair(INPUT_BG), border_color=_pair(LINE),
         text_color=_pair(INK), placeholder_text_color=_pair(INK_MUTED))
    setk("CTkComboBox",
         fg_color=_pair(INPUT_BG), border_color=_pair(LINE),
         button_color=_pair(ACCENT), button_hover_color=_pair(ACCENT_HOVER),
         text_color=_pair(INK))
    setk("CTkOptionMenu",
         fg_color=_pair(ACCENT), button_color=_pair(ACCENT_HOVER),
         button_hover_color=_pair(ACCENT_HOVER), text_color=_pair(ON_ACCENT))
    setk("CTkSegmentedButton",
         fg_color=_pair(PAPER_PANEL),
         selected_color=_pair(ACCENT), selected_hover_color=_pair(ACCENT_HOVER),
         unselected_color=_pair(PAPER_PANEL), unselected_hover_color=_pair(HEADER_BAND),
         text_color=_pair(INK))
    setk("CTkScrollbar",
         fg_color="transparent",
         button_color=_pair(LINE_HEAVY), button_hover_color=_pair(INK_MUTED))
    setk("DropdownMenu",
         fg_color=_pair(PAPER_PANEL), hover_color=_pair(ACCENT_SUBTLE),
         text_color=_pair(INK))
