"""
How far a cue may be dragged, and what stops it.

The short version
-----------------
A cue fires at an int32 tick held in an **event Times array**, and the patcher
moves a cue by rewriting that int32 in place. The arrays are read as *sorted* -
`patcher.compiled_event_blocks` finds them by that property and the engine's
own lookup depends on it - so `patcher.check_relocation_order` drops any move
that would leave one out of order.

For the cues relocation was built for that never mattered. Measured on
EV_FOREE_8510, `_CutEvent` holds 46 cues across 42 arrays: fades and streaming
commands sit alone, and a lone entry cannot be unsorted. The cues we now let
people drag are the opposite shape:

===========  =====  ======  =====================
sub-sequence  cues  arrays  sizes
===========  =====  ======  =====================
_Sound          38       2  19, 19
_Voice          10       2  5, 5
_Text           20       2  10, 10
_ManualSE       48      12  1-8
_CutEvent       46      42  mostly 1
===========  =====  ======  =====================

(Each array appears twice: once in the section export and once in the compiled
template. `relocation_offsets` matches by payload and moves both, which is
required - the compiled copy is what a shipping build evaluates.)

So an SE, voice or music cue **can slide freely between its neighbours in the
same array, and cannot cross them.** The gaps are not small - on 8510's
19-entry `_Sound` array they run 0.63s to 9.53s - but they are real, and the
editor has to say so while the mouse is down. Letting the drag look successful
and having the build quietly drop it is the exact failure the rest of this tool
is written to avoid.

Reordering would mean rewriting the payload blocks into a different order, not
just their times: the blocks sit in the same order as the array and are
variable-size, so nothing can be swapped in place. That is a separate question
from this one, and it is not answered here.

Where the limits come from
--------------------------
Preferably from the assets themselves, which is exact. `compiled_event_blocks`
needs only the raw bytes - no .usmap - so this works whenever `--content` is
configured, and costs one small read per sub-sequence (10-40 KB).

Without Content, the fallback groups a sub-sequence's cues by tick order alone,
as though they shared one array. That is **conservative, never permissive**: a
real file has the same cues split across more arrays, so the fallback can only
ever forbid a move the assets would have allowed. A drag that is refused is
visible and arguable; one that is allowed and then dropped at build time is
not.
"""

from __future__ import annotations

import os
import sys
from bisect import bisect_left
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

#: The tool modules (patcher, zenasset, transforms) live beside editor_qt.
_TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOL_DIR not in sys.path:
    sys.path.insert(0, _TOOL_DIR)

#: Sub-sequences whose cues can be dragged, and the asset suffix each lives in.
DRAGGABLE_SEQS: Tuple[str, ...] = ("Sound", "ManualSE", "Voice", "Text")

#: Sub-sequences the automatic rescue in `collapse.py` moves cues within. It is
#: under the same constraint - a rescued cue cannot cross its array neighbours -
#: and until this index covered these seqs it had no way to know. Counted over
#: all 755 extracted scenes, every cue of a `RELOCATABLE_CLIPS` type lives in
#: one of three sub-sequences:
#:
#: ============  ====================================  ====
#: sub-sequence  clips found there                     cues
#: ============  ====================================  ====
#: CutEvent      Fade, MovieControl, both streaming     793
#: Light         SwitchStreamingVolume, ShowHide...     453
#: PlannerEvent  ShowHideStreamingLevels, Fade            5
#: ============  ====================================  ====
#:
#: `_Light_Low` is absent because it mirrors `_Light` array for array; the plan
#: carries one entry per cue and `relocation_offsets` applies it to both.
RELOCATABLE_SEQS: Tuple[str, ...] = ("CutEvent", "Light", "PlannerEvent")

#: Everything worth reading. Indexing a sub-sequence nothing asks about costs
#: one small read and answers nothing, so the two lists are simply unioned.
INDEXED_SEQS: Tuple[str, ...] = DRAGGABLE_SEQS + RELOCATABLE_SEQS


