"""
Palette and stylesheet.

The colours are carried over from the v2/v3 editors unchanged, so a scene looks
the same here as it did in the browser and muscle memory for "green is a camera
cut" still works.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont

BG = "#14151a"
PANEL = "#1e2028"
PANEL2 = "#262935"
TEXT = "#e8e9ed"
DIM = "#8b8fa3"
ACCENT = "#57b3ff"
GRID = "#2c2f3b"
PLAY = "#ff5757"
SEL = "#ffd257"
STAGE_BG = "#0a0b0f"

#: Block fills, keyed by `Lane.cls`.
#:
#: The structural rows keep the colours they had in v2 and v3, so a scene reads
#: the same as it always did. What changed is the cue rows: every one of them
#: used to be the same amber, which made a dozen rows of orange ticks that could
#: only be told apart by reading the label.
#:
#: They are now coloured by *family* rather than one hue per clip type. Twelve
#: unique hues would collide with each other and with the structural rows; seven
#: families are distinguishable at a glance and mean something - anything red is
#: flow control the game needs to progress, anything amber makes a noise,
#: anything yellow-green is lighting.
LANE_COLOR = {
    # structural - unchanged
    "shot": "#3d6fa8",   # blue
    "cut": "#5a8f5c",    # green
    "vo": "#7a3b6e",     # magenta
    "subt": "#3b6e7a",   # teal
    "vfx": "#2f7a6a",    # green-teal
    "lip": "#8a5a2b",    # brown
    # A switched-off cue is GREY, not red. Red is the colour of a range being
    # removed, and a disabled cue is not that: nothing is deleted, the name is
    # simply broken so the lookup misses, and pressing Del again puts it back.
    # Two different reds for two different meanings made the timeline read as
    # more destructive than the edit actually is. Grey plus the strike-through
    # says "off" without saying "gone".
    "del": "#4a4d55",    # grey, struck through
    # cue families
    "audio": "#a8783d",   # amber   - SE
    "rumble": "#a8553d",  # rust    - vibration
    "music": "#a83d7a",   # rose    - BGM
    "fade": "#6e5aa8",    # indigo  - fades
    "actor": "#4a8fa8",   # cyan    - show/hide, crowd, speed
    "light": "#a8a03d",   # yellow  - dir/env light
    "flow": "#a83d4f",    # crimson - state triggers, jumps
    "rig": "#6a6f9a",     # violet  - constraints, bindings
    "system": "#5f7f8f",  # slate   - streaming volumes
    "evt": "#8b8f6a",     # olive   - anything unrecognised
    "anim": "#6d8f4a",    # moss    - animation clip rows (blocks tint by character)
}

#: Key-tick marks along the bottom of a row.
KEY_MARK = "#c9cede"

#: The band over a range marked for deletion: stripes, edges and ruler mark.
#:
#: Deliberately *not* `LANE_COLOR['del']`. That red is a block fill, chosen to
#: sit quietly behind white text, and it is far too dark to read as a stripe
#: laid over rows that are themselves mid-tone. This one is picked to survive
#: being drawn on top of anything in the tracker.
CUT = "#ff5a4d"


#: Who is who on the stage, keyed by `core.characters.canonical`.
#:
#: Chosen to stay legible on the near-black stage plate and to stay apart from
#: each other at pin size, which is about eight pixels. Two were not specified
#: and are placeholders, marked below.
CHARACTER_COLOR = {
    "sephiroth": "#dfe3ea",   # light silver
    "cloud": "#79d0cf",       # baby teal
    "barret": "#a06a40",      # brown
    "tifa": "#ecc94b",        # yellow
    "aerith": "#f5a9c8",      # baby pink
    "redxiii": "#e8792b",     # orange
    "yuffie": "#5cb85c",      # green
    "vincent": "#b02a37",     # deepish red
    "cid": "#3a5fa8",         # darkish blue
    "caitsith": "#9b6fd0",    # violet      - placeholder, not specified
    "zack": "#6fa8d8",        # steel blue  - placeholder, not specified
    "feeler": "#f4f1d8",      # near white, slightly yellow
    "event": "#7f8699",       # extras, doubles and props - the grey they had
    "npc": "#c85fc8",         # everyone else
}

#: Reading order for a legend: cast first, then the catch-alls.
CHARACTER_ORDER = (
    "cloud", "barret", "tifa", "aerith", "redxiii", "yuffie", "caitsith",
    "zack", "vincent", "cid", "sephiroth", "feeler", "npc", "event",
)

#: Display names, for anywhere the key itself would be unreadable.
CHARACTER_LABEL = {
    "redxiii": "Red XIII",
    "caitsith": "Cait Sith",
    "feeler": "Feelers",
    "event": "Extras & props",
    "npc": "Other NPCs",
}


def character_color(key: str) -> str:
    return CHARACTER_COLOR.get(key, CHARACTER_COLOR["npc"])


def character_label(key: str) -> str:
    return CHARACTER_LABEL.get(key, key.capitalize())


def c(name: str, alpha: float = 1.0) -> QColor:
    col = QColor(name)
    if alpha < 1.0:
        col.setAlphaF(alpha)
    return col


def ui_font(size: int = 9, bold: bool = False) -> QFont:
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    return f


def mono_font(size: int = 9) -> QFont:
    f = QFont("Consolas", size)
    f.setStyleHint(QFont.Monospace)
    return f


STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: "Segoe UI";
    font-size: 12px;
}}
QDockWidget {{
    titlebar-close-icon: none;
    color: {DIM};
    font-size: 11px;
}}
QDockWidget::title {{
    background: {PANEL};
    padding: 5px 8px;
    border-bottom: 1px solid #000;
}}
QToolBar {{
    background: {PANEL};
    border: 0;
    border-bottom: 1px solid #000;
    spacing: 4px;
    padding: 4px 8px;
}}
QToolBar QToolButton, QPushButton {{
    background: {PANEL2};
    border: 1px solid #4a4f63;
    border-radius: 4px;
    padding: 4px 10px;
    color: {TEXT};
}}
QToolBar QToolButton:hover, QPushButton:hover {{ border-color: {ACCENT}; }}
QToolBar QToolButton:disabled, QPushButton:disabled {{ color: #575c70; border-color: #33374a; }}
/* Toolbar toggles are tick boxes rather than buttons that look faintly
   pressed: three of them in a row have to be readable at a glance. */
QCheckBox {{ color: {TEXT}; spacing: 6px; padding: 3px 4px; }}
QCheckBox:disabled {{ color: #575c70; }}
QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 1px solid #4a4f63;
    border-radius: 3px;
    background: {PANEL2};
}}
QCheckBox::indicator:hover {{ border-color: {ACCENT}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QCheckBox::indicator:disabled {{ border-color: #33374a; background: {PANEL}; }}
QComboBox, QLineEdit {{
    background: {PANEL2};
    border: 1px solid #4a4f63;
    border-radius: 4px;
    padding: 3px 8px;
    color: {TEXT};
    selection-background-color: {ACCENT};
}}
QComboBox QAbstractItemView {{
    background: {PANEL2};
    border: 1px solid #4a4f63;
    selection-background-color: #2f4a6b;
}}
QListWidget, QTreeWidget, QPlainTextEdit, QTextEdit {{
    background: {PANEL};
    border: 1px solid {GRID};
    border-radius: 4px;
    selection-background-color: #2f4a6b;
}}
QListWidget::item {{ padding: 3px 6px; }}
QSplitter::handle {{ background: {GRID}; }}
QSplitter::handle:horizontal {{ width: 4px; }}
QSplitter::handle:vertical {{ height: 4px; }}
QScrollBar:vertical, QScrollBar:horizontal {{ background: {BG}; border: 0; }}
QScrollBar:vertical {{ width: 12px; }}
QScrollBar:horizontal {{ height: 12px; }}
QScrollBar::handle {{ background: #3c4152; border-radius: 5px; min-height: 24px; min-width: 24px; }}
QScrollBar::handle:hover {{ background: #4d5468; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QStatusBar {{ background: {PANEL}; color: {DIM}; border-top: 1px solid #000; }}
QLabel[role="dim"] {{ color: {DIM}; font-size: 11px; }}
QLabel[role="heading"] {{ color: {TEXT}; font-weight: 600; }}
QMenu {{ background: {PANEL2}; border: 1px solid #4a4f63; }}
QMenu::item:selected {{ background: #2f4a6b; }}
"""
