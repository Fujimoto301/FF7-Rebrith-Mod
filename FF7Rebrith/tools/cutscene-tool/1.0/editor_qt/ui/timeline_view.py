"""
The timeline.

This is the widget the whole rebuild was for. The browser version laid the
tracker out in normal document flow, so the row labels scrolled away from their
rows, long scenes ran off the right edge with no way back, and nothing could be
resized. Here:

* the label gutter and the ruler are painted at fixed positions in the viewport,
  so they cannot scroll out of reach no matter how far you pan or zoom;
* horizontal and vertical scrolling are real scrollbars owned by Qt;
* zoom is unbounded in the useful direction - a 90-second scene can be read at
  whole-scene scale or at a single frame per 40 pixels;
* only the blocks intersecting the viewport are painted, which is what makes a
  lip-sync row of several thousand phonemes cost nothing.

Painting is deliberately immediate-mode rather than a scene graph of items:
these are rectangles, there can be tens of thousands of them, and culling by
time is a binary search.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Dict, List, Optional, Sequence, Tuple

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QAbstractScrollArea, QWidget

from ..core import drag as drag_core
from ..core.arrays import ArrayIndex
from ..core.collapse import CollapsePlan
from ..core.cues import cue_descriptor, cue_key
from ..core.drag import Drag
from ..core.edits import CutSpan, EditState, empty_edits
from ..core.lanes import Lane, LaneItem, can_move
from ..core.timeline import Cutscene
from ..core.waveform import Waveform
from . import theme

LABEL_W = 168
RULER_H = 26
LANE_H = 22
LANE_GAP = 3
ROW_PITCH = LANE_H + LANE_GAP
TOP_PAD = 4
#: Height of the waveform row when the scene has a rendered mix.
WAVE_H = 52

MIN_PX_PER_SEC = 2.0
MAX_PX_PER_SEC = 4000.0

#: Pointer travel before a press on a cue becomes a drag rather than a click.
#:
#: Without it every click on a block would author a move of a pixel or two,
#: which is worse than useless: it looks like nothing happened and it puts an
#: entry in the plan.
DRAG_THRESHOLD_PX = 4


class TimelineView(QAbstractScrollArea):
    """Rows of blocks against a time ruler."""

    playhead_moved = Signal(float)          # tick, from scrubbing
    item_selected = Signal(object, object)  # LaneItem | None, Lane | None
    selection_changed = Signal(object)      # CutSpan | None
    cue_drag_preview = Signal(object)       # Drag | None, while the mouse is down
    cue_dragged = Signal(object)            # Drag, on release
    #: right-click on a block: LaneItem | None, Lane | None, global QPoint.
    #: The window owns the menu because what can be done to a cue is an editing
    #: question, and `core/` is where those answers live - the tracker only
    #: says which block the pointer was over.
    context_requested = Signal(object, object, object)
    #: (index, count) of the block a click resolved to, when blocks overlap.
    #: The window turns a count above one into a line in the status bar; two
    #: cues on the same frame are otherwise indistinguishable from one.
    stack_hit = Signal(int, int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        self._cs: Optional[Cutscene] = None
        self._lanes: List[Lane] = []
        self._starts: Dict[str, List[float]] = {}
        self._edits: EditState = empty_edits()
        #: what preserving fades and streaming is doing to the current cuts
        self._collapse: Optional[CollapsePlan] = None
        self._wave: Optional[Waveform] = None

        self._px_per_sec = 40.0
        self._playhead = 0.0
        self._selected: Optional[LaneItem] = None
        self._selection: Optional[CutSpan] = None
        self._drag_from: Optional[float] = None
        self._scrubbing = False
        #: which cues share a Times array, so a drag can be clamped to the gap
        #: between its neighbours rather than refused during the build
        self._arrays: Optional[ArrayIndex] = None
        #: the press that might become a drag: (pos, tick, item, lane)
        self._press: Optional[Tuple[QPoint, float, LaneItem, Lane]] = None
        #: the live proposal while a cue is being dragged
        self._drag: Optional[Drag] = None

        self.horizontalScrollBar().valueChanged.connect(lambda _v: self.viewport().update())
        self.verticalScrollBar().valueChanged.connect(lambda _v: self.viewport().update())

    # -- content --------------------------------------------------------

    def set_cutscene(self, cs: Optional[Cutscene], lanes: Sequence[Lane]) -> None:
        self._cs = cs
        self._lanes = list(lanes)
        # sorted start times per lane, so painting can binary-search the window
        self._starts = {
            ln.id: [it.range[0] for it in sorted(ln.items, key=lambda i: i.range[0])]
            for ln in self._lanes
        }
        for ln in self._lanes:
            ln.items.sort(key=lambda i: i.range[0])
        self._selected = None
        self._selection = None
        self._playhead = 0.0
        if cs:
            self.zoom_to_fit()
        self._sync_scrollbars()
        self.viewport().update()

    def set_edits(self, edits: EditState) -> None:
        """The cuts as they will be APPLIED - see `core.collapse.effective`.

        The view draws what gets built, not what was drawn: a cut held back to
        keep a streaming command really is shorter, and showing the longer band
        would be a lie the build then contradicts.
        """
        self._edits = edits
        self.viewport().update()

    def set_collapse(self, plan: Optional[CollapsePlan]) -> None:
        self._collapse = plan
        self.viewport().update()

    def set_array_index(self, index: Optional[ArrayIndex]) -> None:
        """The Times-array membership used to clamp a drag. See core.arrays."""
        self._arrays = index

    def set_waveform(self, wave: Optional[Waveform]) -> None:
        """The scene mix as an envelope, or None to drop the row."""
        self._wave = wave if (wave and not wave.empty) else None
        self._sync_scrollbars()
        self.viewport().update()

    @property
    def _wave_h(self) -> int:
        return WAVE_H if self._wave else 0

    def set_lanes(self, lanes: Sequence[Lane]) -> None:
        """Rebuild the rows without disturbing zoom, scroll or playhead.

        This is what an edit calls: `build_lanes` is cheap and pure, so the
        honest thing is to rebuild rather than to patch rows in place.
        """
        self._lanes = list(lanes)
        for ln in self._lanes:
            ln.items.sort(key=lambda i: i.range[0])
        self._starts = {ln.id: [it.range[0] for it in ln.items] for ln in self._lanes}
        self._selected = None
        self._sync_scrollbars()
        self.viewport().update()

    # -- transform ------------------------------------------------------

    @property
    def _ticks_per_sec(self) -> float:
        return self._cs.time.ticks_per_second if self._cs else 24000.0

    def _px_per_tick(self) -> float:
        return self._px_per_sec / self._ticks_per_sec

    def _time_width(self) -> int:
        return max(0, self.viewport().width() - LABEL_W)

    def x_of(self, t: float) -> float:
        return LABEL_W + t * self._px_per_tick() - self.horizontalScrollBar().value()

    def tick_at(self, x: float) -> float:
        return (x - LABEL_W + self.horizontalScrollBar().value()) / self._px_per_tick()

    def _content_px(self) -> int:
        return int((self._cs.total if self._cs else 0) * self._px_per_tick()) + 40

    def _lanes_px(self) -> int:
        return TOP_PAD + self._wave_h + len(self._lanes) * ROW_PITCH + 8

    def _row_y(self, index: int) -> float:
        """Top of row `index` in viewport coordinates."""
        return (
            RULER_H + TOP_PAD + self._wave_h
            + index * ROW_PITCH
            - self.verticalScrollBar().value()
        )

    def _sync_scrollbars(self) -> None:
        h = self.horizontalScrollBar()
        h.setPageStep(self._time_width())
        h.setSingleStep(40)
        h.setRange(0, max(0, self._content_px() - self._time_width()))
        v = self.verticalScrollBar()
        view_h = max(0, self.viewport().height() - RULER_H)
        v.setPageStep(view_h)
        v.setSingleStep(ROW_PITCH)
        v.setRange(0, max(0, self._lanes_px() - view_h))

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._sync_scrollbars()

    # -- zoom -----------------------------------------------------------

    def zoom_to_fit(self) -> None:
        if not self._cs or self._cs.total <= 0:
            return
        seconds = self._cs.total / self._ticks_per_sec
        width = max(200, self._time_width() - 20)
        self._px_per_sec = max(MIN_PX_PER_SEC, min(MAX_PX_PER_SEC, width / seconds))
        self.horizontalScrollBar().setValue(0)
        self._sync_scrollbars()
        self.viewport().update()

    def zoom_by(self, factor: float, anchor_x: Optional[float] = None) -> None:
        if not self._cs:
            return
        if anchor_x is None:
            anchor_x = LABEL_W + self._time_width() / 2
        anchor_t = self.tick_at(anchor_x)
        self._px_per_sec = max(
            MIN_PX_PER_SEC, min(MAX_PX_PER_SEC, self._px_per_sec * factor)
        )
        self._sync_scrollbars()
        # keep the tick under the cursor where it was
        want = anchor_t * self._px_per_tick() - (anchor_x - LABEL_W)
        self.horizontalScrollBar().setValue(int(want))
        self.viewport().update()

    def ensure_visible(self, t: float, margin: int = 60) -> None:
        x = self.x_of(t)
        h = self.horizontalScrollBar()
        if x < LABEL_W + margin:
            h.setValue(int(h.value() + x - LABEL_W - margin))
        elif x > self.viewport().width() - margin:
            h.setValue(int(h.value() + x - self.viewport().width() + margin))

    # -- playhead and selection ----------------------------------------

    @property
    def playhead(self) -> float:
        return self._playhead

    def set_playhead(self, t: float, follow: bool = True) -> None:
        self._playhead = t
        if follow:
            self.ensure_visible(t)
        self.viewport().update()

    @property
    def selection(self) -> Optional[CutSpan]:
        return self._selection

    def set_selection(self, span: Optional[CutSpan]) -> None:
        self._selection = span
        self.selection_changed.emit(span)
        self.viewport().update()

    @property
    def selected_item(self) -> Optional[LaneItem]:
        return self._selected

    # -- painting -------------------------------------------------------

    def paintEvent(self, _ev) -> None:
        p = QPainter(self.viewport())
        p.fillRect(self.viewport().rect(), theme.c(theme.BG))
        if not self._cs:
            p.setPen(QColor(theme.DIM))
            p.setFont(theme.ui_font(10))
            p.drawText(self.viewport().rect(), Qt.AlignCenter,
                       "Open a cutscene to see its timeline")
            return

        vw, vh = self.viewport().width(), self.viewport().height()
        time_rect = QRect(LABEL_W, RULER_H, vw - LABEL_W, vh - RULER_H)

        p.save()
        p.setClipRect(time_rect)
        self._paint_waveform(p)
        self._paint_lanes(p)
        # over the rows, not under them. Painting the cut band first was the
        # whole reason it read as faint: every row then drew back over it at
        # full strength, leaving a wash that had to compete with the tracker
        # instead of sitting on top of it.
        self._paint_cuts(p, time_rect)
        self._paint_drag(p, time_rect)
        self._paint_selection(p, time_rect)
        p.restore()

        self._paint_gutter(p)
        self._paint_ruler(p)
        self._paint_playhead(p)

    # ruler ------------------------------------------------------------

    _TICK_STEPS = [0.04, 0.1, 0.25, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300]

    def _ruler_step_seconds(self) -> float:
        for s in self._TICK_STEPS:
            if s * self._px_per_sec >= 64:
                return s
        return self._TICK_STEPS[-1]

    def _paint_ruler(self, p: QPainter) -> None:
        vw = self.viewport().width()
        band = QRectF(LABEL_W, 0, vw - LABEL_W, RULER_H)
        p.fillRect(band, theme.c(theme.PANEL))
        p.setPen(QPen(QColor("#000000"), 1))
        p.drawLine(QPointF(LABEL_W, RULER_H - 0.5), QPointF(vw, RULER_H - 0.5))

        cs = self._cs
        step_s = self._ruler_step_seconds()
        step_t = step_s * self._ticks_per_sec
        first = max(0.0, self.tick_at(LABEL_W))
        last = min(cs.total, self.tick_at(vw))
        n0 = int(first // step_t)
        n1 = int(last // step_t) + 1

        p.setFont(theme.ui_font(8))
        p.setClipRect(QRectF(LABEL_W, 0, vw - LABEL_W, RULER_H))
        for n in range(n0, n1 + 1):
            t = n * step_t
            x = self.x_of(t)
            p.setPen(QPen(theme.c(theme.GRID), 1))
            p.drawLine(QPointF(x, RULER_H - 7), QPointF(x, RULER_H))
            p.setPen(QColor(theme.DIM))
            p.drawText(QRectF(x + 3, 2, 90, 14), Qt.AlignLeft | Qt.AlignVCenter,
                       cs.time.format(t))

        # cuts, repeated as a solid strip along the foot of the ruler. Zoomed
        # in far enough to work on a join, the band itself can fill the screen
        # or sit entirely off it; this is the one place the whole edit stays
        # visible at a glance.
        for span in self._edits.cuts:
            x0 = max(float(LABEL_W), self.x_of(span.a))
            x1 = min(float(vw), self.x_of(span.b))
            if x1 <= x0:
                continue
            p.fillRect(QRectF(x0, RULER_H - 4, x1 - x0, 4), theme.c(theme.CUT))
        p.setClipping(False)

    # gutter -----------------------------------------------------------

    def _lane_colour(self, lane: Lane) -> QColor:
        """A row belonging to one speaker wears that character's colour.

        Same key the stage pins use, so a dialogue row and the pin above it
        agree about who is talking. Every other row keeps its family colour.
        """
        if lane.who:
            return theme.c(theme.character_color(lane.who)).darker(135)
        return theme.c(theme.LANE_COLOR.get(lane.cls, "#555a6d"))

    def _paint_gutter(self, p: QPainter) -> None:
        vh = self.viewport().height()
        g = QRectF(0, 0, LABEL_W, vh)
        p.fillRect(g, theme.c(theme.PANEL))
        p.setPen(QPen(QColor("#000000"), 1))
        p.drawLine(QPointF(LABEL_W - 0.5, 0), QPointF(LABEL_W - 0.5, vh))

        p.setClipRect(QRectF(0, RULER_H, LABEL_W, vh - RULER_H))
        p.setFont(theme.ui_font(8))
        fm = QFontMetrics(p.font())

        if self._wave:
            wy = RULER_H + TOP_PAD - self.verticalScrollBar().value()
            p.fillRect(QRectF(6, wy + WAVE_H / 2 - 4, 8, 8), theme.c(theme.ACCENT))
            p.setPen(QColor(theme.TEXT))
            p.drawText(QRectF(20, wy, LABEL_W - 26, WAVE_H - LANE_GAP),
                       Qt.AlignLeft | Qt.AlignVCenter, "Audio (scene mix)")

        for i, lane in enumerate(self._lanes):
            y = self._row_y(i)
            if y + LANE_H < RULER_H or y > vh:
                continue
            swatch = QRectF(6, y + LANE_H / 2 - 4, 8, 8)
            p.fillRect(swatch, self._lane_colour(lane))
            p.setPen(QColor(theme.TEXT))
            text = fm.elidedText(lane.label, Qt.ElideRight, LABEL_W - 28)
            p.drawText(QRectF(20, y, LABEL_W - 26, LANE_H),
                       Qt.AlignLeft | Qt.AlignVCenter, text)
        p.setClipping(False)

    # lanes ------------------------------------------------------------

    def _visible_slice(self, lane: Lane, t0: float, t1: float) -> Tuple[int, int]:
        """Indices of items that can intersect [t0, t1].

        Items are sorted by start, so the right edge is a binary search; the
        left edge steps back a little to catch a long block that started before
        the window. Camera cuts and shots can be minutes long, hence the walk.
        """
        starts = self._starts.get(lane.id) or []
        hi = bisect_right(starts, t1)
        lo = bisect_left(starts, t0)
        back = 0
        while lo > 0 and back < 64:
            lo -= 1
            back += 1
            if lane.items[lo].range[1] < t0:
                break
        return lo, hi

    def _paint_waveform(self, p: QPainter) -> None:
        """The scene mix, one peak per pixel column, mirrored about the centre.

        Peaks are reduced by maximum rather than sampled, so a transient never
        vanishes because the zoom stepped over it - the whole point is to see
        the frame a sound starts on.
        """
        wave = self._wave
        if not wave or not self._cs:
            return
        vw = self.viewport().width()
        top = RULER_H + TOP_PAD - self.verticalScrollBar().value()
        if top + WAVE_H < RULER_H or top > self.viewport().height():
            return

        band = QRectF(LABEL_W, top, vw - LABEL_W, WAVE_H - LANE_GAP)
        p.fillRect(band, theme.c(theme.STAGE_BG))

        columns = int(band.width())
        if columns <= 0:
            return
        tps = self._ticks_per_sec
        start_s = self.tick_at(LABEL_W) / tps
        end_s = self.tick_at(vw) / tps
        peaks = wave.slice_for(start_s, end_s, columns)

        mid = band.center().y()
        half = band.height() / 2 - 2
        p.setPen(QPen(theme.c(theme.ACCENT, 0.75), 1))
        for i, v in enumerate(peaks):
            if v <= 0:
                continue
            h = v / 255.0 * half
            x = band.left() + i + 0.5
            p.drawLine(QPointF(x, mid - h), QPointF(x, mid + h))

        p.setPen(QPen(theme.c(theme.GRID), 1))
        p.drawLine(QPointF(band.left(), mid), QPointF(band.right(), mid))

    def _paint_lanes(self, p: QPainter) -> None:
        vw, vh = self.viewport().width(), self.viewport().height()
        t0 = self.tick_at(LABEL_W)
        t1 = self.tick_at(vw)
        p.setFont(theme.ui_font(8))
        fm = QFontMetrics(p.font())

        for i, lane in enumerate(self._lanes):
            y = self._row_y(i)
            if y + LANE_H < RULER_H or y > vh:
                continue
            p.fillRect(QRectF(LABEL_W, y, vw - LABEL_W, LANE_H),
                       theme.c(theme.PANEL, 0.45))

            lane_base = self._lane_colour(lane)
            check_killed = bool(self._edits.killed) and lane.kind in ("cue", "vfx", "subtitle")
            lo, hi = self._visible_slice(lane, t0, t1)
            for item in lane.items[lo:hi]:
                x0 = self.x_of(item.range[0])
                x1 = self.x_of(item.range[1])
                w = max(2.0, x1 - x0)
                if x0 > vw or x0 + w < LABEL_W:
                    continue
                r = QRectF(x0, y, w, LANE_H)

                # the silenced tail of a trimmed voice line, drawn as a ghost
                if item.voice and item.voice.kept < item.voice.full:
                    gx = self.x_of(
                        item.voice.start + item.voice.full * self._ticks_per_sec
                    )
                    ghost = QRectF(x1, y + 4, max(1.0, gx - x1), LANE_H - 8)
                    p.fillRect(ghost, theme.c(theme.LANE_COLOR["vo"], 0.22))

                base = (
                    theme.c(theme.character_color(item.who)).darker(135)
                    if item.who
                    else lane_base
                )
                killed = check_killed and self._is_killed(item)
                if killed:
                    base = theme.c(theme.LANE_COLOR["del"])

                selected = item is self._selected
                p.fillRect(r, base if not selected else base.lighter(150))
                p.setPen(QPen(theme.c(theme.SEL) if selected else base.darker(160), 1))
                p.drawRect(r.adjusted(0.5, 0.5, -0.5, -0.5))

                if killed:
                    # struck out rather than removed: an off cue is still there,
                    # and clicking it again switches it back on
                    p.setPen(QPen(theme.c(theme.TEXT, 0.8), 1))
                    mid_y = r.center().y()
                    p.drawLine(QPointF(r.left() + 2, mid_y), QPointF(r.right() - 2, mid_y))

                if w > 26 and item.name:
                    p.setPen(theme.c(theme.TEXT, 0.55) if killed else QColor(theme.TEXT))
                    p.drawText(
                        r.adjusted(4, 0, -3, 0),
                        Qt.AlignLeft | Qt.AlignVCenter,
                        fm.elidedText(item.name, Qt.ElideRight, int(w) - 7),
                    )

            if lane.ticks:
                self._paint_key_ticks(p, lane, y, t0, t1, vw)

    def _is_killed(self, item: LaneItem) -> bool:
        d = cue_descriptor(item)
        k = cue_key(d)
        return bool(k and k in self._edits.killed)

    def _paint_key_ticks(self, p: QPainter, lane: Lane, y: float,
                         t0: float, t1: float, vw: float) -> None:
        """Key times as marks along the bottom of the row.

        Ticks are data, not items: an actor's transform track can carry over a
        thousand keys, and a thousand LaneItems would cost hit-testing and
        memory for blocks nobody clicks. Marks cull by binary search and merge
        when denser than a pixel, so a fully-baked track reads as a solid strip
        - which is itself the information: no gap for a join to land in.
        """
        ticks = lane.ticks
        lo = bisect_left(ticks, t0)
        hi = bisect_right(ticks, t1)
        if lo >= hi:
            return
        p.setPen(QPen(theme.c(theme.KEY_MARK, 0.8), 1))
        top = y + LANE_H - 6
        bottom = y + LANE_H - 1
        last_px = -10.0
        for t in ticks[lo:hi]:
            x = self.x_of(t)
            if x - last_px < 1.0:
                continue   # denser than a pixel: one mark is the truth of it
            last_px = x
            p.drawLine(QPointF(x, top), QPointF(x, bottom))

    # cuts and selection ------------------------------------------------

    #: Gap between deletion stripes, and their width, in pixels.
    #:
    #: Tuned against a wide band at high zoom, which is the hard case: heavy
    #: enough there and you can no longer read the cues you are deleting, which
    #: defeats the point of drawing them at all.
    HATCH_PITCH = 11.0
    HATCH_WIDTH = 2.5

    def _hatch(self, p: QPainter, r: QRectF, colour: QColor,
               pitch: float, width: float, backslash: bool = False) -> None:
        """Fill `r` with 45° stripes, anchored to the timeline rather than the
        window.

        Anchoring is the fiddly part and the reason this is not `BDiagPattern`.
        Qt's built-in hatch brushes are 8×8 device-pixel tiles pinned to the
        widget, so the stripes crawl across the band as you scroll and go to
        mush at any real stripe weight. These are drawn against content
        coordinates, so a stripe stays on the same frame of the scene while the
        view moves under it, and the weight is ours to choose.

        `backslash` leans them the other way, which is how a band that is being
        KEPT is told apart from one being removed without relying on colour.
        """
        p.save()
        p.setClipRect(r, Qt.IntersectClip)
        pen = QPen(colour, width)
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        h = r.height()
        scroll = self.horizontalScrollBar().value()
        # a stripe crosses the band over `h` pixels of x, so start that far left
        first = r.left() + scroll - h
        cx = first - (first % pitch)          # snap to the content-space grid
        while cx - scroll < r.right():
            x = cx - scroll
            if backslash:
                p.drawLine(QPointF(x, r.top()), QPointF(x + h, r.bottom()))
            else:
                p.drawLine(QPointF(x, r.bottom()), QPointF(x + h, r.top()))
            cx += pitch
        p.restore()

    def _paint_cuts(self, p: QPainter, clip: QRect) -> None:
        """The ranges marked for deletion, drawn over the rows they remove.

        Four things stack up, and each carries a different piece of the meaning:
        the footage inside is knocked back so it reads as already gone, the red
        tint says why, the stripes make the band unmistakable at any zoom even
        where it covers a busy row, and the hard edges mark exactly which frames
        the join will land between.
        """
        if not self._edits.cuts:
            return
        cs = self._cs
        knock_back = QColor(0, 0, 0, 96)
        tint = theme.c(theme.CUT, 0.13)
        stripe = theme.c(theme.CUT, 0.42)
        edge = QPen(theme.c(theme.CUT), 2)
        p.setFont(theme.ui_font(8, bold=True))
        fm = QFontMetrics(p.font())

        for span in self._edits.cuts:
            x0 = self.x_of(span.a)
            x1 = self.x_of(span.b)
            if x1 < clip.left() or x0 > clip.right():
                continue
            r = QRectF(x0, clip.top(), max(1.0, x1 - x0), clip.height())
            p.fillRect(r, knock_back)
            p.fillRect(r, tint)
            self._hatch(p, r, stripe, self.HATCH_PITCH, self.HATCH_WIDTH)
            p.setPen(edge)
            p.drawLine(QPointF(x0, clip.top()), QPointF(x0, clip.bottom()))
            p.drawLine(QPointF(x1, clip.top()), QPointF(x1, clip.bottom()))

            # what the cut costs, on a plate so it stays readable over stripes
            if cs is None or r.width() < 64:
                continue
            text = "−%s" % cs.time.describe_span(span.b - span.a)
            tw = fm.horizontalAdvance(text) + 12
            if tw > r.width() - 8:
                continue
            plate = QRectF(r.center().x() - tw / 2, clip.top() + 6, tw, 17)
            p.fillRect(plate, QColor(0, 0, 0, 205))
            p.setPen(QPen(theme.c(theme.CUT), 1))
            p.drawRect(plate.adjusted(0.5, 0.5, -0.5, -0.5))
            p.drawText(plate, Qt.AlignCenter, text)

    # -- cues moved, by hand or by the collapse pass ----------------------
    #
    # Nothing is painted for a relocated cue any more, and that is the point:
    # `lanes.apply_moves` and `lanes.apply_relocations` put the block itself at
    # the tick it will fire on, so the tracker shows the result rather than an
    # annotation describing it. The ghost, the dotted connector and the
    # "4.83s from end" plate were three marks saying what one block in the
    # right place says on its own, and at any real zoom they crossed half the
    # rows to say it.
    #
    # What replaced them, rather than nothing: the block's own position, the
    # toolbar's collapse summary, and the details pane, which names the
    # authored tick and how far the cue has come.

    def _lane_row(self, lane: Lane) -> Optional[float]:
        for i, ln in enumerate(self._lanes):
            if ln is lane or ln.id == lane.id:
                y = self._row_y(i)
                return y if RULER_H - LANE_H < y < self.viewport().height() else None
        return None

    def _paint_drag(self, p: QPainter, clip: QRect) -> None:
        """The block under the pointer, at the tick it would land on.

        This one mark stays, because until the mouse comes up nothing has been
        committed and the real block has not moved yet - so without it the drag
        has no feedback at all. It is not a connector: it sits on its own row,
        it is the same size and colour as the block it stands for, and it goes
        away on release when the block itself takes that position.

        When a neighbour is holding the drag back the copy turns the cut
        colour. The block stops following the mouse at that point, and without
        a change of state that reads as the widget having lost track of it.
        """
        d = self._drag
        if d is None or self._press is None or d.empty or self._cs is None:
            return
        _start, _tick, item, lane = self._press
        y = self._lane_row(lane)
        if y is None:
            return
        origin = item.moved_from if item.moved_from is not None else item.range[0]
        width = item.range[1] - item.range[0]
        x0 = self.x_of(origin + d.delta)
        x1 = self.x_of(origin + d.delta + width)
        if x1 < clip.left() or x0 > clip.right():
            return
        base = theme.c(theme.CUT if d.clamped
                       else theme.LANE_COLOR.get(lane.cls, theme.SEL))
        r = QRectF(x0, y, max(2.0, x1 - x0), LANE_H)
        p.fillRect(r, QColor(base.red(), base.green(), base.blue(), 205))
        p.setPen(QPen(theme.c(theme.SEL), 1))
        p.drawRect(r.adjusted(0.5, 0.5, -0.5, -0.5))

        # how far, on a plate, so it stays readable over whatever is behind it
        p.setFont(theme.ui_font(8, bold=True))
        fm = QFontMetrics(p.font())
        text = "%s%s" % ("+" if d.delta > 0 else "−",
                         self._cs.time.describe_span(abs(d.delta)))
        tw = fm.horizontalAdvance(text) + 10
        plate = QRectF(x0 + 4, y - 17, tw, 15)
        p.fillRect(plate, QColor(0, 0, 0, 205))
        p.setPen(QPen(theme.c(theme.CUT if d.clamped else theme.SEL), 1))
        p.drawRect(plate.adjusted(0.5, 0.5, -0.5, -0.5))
        p.drawText(plate, Qt.AlignCenter, text)

    def _paint_selection(self, p: QPainter, clip: QRect) -> None:
        s = self._selection
        if not s or s.b <= s.a:
            return
        x0 = self.x_of(s.a)
        x1 = self.x_of(s.b)
        r = QRectF(x0, clip.top(), max(1.0, x1 - x0), clip.height())
        p.fillRect(r, theme.c(theme.SEL, 0.13))
        p.setPen(QPen(theme.c(theme.SEL), 1))
        p.drawLine(QPointF(x0, clip.top()), QPointF(x0, clip.bottom()))
        p.drawLine(QPointF(x1, clip.top()), QPointF(x1, clip.bottom()))

    def _paint_playhead(self, p: QPainter) -> None:
        x = self.x_of(self._playhead)
        if x < LABEL_W - 1 or x > self.viewport().width():
            return
        p.setPen(QPen(theme.c(theme.PLAY), 1))
        p.drawLine(QPointF(x, 0), QPointF(x, self.viewport().height()))
        p.setBrush(QBrush(theme.c(theme.PLAY)))
        p.setPen(Qt.NoPen)
        p.drawRect(QRectF(x - 3, 0, 6, 7))

    # -- interaction ----------------------------------------------------

    def _lane_at(self, y: int) -> Optional[Tuple[int, Lane]]:
        off = self.verticalScrollBar().value()
        idx = int((y - RULER_H - TOP_PAD - self._wave_h + off) // ROW_PITCH)
        if 0 <= idx < len(self._lanes):
            return idx, self._lanes[idx]
        return None

    def _items_at(self, pos: QPoint) -> Tuple[List[LaneItem], Optional[Lane]]:
        """Every block under the pointer, the one drawn on top first."""
        found = self._lane_at(pos.y())
        if not found:
            return [], None
        _idx, lane = found
        t = self.tick_at(pos.x())
        slack = 3 / max(1e-9, self._px_per_tick())
        return [item for item in reversed(lane.items)
                if item.range[0] - slack <= t <= item.range[1] + slack], lane

    def _item_at(self, pos: QPoint) -> Tuple[Optional[LaneItem], Optional[Lane]]:
        """The block a click means, cycling through a pile on repeated clicks.

        Cues are instantaneous and drawn as a quarter-second sliver, so two on
        the same frame land on exactly the same pixels: the one drawn last
        covers the other completely and, walking the row from the top, this
        used to return that same one every time. The buried cue could not be
        clicked, so it could not be switched off, and nothing on screen said it
        was there — EV_CORLE_0100 shipped with one flower lei still attached
        for exactly that reason.

        Clicking again now steps to the next block in the pile and round-trips
        back to the first, the way a stack of overlapping objects behaves in a
        drawing program. `stack_hit` tells the window how deep the pile is so
        it can say so.
        """
        hits, lane = self._items_at(pos)
        if not hits:
            return None, lane
        # identity, not equality: `LaneItem` is a plain dataclass, and two cues
        # that happen to carry the same payload compare equal
        index = 0
        for i, item in enumerate(hits):
            if item is self._selected:
                index = (i + 1) % len(hits)
                break
        self.stack_hit.emit(index, len(hits))
        return hits[index], lane

    def mousePressEvent(self, ev) -> None:
        """Left button: **Shift** sweeps out a range, plain drags a cue.

        The two gestures used to be one - any press that was not on a
        structural block started a range sweep, including a press on the very
        SE you wanted to nudge. Putting the sweep behind Shift is what frees a
        plain drag to mean "move this", and it is the modifier already used for
        the coarse versions of things (`Shift+arrow`, `Shift+Del`).
        """
        if not self._cs:
            return
        pos = ev.position().toPoint()
        if pos.x() < LABEL_W:
            return
        if pos.y() < RULER_H:
            self._scrubbing = True
            self._scrub_to(pos.x())
            return
        if ev.button() != Qt.LeftButton:
            return

        if ev.modifiers() & Qt.ShiftModifier:
            self._drag_from = self.tick_at(pos.x())
            return

        item, lane = self._item_at(pos)
        self._selected = item
        self.item_selected.emit(item, lane)
        if item is not None and lane is not None and lane.range_row:
            self.set_selection(CutSpan(item.range[0], item.range[1]))
        elif item is not None and lane is not None and can_move(lane, item):
            # armed, not yet dragging - a click has to stay a click
            self._press = (pos, self.tick_at(pos.x()), item, lane)
        self.viewport().update()

    def contextMenuEvent(self, ev) -> None:
        """Right-click selects the block under the pointer, then asks the window.

        Selecting first matters: every action the menu offers acts on the
        selected cue, and a menu that acted on a different block from the one
        highlighted would be the worst kind of surprise.

        Which is also why this does not cycle through a pile the way a left
        click does: having clicked down to the buried cue, right-clicking it
        has to mean *that* one, not the next one along.
        """
        if not self._cs:
            return
        pos = ev.pos()
        if pos.x() < LABEL_W or pos.y() < RULER_H:
            return
        hits, lane = self._items_at(pos)
        item = next((i for i in hits if i is self._selected), hits[0] if hits else None)
        if item is not None:
            self._selected = item
            self.item_selected.emit(item, lane)
            self.viewport().update()
        self.context_requested.emit(item, lane, ev.globalPos())

    def mouseMoveEvent(self, ev) -> None:
        pos = ev.position().toPoint()
        if self._scrubbing:
            self._scrub_to(pos.x())
            return
        if not (ev.buttons() & Qt.LeftButton):
            return
        if self._drag_from is not None:
            t = self.tick_at(pos.x())
            a, b = sorted((self._drag_from, t))
            if b - a > 1:
                self.set_selection(CutSpan(a, b))
            return
        if self._press is not None:
            self._drag_to(pos, bool(ev.modifiers() & Qt.AltModifier))

    def _drag_to(self, pos: QPoint, free: bool) -> None:
        """Update the live proposal for the cue under the pointer.

        `free` (Alt) turns snapping off and leaves the frame grid, for the
        occasional cue that has to sit between two things the snap would prefer.
        """
        start, start_tick, item, lane = self._press
        if self._drag is None and abs(pos.x() - start.x()) < DRAG_THRESHOLD_PX:
            return
        wanted = self.tick_at(pos.x()) - start_tick
        index = self._arrays
        if index is None:
            return
        self._drag = drag_core.propose(
            self._cs, self._edits, index, lane, item, wanted, snap=not free
        )
        self.cue_drag_preview.emit(self._drag)
        self.viewport().update()

    def mouseReleaseEvent(self, _ev) -> None:
        if self._drag is not None:
            if not self._drag.empty:
                self.cue_dragged.emit(self._drag)
            self.cue_drag_preview.emit(None)
        self._drag = None
        self._press = None
        self._scrubbing = False
        self._drag_from = None

    def _scrub_to(self, x: float) -> None:
        cs = self._cs
        if not cs:
            return
        t = max(0.0, min(cs.total, self.tick_at(x)))
        self._playhead = t
        self.playhead_moved.emit(t)
        self.viewport().update()

    def wheelEvent(self, ev) -> None:
        delta = ev.angleDelta().y()
        mods = ev.modifiers()
        if mods & Qt.ControlModifier:
            self.zoom_by(1.25 if delta > 0 else 1 / 1.25, ev.position().x())
            ev.accept()
            return
        if mods & Qt.ShiftModifier:
            h = self.horizontalScrollBar()
            h.setValue(h.value() - delta)
            ev.accept()
            return
        super().wheelEvent(ev)