@dataclass(frozen=True)
class Limits:
    """The open interval a cue may be dragged within, in original ticks.

    `lo`/`hi` are the neighbouring cues' ticks - exclusive bounds. `exact` says
    whether these came from the asset's real arrays or from the conservative
    fallback, so the UI can be honest about which it is enforcing.
    """

    lo: float
    hi: float
    lo_label: str = ""
    hi_label: str = ""
    exact: bool = True

    def clamp(self, t: float, margin: float) -> float:
        """`t` pulled inside the interval, keeping `margin` off each neighbour.

        A cue landing exactly on its neighbour's tick leaves the array sorted -
        `check_relocation_order` allows equal - but two cues on one tick fire
        together and whichever the engine honours last is what you get. One
        frame of daylight is cheap and removes the question.
        """
        lo = self.lo + margin if self.lo > float("-inf") else float("-inf")
        hi = self.hi - margin if self.hi < float("inf") else float("inf")
        if lo > hi:
            # No room between the two neighbours - only possible when both are
            # real, so the midpoint is a real tick. Substituting `t` for an
            # unbounded side instead of an infinity was a bug: it made `lo > hi`
            # fire on a cue with nothing in front of it, and the "midpoint" of
            # an infinity came back as an infinity.
            return (self.lo + self.hi) / 2
        return min(max(t, lo), hi)

    def blocked_at(self, t: float, margin: float) -> str:
        """Which neighbour is stopping the drag here, if either is."""
        if self.lo > float("-inf") and t <= self.lo + margin:
            return self.lo_label
        if self.hi < float("inf") and t >= self.hi - margin:
            return self.hi_label
        return ""


class ArrayIndex:
    """Times-array membership for one cutscene's event cues.

    `limits(seq, tick)` is the only thing the UI needs: everything else is
    bookkeeping to answer it.
    """

    def __init__(self, exact: bool = True) -> None:
        #: (seq) -> list of sorted tick lists, one per Times array
        self._arrays: Dict[str, List[List[float]]] = {}
        #: (seq, tick) -> the array it belongs to
        self._of: Dict[Tuple[str, float], List[float]] = {}
        self.exact = exact

    def add_array(self, seq: str, ticks: Sequence[float]) -> None:
        arr = sorted(ticks)
        if not arr:
            return
        self._arrays.setdefault(seq, []).append(arr)
        for t in arr:
            # A tick appearing in two arrays of one sub-sequence would make
            # membership ambiguous; the narrower neighbourhood is the safe
            # answer, so keep whichever array constrains it more tightly.
            key = (seq, float(t))
            prev = self._of.get(key)
            if prev is None or _span_around(arr, t) < _span_around(prev, t):
                self._of[key] = arr

    def limits(self, seq: str, tick: float,
               labels: Optional[Dict[float, str]] = None) -> Limits:
        arr = self._of.get((seq, float(tick)))
        if arr is None:
            # A cue we cannot place in an array is one we cannot prove is safe
            # to move. Say so by refusing rather than by guessing.
            return Limits(tick, tick, "an array we could not read",
                          "an array we could not read", self.exact)
        i = bisect_left(arr, tick)
        lo = arr[i - 1] if i > 0 else float("-inf")
        hi = arr[i + 1] if i + 1 < len(arr) else float("inf")
        name = labels or {}
        return Limits(
            lo, hi,
            name.get(lo, "the cue before it") if lo > float("-inf") else "",
            name.get(hi, "the cue after it") if hi < float("inf") else "",
            self.exact,
        )

    def known(self, seq: str, tick: float) -> bool:
        return (seq, float(tick)) in self._of

    def arrays_for(self, seq: str) -> List[List[float]]:
        """Every Times array in one sub-sequence, each sorted.

        `limits` answers about one cue; this answers about the whole
        constraint, which is what a test has to check to show that the
        editor's rule and `patcher.check_relocation_order` agree.
        """
        return [list(a) for a in self._arrays.get(seq, [])]

    @property
    def empty(self) -> bool:
        return not self._arrays


