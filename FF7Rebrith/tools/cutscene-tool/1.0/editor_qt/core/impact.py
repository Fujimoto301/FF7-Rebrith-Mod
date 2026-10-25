"""
What a proposed cut would cost.

This is the analysis behind the warning bar and behind `impact` in the edit
plan. It is pure so it can be unit-tested against known scenes - the warnings
are the only thing standing between a plausible-looking selection and a
softlock, so they need to be right.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .edits import CutSpan
from .timeline import Cutscene


@dataclass
class CutImpact:
    #: actors (or voice names) whose lines the cut touches at all
    lines: List[str] = field(default_factory=list)
    #: SendStateTrigger IDs removed - the game uses these to advance
    triggers: List[str] = field(default_factory=list)
    #: Jump / StoryJump clips removed
    jumps: List[str] = field(default_factory=list)
    #: camera cuts wholly inside the selection
    cuts: int = 0
    #: a line the cut starts or ends in the middle of
    mid_line: Optional[str] = None
    #: ticks of dialogue that will play on over the following footage
    overrun: float = 0.0
    #: subtitles whose "off" event is cut but whose "on" survives - left on screen
    stranded: List[str] = field(default_factory=list)
    #: lipsync lines split by the cut
    lip_split: int = 0


def impact_of(cs: Cutscene, a: float, b: float) -> CutImpact:
    """Voice is fired by Clip_Voice, an *instantaneous* event with no duration
    and no stop cue, so the clip always plays to its natural end. Cutting into a
    line does not shorten it - the audio simply runs on over whatever follows.
    """
    ticks = cs.time.ticks_per_second
    hit = CutImpact()

    for v in cs.voice:
        s = v.tick
        e = v.tick + (v.duration or 1) * ticks
        if e > a and s < b:
            hit.lines.append(v.actor or v.name)
            if s < a:
                # line starts before the cut and runs into it
                hit.mid_line = v.actor or v.name
                hit.overrun = max(hit.overrun, min(e, b) - a)
            elif e > b:
                # cut starts mid-line
                hit.mid_line = v.actor or v.name

    # a subtitle left on screen: its "off" event is inside the cut, its "on" isn't
    for r in cs.subtitles:
        if a < r.end <= b and r.start < a:
            hit.stranded.append(r.actor or r.label)

    for ln in cs.lipsync:
        if not ln.frames:
            continue
        s = ln.frames[0][0]
        e = ln.frames[-1][1]
        if e > a and s < b and (s < a or e > b):
            hit.lip_split += 1

    for key in ("PlannerEvent", "CutEvent"):
        for e in cs.events(key):
            t = e["tick"]
            if t < a or t >= b:
                continue
            if e.get("clip") == "SendStateTrigger":
                v = (e.get("props") or {}).get("TriggerID", [])
                hit.triggers.append(
                    ",".join(str(x) for x in (v if isinstance(v, list) else [v]))
                )
            if e.get("clip") in ("Jump", "StoryJump"):
                hit.jumps.append(e["clip"])

    hit.cuts = sum(1 for c in cs.cuts if c.range[0] >= a and c.range[1] <= b)
    return hit


def make_safe(cs: Cutscene, a: float, b: float) -> Optional[CutSpan]:
    """Pull a selection's edges inward until it splits no voice line and strands
    no subtitle.

    Returns None when there is no safe cut in that region at all - which is the
    correct answer for a selection sitting inside one line, not a failure.

    The frame snap happens first: doing it afterwards could clip a line the
    shrink pass had already cleared.
    """
    ticks = cs.time.ticks_per_second
    a = cs.time.ceil_to_frame(a)
    b = cs.time.floor_to_frame(b)

    for _ in range(8):
        moved = False
        for v in cs.voice:
            s = v.tick
            e = v.tick + (v.duration or 1) * ticks
            if e > a and s < b:
                if s < a < e <= b:
                    a = e  # trailing audio from a line that starts before the cut
                    moved = True
                elif a <= s < b and e > b:
                    b = s  # leading audio of a line that runs past the cut
                    moved = True
                elif s < a and e > b:
                    a = b = 0  # the whole selection sits inside one line
                    moved = True
        for r in cs.subtitles:
            if a < r.end <= b and r.start < a:
                a = r.end
                moved = True
        if not moved:
            break

    return CutSpan(a, b) if b > a else None


def snap_tick(
    cs: Cutscene,
    cuts: Sequence[CutSpan],
    t: float,
    tolerance: float,
    enabled: bool = True,
) -> float:
    """Snap a tick to whatever matters nearby, in priority order: camera-cut
    boundaries, voice starts and ends, edges of existing cuts, then the frame
    grid. `tolerance` is in ticks (the caller converts from pixels).
    """
    ticks = cs.time.ticks_per_second
    clamped = min(max(t, 0), cs.total)
    if not enabled:
        return cs.time.snap_to_frame(clamped)

    best: Optional[float] = None
    best_dist = tolerance

    def consider(v: float) -> None:
        nonlocal best, best_dist
        d = abs(v - clamped)
        if d < best_dist:
            best_dist = d
            best = v

    for c in cs.cuts:
        consider(c.range[0])
        consider(c.range[1])
    for v in cs.voice:
        consider(v.tick)
        consider(v.tick + (v.duration or 1) * ticks)
    for x in cuts:
        consider(x.a)
        consider(x.b)

    return best if best is not None else cs.time.snap_to_frame(clamped)
