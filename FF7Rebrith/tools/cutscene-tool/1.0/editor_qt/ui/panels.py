"""
The side panels: the scene list, the details pane, the actors pane.

All three are dock widgets in the main window, which is the point - each can be
resized, torn off, stacked or hidden, and the arrangement is remembered. In the
browser build these were fixed blocks in a column with no way to change them.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from ..core.characters import canonical
from ..core.edits import EditState, actor_pin, all_pins, pin_spans_for
from ..core.lanes import Lane, LaneItem
from ..core.library import SceneEntry, SceneLibrary
from ..core.stage import StageFrame, in_frame
from ..core.text import window_around
from ..core.timeline import Cutscene
from . import theme


def _mmss(tick: float) -> str:
    """`m:ss.hh` without needing the scene's TimeBase in this file."""
    s = max(0.0, tick) / 24000.0
    return "%d:%05.2f" % (int(s // 60), s - int(s // 60) * 60)


#: Extra roles on a list item, for the delegate to paint.
ROLE_EV = Qt.UserRole
ROLE_META = Qt.UserRole + 1
ROLE_CAPTION = Qt.UserRole + 2
ROLE_IS_HIT = Qt.UserRole + 3
ROLE_QUERY = Qt.UserRole + 4


class SceneRowDelegate(QStyledItemDelegate):
    """Two lines per scene: the name and time on top, a line of dialogue under.

    The dialogue line is the point. A cutscene called EV_FOREE_8510 tells you
    nothing; "Cloud: Aerith... Wake up." tells you exactly which scene it is.
    When a search matched a spoken line rather than the name, that line is shown
    instead of the first one, with the matched words picked out.
    """

    LINE1 = 17
    LINE2 = 16
    PAD = 4

    def sizeHint(self, option, index) -> QSize:
        return QSize(option.rect.width(), self.LINE1 + self.LINE2 + self.PAD * 2)

    def paint(self, painter: QPainter, option, index) -> None:
        painter.save()
        rect = option.rect
        selected = bool(option.state & QStyle.State_Selected)
        if selected:
            painter.fillRect(rect, theme.c("#2f4a6b"))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(rect, theme.c(theme.PANEL2))

        x = rect.left() + 8
        w = rect.width() - 16

        name = index.data(Qt.DisplayRole) or ""
        meta = index.data(ROLE_META) or ""
        caption = index.data(ROLE_CAPTION) or ""
        is_hit = bool(index.data(ROLE_IS_HIT))
        query = index.data(ROLE_QUERY) or ""

        # line 1: name on the left, duration and area right-aligned.
        # Constant weight on purpose: bolding the selected row re-measures the
        # text and elides a name that fitted a moment ago, which reads as the
        # list jumping about.
        painter.setFont(theme.ui_font(9))
        fm = QFontMetrics(painter.font())
        meta_w = fm.horizontalAdvance(meta) + 10 if meta else 0
        top = QRect(x, rect.top() + self.PAD, w - meta_w, self.LINE1)
        painter.setPen(QColor(theme.TEXT))
        painter.drawText(top, Qt.AlignLeft | Qt.AlignVCenter,
                         fm.elidedText(name, Qt.ElideRight, top.width()))
        if meta:
            painter.setPen(QColor(theme.DIM))
            painter.drawText(QRect(x + w - meta_w, rect.top() + self.PAD, meta_w, self.LINE1),
                             Qt.AlignRight | Qt.AlignVCenter, meta)

        # line 2: the dialogue
        bottom = QRect(x, rect.top() + self.PAD + self.LINE1, w, self.LINE2)
        font = theme.ui_font(8)
        font.setItalic(True)
        painter.setFont(font)
        fm2 = QFontMetrics(font)
        if not caption:
            painter.setPen(QColor("#4a4f60"))
            painter.drawText(bottom, Qt.AlignLeft | Qt.AlignVCenter, "no dialogue")
            painter.restore()
            return

        if is_hit and query:
            # keep the matched words on screen; the tail is the expendable part
            caption = window_around(caption, query, bottom.width() // 6)
        text = fm2.elidedText(caption, Qt.ElideRight, bottom.width())
        painter.setPen(theme.c(theme.ACCENT) if is_hit else QColor(theme.DIM))
        if is_hit and query:
            self._draw_highlighted(painter, bottom, text, query, fm2)
        else:
            painter.drawText(bottom, Qt.AlignLeft | Qt.AlignVCenter, text)
        painter.restore()

    def _draw_highlighted(self, painter, rect, text, query, fm) -> None:
        """Paint the matched words brighter than the rest of the line."""
        at = text.lower().find(query.lower())
        if at < 0:
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
            return
        before, hit, after = text[:at], text[at:at + len(query)], text[at + len(query):]
        cx = rect.left()
        for part, colour in (
            (before, QColor(theme.DIM)),
            (hit, QColor(theme.SEL)),
            (after, QColor(theme.DIM)),
        ):
            if not part:
                continue
            painter.setPen(colour)
            width = fm.horizontalAdvance(part)
            painter.drawText(QRect(cx, rect.top(), width + 2, rect.height()),
                             Qt.AlignLeft | Qt.AlignVCenter, part)
            cx += width


class ScenePanel(QWidget):
    """Every extracted cutscene, filtered as you type - by name or by line."""

    scene_chosen = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._library: Optional[SceneLibrary] = None
        self._total = 0

        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search names, cast or dialogue…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._queue_refilter)

        # typing is cheap over 755 entries, but not free; coalesce keystrokes
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(110)
        self._debounce.timeout.connect(self._refilter)

        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.setUniformItemSizes(True)
        self.list.setItemDelegate(SceneRowDelegate(self.list))
        self.list.setMouseTracking(True)
        self.list.itemActivated.connect(self._activate)
        self.list.itemClicked.connect(self._activate)

        self.count = QLabel("", self)
        self.count.setProperty("role", "dim")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(5)
        lay.addWidget(self.search)
        lay.addWidget(self.list, 1)
        lay.addWidget(self.count)

    def set_library(self, library: SceneLibrary) -> None:
        self._library = library
        self._total = len(library.entries)
        self._refilter()

    def select(self, ev: str) -> None:
        for i in range(self.list.count()):
            if self.list.item(i).data(ROLE_EV) == ev:
                self.list.setCurrentRow(i)
                self.list.scrollToItem(self.list.item(i))
                return

    def _queue_refilter(self) -> None:
        self._debounce.start()

    def _refilter(self) -> None:
        if not self._library:
            return
        query = self.search.text().strip()
        matches = self._library.search(query)

        self.list.setUpdatesEnabled(False)
        self.list.clear()
        spoken = 0
        for m in matches:
            item = QListWidgetItem(m.entry.ev)
            item.setData(ROLE_EV, m.entry.ev)
            item.setData(ROLE_META, m.entry.meta)
            item.setData(ROLE_CAPTION, m.caption)
            item.setData(ROLE_IS_HIT, bool(m.hit))
            item.setData(ROLE_QUERY, query)
            if m.caption:
                item.setToolTip(m.caption)
            self.list.addItem(item)
            if m.hit:
                spoken += 1
        self.list.setUpdatesEnabled(True)

        if query and spoken:
            self.count.setText(
                "%d of %d  ·  %d matched on dialogue"
                % (len(matches), self._total, spoken)
            )
        else:
            self.count.setText("%d of %d cutscenes" % (len(matches), self._total))

    def _activate(self, item: QListWidgetItem) -> None:
        ev = item.data(ROLE_EV)
        if ev:
            self.scene_chosen.emit(ev)


class DetailsPanel(QWidget):
    """Whatever the selected block actually carries, unabridged.

    Cue properties are the raw extracted dict on purpose: when a cue does not
    behave the way the editor claims, this is where you find out why.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.heading = QLabel("Click any block…", self)
        self.heading.setProperty("role", "heading")
        self.heading.setWordWrap(True)

        self.body = QPlainTextEdit(self)
        self.body.setReadOnly(True)
        self.body.setFont(theme.mono_font(9))
        self.body.setLineWrapMode(QPlainTextEdit.NoWrap)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)
        lay.addWidget(self.heading)
        lay.addWidget(self.body, 1)

    def clear(self) -> None:
        self.heading.setText("Click any block…")
        self.body.setPlainText("")

    def show_item(self, cs: Cutscene, item: Optional[LaneItem],
                  lane: Optional[Lane], repoint=None) -> None:
        if item is None:
            self.clear()
            return
        t = cs.time
        a, b = item.range
        head = "%s · %s" % (lane.label if lane else item.type, item.name or item.type)
        self.heading.setText(head)

        lines = [
            "type       %s" % item.type,
            "clip       %s" % (item.clip or "—"),
            "sequence   %s" % (item.seq or "—"),
            "start      %s   (%d ticks, frame %d)" % (t.format(a), a, t.to_frame(a)),
            "end        %s   (%d ticks, frame %d)" % (t.format(b), b, t.to_frame(b)),
            "length     %s" % t.describe_span(b - a),
            "aligned    %s" % ("yes" if t.is_frame_aligned(a) else "NO — not on a frame"),
        ]
        if item.moved_from is not None:
            delta = a - item.moved_from
            lines += [
                "",
                "moved      from %s (%d ticks)" % (t.format(item.moved_from),
                                                   item.moved_from),
                "           %s %s   —  press R to put it back"
                % ("later by" if delta > 0 else "earlier by",
                   t.describe_span(abs(delta))),
            ]
        if repoint is not None:
            # The properties below are the scene's, unedited, which is the
            # point of this panel - so the repoint is stated separately rather
            # than folded into them. `MusicName` down there still reads what
            # the scene shipped, and that is not a mistake.
            lines += [
                "",
                "music      %s  →  %s" % (repoint.frm, repoint.to),
                "           %s" % (repoint.label or "—"),
                "           the scene's own MusicName is unchanged below;"
                " the build rewrites it",
            ]
        if item.voice:
            v = item.voice
            lines += [
                "",
                "voice      %s" % v.name,
                "recording  %.3fs" % v.full,
                "kept       %.3fs%s" % (v.kept, "" if v.kept >= v.full else "  (trimmed)"),
            ]
        if item.props:
            lines += ["", "properties"]
            lines += [
                "  %s" % ln
                for ln in json.dumps(item.props, indent=2, ensure_ascii=False).splitlines()
            ]
        self.body.setPlainText("\n".join(lines))


class ActorPanel(QWidget):
    """Every actor the scene shows or hides, each pinnable.

    Pinning exists because an actor's show/hide cue can sit inside a cut, where
    clicking the cue is impossible - which is exactly the case that produced the
    Aerith double staying on screen.

    A pin can cover the whole scene or just a selected range. The range came
    second and from a real fault: EV_FOREE_8514 puts both Aeriths on screen
    from 95s to the end on purpose - the clean one is the body on the floor -
    so a whole-scene Hide to stop five seconds of Z-fighting also deleted her
    from every shot after it.
    """

    pin_changed = Signal(str, str)        # actor, 'normal' | 'show' | 'hide'
    pin_ranged = Signal(str, bool)        # actor, hidden - over the selection
    pin_span_cleared = Signal(str)        # actor - drop its bounded pin(s)
    pin_removed = Signal(object)          # PinEntry - drop exactly this one
    pins_cleared = Signal()               # drop the lot

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._groups: Dict[str, QButtonGroup] = {}
        self._selection_text = ""
        self._effect: Dict[str, str] = {}

        self.note = QLabel(
            "Set an actor to Show or Hide to pin it for the whole scene — "
            "no need to find its cues, which may sit inside a cut.\n"
            "To pin only part of the scene, drag a range on the timeline first, "
            "then use the range buttons.",
            self,
        )
        self.note.setProperty("role", "dim")
        self.note.setWordWrap(True)

        self.inner = QWidget(self)
        self.grid = QGridLayout(self.inner)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(3)

        scroll = QScrollArea(self)
        scroll.setWidget(self.inner)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        # Every pin in the scene, in one place. A bounded pin lives on the
        # plan across sessions, and listing it only beside its own actor made
        # an old one easy to lose track of and awkward to find again.
        self.summary = QWidget(self)
        self.summary_lay = QVBoxLayout(self.summary)
        self.summary_lay.setContentsMargins(0, 0, 0, 0)
        self.summary_lay.setSpacing(2)
        self.summary.hide()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)
        lay.addWidget(self.note)
        lay.addWidget(self.summary)
        lay.addWidget(scroll, 1)

    def set_selection_label(self, text: str, counts=None) -> None:
        """What the range buttons would apply to, or '' when nothing is
        selected. Kept as text so this panel needs no TimeBase of its own.

        `counts` is actor -> a plain sentence describing what pinning over the
        selection would actually do, worked out by the window because only it
        knows the scene. Visibility is a step function, so "from 1:35.00" is
        the honest answer far more often than "over the range you drew".
        """
        self._selection_text = text
        self._effect = counts or {}

    def set_actors(self, actors: List[str], state: EditState) -> None:
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                # unparent first: deleteLater only destroys once the event loop
                # gets round to it, and until then the old row is still painted
                w.setParent(None)
                w.deleteLater()
        self._groups.clear()

        if not actors:
            empty = QLabel("This scene shows or hides no actors.", self.inner)
            empty.setProperty("role", "dim")
            self.grid.addWidget(empty, 0, 0, 1, 4)
            return

        for row, actor in enumerate(actors):
            # the swatch is how you tell cut_PC0003_00a from cut_PC0000_00b at a
            # glance - the two doubles whose pins were the reason for this panel
            who = canonical(actor)
            label = QLabel(
                "<span style='color:%s'>■</span> %s"
                % (theme.character_color(who), actor),
                self.inner,
            )
            label.setToolTip("%s — %s" % (actor, theme.character_label(who)))
            self.grid.addWidget(label, row, 0)
            group = QButtonGroup(self.inner)
            pin = actor_pin(state, actor)
            for col, mode in enumerate(("normal", "show", "hide"), start=1):
                rb = QRadioButton(mode.capitalize(), self.inner)
                rb.setChecked(pin == mode)
                rb.toggled.connect(
                    lambda checked, a=actor, m=mode: (
                        self.pin_changed.emit(a, m) if checked else None
                    )
                )
                group.addButton(rb)
                self.grid.addWidget(rb, row, col)
            self._groups[actor] = group

            # the same two states, but only over the selected range
            for col, (text, hide) in enumerate(
                (("Show ▸", False), ("Hide ▸", True)), start=4
            ):
                btn = QPushButton(text, self.inner)
                btn.setFixedWidth(58)
                # Always live when there is a range. A window with no command
                # inside it still works - the command before it is what the
                # window's state comes from, and that is the one rewritten.
                btn.setEnabled(bool(self._selection_text))
                btn.setToolTip(
                    ("Keep %s %s across %s, and the opposite outside it.\n%s"
                     % (actor, "hidden" if hide else "visible",
                        self._selection_text, self._effect.get(actor, "")))
                    if self._selection_text
                    else "Drag a range on the timeline to enable this"
                )
                btn.clicked.connect(
                    lambda _c=False, a=actor, h=hide: self.pin_ranged.emit(a, h)
                )
                self.grid.addWidget(btn, row, col)

            spans = pin_spans_for(state, actor)
            if spans:
                p0 = spans[0]
                row_w = QWidget(self.inner)
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                row_l.setSpacing(4)
                lab = QLabel("%s %s–%s" % ("hidden" if p0.hidden else "visible",
                                           _mmss(p0.a), _mmss(p0.b)), row_w)
                lab.setStyleSheet("color: %s;" % theme.SEL)
                # `×` rather than a dingbat: it is Latin-1, so it renders in
                # whatever font Qt picks instead of coming out as a box
                clear = QPushButton("×", row_w)
                clear.setFixedWidth(22)
                clear.setToolTip("Remove this range pin")
                clear.clicked.connect(
                    lambda _c=False, a=actor: self.pin_span_cleared.emit(a)
                )
                row_l.addWidget(lab)
                row_l.addWidget(clear)
                row_l.addStretch(1)
                self.grid.addWidget(row_w, row, 6)
        self.grid.setRowStretch(len(actors), 1)
        self._rebuild_summary(state)

    def _rebuild_summary(self, state: EditState) -> None:
        """One line per pin in the scene, each with its own remove button."""
        while self.summary_lay.count():
            w = self.summary_lay.takeAt(0).widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        entries = all_pins(state)
        if not entries:
            self.summary.hide()
            return
        self.summary.show()

        head = QWidget(self.summary)
        head_l = QHBoxLayout(head)
        head_l.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Pins in this scene (%d)" % len(entries), head)
        title.setStyleSheet("color: %s; font-weight: bold;" % theme.TEXT)
        drop = QPushButton("Clear all", head)
        drop.setFixedWidth(70)
        drop.setToolTip("Remove every visibility pin in this scene")
        drop.clicked.connect(lambda _c=False: self.pins_cleared.emit())
        head_l.addWidget(title)
        head_l.addStretch(1)
        head_l.addWidget(drop)
        self.summary_lay.addWidget(head)

        for e in entries:
            w = QWidget(self.summary)
            wl = QHBoxLayout(w)
            wl.setContentsMargins(10, 0, 0, 0)
            wl.setSpacing(6)
            where = ("whole scene" if e.is_global
                     else "%s – %s" % (_mmss(e.span.a), _mmss(e.span.b)))
            dot = QLabel("<span style='color:%s'>■</span>"
                         % theme.character_color(canonical(e.actor)), w)
            lab = QLabel("%s — %s — %s"
                         % (e.actor, "hidden" if e.hidden else "visible", where), w)
            lab.setStyleSheet("color: %s;" % (theme.DIM if e.is_global else theme.SEL))
            rm = QPushButton("×", w)
            rm.setFixedWidth(22)
            rm.setToolTip("Remove this pin")
            rm.clicked.connect(lambda _c=False, x=e: self.pin_removed.emit(x))
            wl.addWidget(dot)
            wl.addWidget(lab)
            wl.addStretch(1)
            wl.addWidget(rm)
            self.summary_lay.addWidget(w)


class StageInfoPanel(QWidget):
    """Who is in frame, how far away, and where the camera is."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.body = QLabel("", self)
        self.body.setTextFormat(Qt.RichText)
        self.body.setWordWrap(True)
        self.body.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # The cast in frame changes on every scrubbed frame, and a word-wrapped
        # QLabel asks for however much height its current text needs. In a plain
        # layout that answer becomes the dock's minimum, so scrubbing into a
        # crowded shot grew this panel and pushed everything stacked with it off
        # the bottom of the screen. Inside a scroll area the label may be as
        # tall as it likes and the panel stays the size it was given.
        area = QScrollArea(self)
        area.setWidget(self.body)
        area.setWidgetResizable(True)
        area.setFrameShape(QFrame.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.addWidget(area, 1)

    def sizeHint(self) -> QSize:
        return QSize(260, 150)

    def minimumSizeHint(self) -> QSize:
        """Deliberately small: what the panel needs, not what it happens to
        hold. Anything longer scrolls."""
        return QSize(140, 60)

    def set_frame(self, frame: Any) -> None:
        if frame is None:
            self.body.setText(
                "<span style='color:%s'>no sampled scene data</span>" % theme.DIM
            )
            return
        parts: List[str] = []
        cam = frame.cam
        if cam:
            parts.append(
                "<b>FOV</b> %d° · cam (%d, %d, %d)"
                % (round(cam[6]), int(cam[0]), int(cam[1]), int(cam[2]))
            )

        # nearest first, and each name in that character's own colour, so this
        # list and the two stage views agree at a glance
        shown = sorted(
            ((a, pr) for a, _p, pr in frame.points if in_frame(pr)),
            key=lambda q: q[1].d,
        )
        parts.append("<br><b>In frame (%d)</b>" % len(shown))
        for actor, pr in shown:
            colour = theme.character_color(StageFrame.who(actor))
            centre = " · centre" if abs(pr.x) < 0.33 else ""
            parts.append(
                "<span style='color:%s'>•</span> %s "
                "<span style='color:%s'>%.1fm%s</span>"
                % (colour, actor.get("label", ""), theme.DIM, pr.d / 100.0, centre)
            )

        off = [a for a, _p, pr in frame.points if not in_frame(pr)]
        if off:
            names = ", ".join(
                "<span style='color:%s'>%s</span>"
                % (theme.character_color(StageFrame.who(a)), a.get("label", ""))
                for a in off
            )
            parts.append("<span style='color:%s'>off:</span> %s" % (theme.DIM, names))
        self.body.setText("<br>".join(parts))