def _span_around(arr: Sequence[float], t: float) -> float:
    i = bisect_left(arr, t)
    lo = arr[i - 1] if i > 0 else float("-inf")
    hi = arr[i + 1] if i + 1 < len(arr) else float("inf")
    if lo == float("-inf") or hi == float("inf"):
        return float("inf")
    return hi - lo


def find_ev_dir(content: str, area: Optional[str], ev: str) -> Optional[str]:
    """The scene's asset folder, by area if we know it and by search if not."""
    root = os.path.join(content, "Cut", "Game")
    if area:
        p = os.path.join(root, area, ev)
        if os.path.isdir(p):
            return p
    if not os.path.isdir(root):
        return None
    for a in os.listdir(root):
        p = os.path.join(root, a, ev)
        if os.path.isdir(p):
            return p
    return None


def load(content: Optional[str], area: Optional[str], ev: str, total: float,
         seqs: Sequence[str] = INDEXED_SEQS) -> Optional[ArrayIndex]:
    """Read the real Times arrays out of the scene's assets.

    None when Content is not configured or the folder is missing - the caller
    falls back to `from_events`. An asset that will not parse is skipped
    individually rather than failing the whole index: one unreadable
    sub-sequence should cost that sub-sequence's drags, not every drag.
    """
    if not content:
        return None
    ev_dir = find_ev_dir(content, area, ev)
    if not ev_dir:
        return None
    try:
        import patcher
    except Exception:
        return None

    index = ArrayIndex(exact=True)
    for seq in seqs:
        path = os.path.join(ev_dir, "%s_%s.uasset" % (ev, seq))
        if not os.path.exists(path):
            continue
        try:
            with open(path, "rb") as fh:
                data = fh.read()
            blocks = patcher.compiled_event_blocks(data, total)
        except Exception:
            continue
        for arr in _group_by_array(blocks):
            index.add_array(seq, arr)
    return None if index.empty else index


def _group_by_array(blocks: Sequence[Tuple[int, int, int, int]]) -> List[List[float]]:
    """Split `(time_offset, tick, pos, size)` blocks into their Times arrays.

    Entries of one array are consecutive int32s, so they sit exactly 4 bytes
    apart - the same rule `patcher.check_relocation_order` groups by, and it
    has to stay the same rule or the editor would enforce a different
    constraint from the one the build applies.
    """
    out: List[List[float]] = []
    cur: List[float] = []
    last_off: Optional[int] = None
    for toff, tick, _pos, _size in sorted(blocks, key=lambda b: b[0]):
        if last_off is not None and toff - last_off != 4:
            out.append(cur)
            cur = []
        cur.append(float(tick))
        last_off = toff
    if cur:
        out.append(cur)
    return out


def from_events(cs, seqs: Sequence[str] = INDEXED_SEQS) -> ArrayIndex:
    """The conservative fallback: treat each sub-sequence as one array.

    Over-constrains on purpose. `_ManualSE` really holds a dozen arrays, so
    this will refuse some moves the assets would take - but it can never allow
    one they would refuse, and a visible refusal beats a move that disappears
    during the build.
    """
    index = ArrayIndex(exact=False)
    events = (cs.data.get("events") or {})
    for seq in seqs:
        ticks = [
            e["tick"] for e in (events.get(seq) or [])
            if isinstance(e, dict) and e.get("tick") is not None
        ]
        if ticks:
            index.add_array(seq, ticks)
    return index


def for_scene(cs, content: Optional[str] = None) -> ArrayIndex:
    """The best index available for this scene: exact if we can, safe if not."""
    exact = load(content, cs.area, cs.name, cs.total)
    return exact if exact is not None else from_events(cs)
