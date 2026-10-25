"""
Time units.

A cutscene carries three clocks and mixing them is the classic bug here:
sequencer *ticks* (24000/s), display *frames* (30fps => 800 ticks each), and
*seconds* for audio and for anything shown to a human. The plan format speaks
ticks; the audio player speaks seconds; snapping and warnings speak frames.

TypeScript branded these so a Seconds could never be passed where a Tick
belongs. Python cannot enforce that at runtime, so the discipline here is:
every conversion goes through a TimeBase, which is read from the cutscene's own
metadata rather than assumed, and nothing else divides by 24000 by hand.

Rounding note: JavaScript's Math.round is half-up; Python's round() is
half-to-even. Every rounding in this port goes through `round_half_up` so a
tick landing exactly between two frames snaps the same way it did in v3.
"""

from __future__ import annotations

import math
from typing import NewType, Sequence, Tuple

Tick = NewType("Tick", float)
Frame = NewType("Frame", int)
Seconds = NewType("Seconds", float)

#: Half-open [start, end) in ticks - the same convention the engine uses.
TickRange = Tuple[float, float]

DEFAULT_TICK_RESOLUTION = 24000
DEFAULT_DISPLAY_RATE = 30


def round_half_up(x: float) -> int:
    """JavaScript Math.round: ties go toward positive infinity."""
    return math.floor(x + 0.5)


def make_range(a: float, b: float) -> TickRange:
    return (a, b)


def range_length(r: TickRange) -> float:
    return r[1] - r[0]


def range_contains(r: TickRange, t: float) -> bool:
    return r[0] <= t < r[1]


def ranges_overlap(a: TickRange, b: TickRange) -> bool:
    return a[1] > b[0] and a[0] < b[1]


def clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


class TimeBase:
    """Ticks, frames and seconds, and the only sanctioned way between them."""

    __slots__ = ("ticks_per_second", "fps", "ticks_per_frame")

    def __init__(
        self,
        tick_resolution: float | None = None,
        display_rate: float | None = None,
    ) -> None:
        self.ticks_per_second: float = tick_resolution or DEFAULT_TICK_RESOLUTION
        self.fps: float = display_rate or DEFAULT_DISPLAY_RATE
        #: ticks in one display frame (800). Every authored boundary is a multiple.
        self.ticks_per_frame: float = self.ticks_per_second / self.fps

    # -- conversions ----------------------------------------------------

    def to_seconds(self, t: float) -> float:
        return t / self.ticks_per_second

    def to_ticks(self, s: float) -> float:
        return s * self.ticks_per_second

    def to_frame(self, t: float) -> int:
        return round_half_up(t / self.ticks_per_frame)

    def frame_to_tick(self, f: float) -> float:
        return f * self.ticks_per_frame

    # -- the frame grid -------------------------------------------------

    def snap_to_frame(self, t: float) -> float:
        """Nearest frame boundary. Cuts must land on one or the patcher's key
        correction has nothing to write to."""
        return round_half_up(t / self.ticks_per_frame) * self.ticks_per_frame

    def ceil_to_frame(self, t: float) -> float:
        """Frame boundary at or after `t` - for pulling a selection edge inward."""
        return math.ceil(t / self.ticks_per_frame) * self.ticks_per_frame

    def floor_to_frame(self, t: float) -> float:
        """Frame boundary at or before `t`."""
        return math.floor(t / self.ticks_per_frame) * self.ticks_per_frame

    def is_frame_aligned(self, t: float) -> bool:
        return t % self.ticks_per_frame == 0

    # -- for humans -----------------------------------------------------

    def format(self, t: float) -> str:
        """`m:ss.hh`, the form used throughout the UI."""
        s = max(0.0, t) / self.ticks_per_second
        m = int(s // 60)
        return "%d:%05.2f" % (m, s - m * 60)

    def describe_span(self, t: float) -> str:
        """`4.17s - 125f` - what a cut costs, in both currencies."""
        return "%.2fs · %df" % (
            t / self.ticks_per_second,
            round_half_up(t / self.ticks_per_frame),
        )


def clamp_tick(t: float, lo: float, hi: float) -> float:
    return clamp(t, lo, hi)


def parse_range(raw: Sequence | None) -> TickRange | None:
    """Ranges arrive as `[lower, upper, "Inclusive", "Exclusive"]`."""
    if raw and len(raw) >= 2:
        return (raw[0], raw[1])
    return None
