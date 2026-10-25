"""
Fades and level streaming keep their place at the end of a cut.

The problem
-----------
A ripple cut that reaches the end of a scene throws away the last things the
scene does, and those are usually the ones you least want to lose:

* the **fade to black** the scene ends on. Without it the edit ends on a hard
  frame, mid-shot.
* the **level streaming** commands - `SwitchStreamingVolume` and
  `ShowHideStreamingLevels` - that preload the sky, lighting and sub-levels the
  *next* scene needs, and the state they leave the world in. Drop them and the
  next scene starts on assets that never loaded.

What this does
--------------
It depends on **where the cut ends**, and getting that wrong was a real bug -
see "Two kinds of cut" below.

A cut that runs off the **end of the scene** moves its cues into the surviving
footage keeping the exact spacing they had:

    original   ...====[ last shot ]====|
                      P1    F      P2  |end
    drawn cut  ...=========|xxxxxxxxxxx|
    built      ...=========|
                    P1  F  P2          <- same gaps, measured back from the
                                          new end instead of the old one

Each cue lands the same distance from the **new** end that it had from the old
one. That is a single rigid translation of the whole group - by the length of
the cut - so a `Preload` keeps exactly its authored head start over the
`SwitchToPreloaded` that consumes it, and a fade that finished on the last
frame still finishes on the last frame. Nothing is appended, and the footage
you cut stays cut.

An **interior** cut fires its cues at the join instead. See below.

Two kinds of cut
----------------
Distance-from-the-end is the right thing to preserve only when the cut reaches
the end, because that is what anchors the thing being preserved: the fade has
to land on the last frame, the preload has to keep its lead into the *next
scene*. For a cut in the middle of a scene nothing is anchored to the end. The
cue simply has to still happen, and the first surviving instant is the join.

This distinction was missing, and the arithmetic hid it. The old rule was::

    target = tick - length - removed_before          # == join - (b - tick)

which preserves the distance from `b`, the end of the **cut**, not the end of
the **scene**. Those two are the same number exactly when `b == cs.total`, and
the only two scenes anyone had cut that way were EV_FOREE_7500 and
EV_FOREE_8510 - so every relocation the feature had ever produced was correct
by coincidence, and the interior path had never once run.

On an interior cut it translated the inside of the cut onto the footage
*before* the join, dropping a cue back by up to the whole length of the cut:

    EV_FOREE_8514, cut [49.97s, 76.07s), join at 49.97s
        cue at 50.00s  ->  23.90s     26.07s before the join
        cue at 75.83s  ->  49.73s      0.23s before the join

- and when the cut was longer than everything before it the result went
negative and the cue was thrown away as "nowhere left of the join to put it",
which was the formula's own defect wearing a reason.

The guard that should have caught it could not: `if target > join` is
unreachable, because `target - join == tick - b` and `tick < b` is the loop
condition. It was written against the docstring's rule, not the code's.

Why moving the tick is enough
-----------------------------
The engine schedules from the baked evaluation field, so the fear is that
moving a cue's tick moves the cue but not its slot in the schedule. Measured
across 16 scenes, over both `_Light` and `_CutEvent`:

===========================================================  ====
event ticks that are a field boundary AND another section's    49
event ticks that are a field boundary and nothing else          0
event ticks that are not a field boundary at all               31
===========================================================  ====

**Zero.** No event tick anywhere introduces a field boundary of its own, so the
field is never refined by an event section - the ones that coincide do so
because cues are authored on the same beats as the lighting and shot changes
that *do* refine it. These sections span whole ranges; the tick alone decides
when the event fires.

`patcher.SILENCE_KEYS` is the same fact from the other direction: voice and SE
cues have to be renamed when a cut swallows them precisely because, collapsed
onto the join, they *do* fire.

Everything here is pure. The UI draws its result, the plan carries it, and
`patcher.relocation_offsets` writes it - one int32 per copy, in place.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .edits import CutSpan, EditState, normalise_cuts, to_edited, to_original
from .timeline import Cutscene
from .units import TickRange

#: Clip types that are moved rather than lost, and why each one matters.
RELOCATABLE_CLIPS: Tuple[str, ...] = (
    "Fade",
    "SwitchStreamingVolume",
    "ShowHideStreamingLevels",
    "MovieControl",
)

CLIP_REASON = {
    "Fade": "the scene's fade to black",
    "SwitchStreamingVolume": "preloads the sky/lighting volume the next scene needs",
    "ShowHideStreamingLevels": "shows or hides a streaming sub-level",
    "MovieControl": "hands off to a pre-rendered movie",
}

#: What to call each family where there is no room for its clip name.
SHORT_NAME = {
    "Fade": "fade",
    "SwitchStreamingVolume": "streaming",
    "ShowHideStreamingLevels": "streaming",
    "MovieControl": "movie",
}


def short_names(clips: Sequence[str]) -> str:
    """'streaming' rather than 'SwitchStreamingVolume, ShowHideStreamingLevels'."""
    seen: List[str] = []
    for c in clips:
        n = SHORT_NAME.get(c, c)
        if n not in seen:
            seen.append(n)
    return ", ".join(seen)


#: Payload keys that identify a cue to the patcher. Not a name to break - an
#: identity to match, so the right one of two fades in a scene is moved.
IDENTITY_KEYS: Tuple[str, ...] = (
    "From", "To", "Frame", "White",
    "VolumeLabel", "SwitchLabel", "SwitchType",
    "Labels", "Hidden", "WithoutCollision",
    "TargetName", "MovieName",
)


@dataclass(frozen=True)
class Relocation:
    """One cue moved, by rewriting the int32 tick in its event Times array."""

    #: sub-sequence it lives in, e.g. "CutEvent", "Light"
    seq: str
    #: Clip_* type without the prefix
    clip: str
    #: where it fires in the untouched scene, in ORIGINAL ticks
    tick: float
    #: where it will fire, in EDITED ticks - i.e. on the finished timeline with
    #: every cut closed up. Written into the asset verbatim: the patcher places
    #: relocated cues rather than remapping them, so what the editor decided is
    #: exactly what the game gets.
    new_tick: float
    #: the same moment in ORIGINAL ticks, which is the space the timeline view
    #: draws in. Obtained by inverting the remap, NOT by adding up every cut
    #: before it - a cue that lands ahead of an earlier cut must not have that
    #: cut's length added, or it is drawn inside a red band and reads as though
    #: the edit will swallow it. Always in surviving footage.
    at_tick: float = 0.0
    #: distance from the end of the EDITED scene once it has moved - the number
    #: that actually matters, and for a cue inside a cut it comes out equal to
    #: the distance it had from the old end
    from_end: float = 0.0
    #: why it moved, for the plan and the details pane
    why: str = ""
    #: payload fields that identify this cue among others of its type
    match: Dict[str, Any] = field(default_factory=dict)
    label: str = ""

    @property
    def moved_by(self) -> float:
        return self.tick - self.new_tick


@dataclass(frozen=True)
class Lost:
    """A cue that could not be moved, and why. Never silent."""

    clip: str
    tick: float
    label: str
    reason: str


@dataclass(frozen=True)
class CollapsePlan:
    #: cuts as they will be applied. Unchanged from what was drawn - this
    #: feature never edits the cut, it only moves cues out of it.
    cuts: Tuple[CutSpan, ...] = ()
    relocations: Tuple[Relocation, ...] = ()
    lost: Tuple[Lost, ...] = ()

    def is_empty(self) -> bool:
        return not self.relocations and not self.lost

    def relocation_at(self, seq: str, tick: float) -> Optional[Relocation]:
        for r in self.relocations:
            if r.seq == seq and r.tick == tick:
                return r
        return None


# -- reading the scene ---------------------------------------------------


def relocatable_cues(
    cs: Cutscene, clips: Sequence[str] = RELOCATABLE_CLIPS
) -> List[Dict[str, Any]]:
    """Every fade / streaming / movie cue in the scene, sorted by tick."""
    wanted = set(clips)
    out: List[Dict[str, Any]] = []
    for seq, group in (cs.data.get("events") or {}).items():
        for e in group or []:
            if not isinstance(e, dict) or e.get("tick") is None:
                continue
            if e.get("clip") in wanted:
                out.append({"seq": seq, "clip": e["clip"], "tick": e["tick"],
                            "props": e.get("props") or {}})
    out.sort(key=lambda e: e["tick"])
    return out


def unreadable_cues(
    cs: Cutscene, clips: Sequence[str] = RELOCATABLE_CLIPS
) -> List[Dict[str, Any]]:
    """Relocatable cues whose tick the extractor could not read.

    `payload_events` locates an event's Times array by searching backwards for
    `[N][N ascending ticks][N]` and rejecting any candidate with a tick outside
    the scene's playback range. One out-of-range tick rejects the **whole**
    array, so every cue sharing it comes back with `tick: None` - five of them
    in EV_FOREE_8512, whose array is `[0, 912800, 1282400, 5672000, 5828000]`
    against a playback end of 1282400.

    A cue with no tick cannot be tested against a cut, so it can neither be
    carried nor be shown to be safe. Dropping it silently - which is what
    filtering it out of `relocatable_cues` did - makes an unknown look like an
    absence, and the plan then reports `lostCues: []` while being blind. They
    are reported instead, so the plan says what it does not know.
    """
    wanted = set(clips)
    out: List[Dict[str, Any]] = []
    for seq, group in (cs.data.get("events") or {}).items():
        for e in group or []:
            if not isinstance(e, dict) or e.get("clip") not in wanted:
                continue
            if e.get("tick") is None:
                out.append({"seq": seq, "clip": e["clip"], "tick": None,
                            "props": e.get("props") or {}})
    return out


def _identity(props: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in IDENTITY_KEYS:
        if k in props:
            v = props[k]
            out[k] = list(v) if isinstance(v, (list, tuple)) else v
    return out


def is_preload(e: Dict[str, Any]) -> bool:
    """A streaming command that only *loads*, and shows nothing.

    `Preload` brings a volume's levels into memory; the matching
    `SwitchToPreloaded` is what puts them on screen. So a Preload can be fired
    as early as we like - it costs memory and nothing else - while moving a
    switch would change the sky in front of the player.
    """
    if e["clip"] != "SwitchStreamingVolume":
        return False
    return str((e["props"] or {}).get("SwitchType", "")).endswith("Preload")


def _join_of(spans: Sequence[CutSpan], t: float) -> float:
    """Where a tick inside a cut ends up when nothing carries it: the join."""
    removed = 0.0
    for span in spans:
        if span.a <= t < span.b:
            return span.a - removed
        removed += span.b - span.a
    return t - removed


def _array_floor(index, all_cuts: EditState, spans: Sequence[CutSpan],
                 e: Dict[str, Any],
                 placed: Dict[Tuple[str, float], float]) -> Optional[float]:
    """The earliest tick this cue may be given, or None if we cannot say.

    A cue fires at an int32 in a shared, **sorted** `Times` array, and
    `patcher.check_relocation_order` drops any move that would unsort one - so
    a rescue that lands before the entry in front of it is not a rescue, it is
    a move the build will refuse. It refuses correctly and says so, but the
    planner never heard: the plan still claimed the cue would be at a tick it
    was never going to reach, the timeline drew it there, and
    `build_mod.verify` then failed a build whose bytes were fine. EV_GRASE_2280
    is the scene that showed it - `Sky_Grass` is hidden at 0, shown at 1466400
    and hidden again at 1760800, all three in one array, and a 24.1s tail cut
    asked for that last hide at 389600, in front of its own show.

    Answered from `arrays.ArrayIndex`, which reads the real arrays out of the
    assets, and **only when they are the real ones**: the conservative fallback
    treats a whole sub-sequence as one array, which here would not merely
    over-constrain a gesture the user can see refused - it would silently stop
    a swallowed cue landing where the cut says it should, which is the
    guarantee this module exists for. No index, or an inexact one, means no
    floor and exactly the behaviour that shipped.

    The neighbour's own edited tick is what bounds us, not its authored one:
    it may itself have been carried (read it back out of `placed`), it may have
    survived (`to_edited`), or it may be a cue nothing carries that sits inside
    a cut - in which case the patcher remaps it onto the join, and that is the
    number this cue has to clear.
    """
    if index is None or not getattr(index, "exact", False):
        return None
    seq, tick = e["seq"], float(e["tick"])
    if not index.known(seq, tick):
        return None                 # not in an array we could read: no claim
    lo = index.limits(seq, tick).lo
    if lo == float("-inf"):
        return None                 # first in its array, nothing in front
    key = (seq, float(lo))
    if key in placed:
        return placed[key]
    natural = to_edited(all_cuts, lo)
    return natural if natural is not None else _join_of(spans, lo)


def label_of(e: Dict[str, Any]) -> str:
    p = e["props"]
    clip = e["clip"]
    if clip == "Fade":
        return "fade %s→%s%s" % (p.get("From"), p.get("To"),
                                 " (white)" if p.get("White") else "")
    if clip == "SwitchStreamingVolume":
        kind = str(p.get("SwitchType") or "").rsplit("::", 1)[-1]
        return "%s → %s%s" % (p.get("VolumeLabel"), p.get("SwitchLabel"),
                              " (%s)" % kind if kind else "")
    if clip == "ShowHideStreamingLevels":
        labels = p.get("Labels")
        names = ", ".join(
            str(x) for x in (labels if isinstance(labels, list) else [labels])
        )
        return "%s %s" % (names, "hide" if p.get("Hidden") else "show")
    return clip


# -- the plan ------------------------------------------------------------


def plan_collapse(
    cs: Cutscene,
    cuts: Sequence[CutSpan],
    enabled: bool = True,
    clips: Sequence[str] = RELOCATABLE_CLIPS,
    restore_preload_lead: bool = False,
    index: Any = None,
) -> CollapsePlan:
    """Where each swallowed fade / streaming command goes.

    A cut that reaches the **end of the scene** measures back from the new end:

        new_tick = new_total - (cs.total - tick)

    so the group keeps its internal spacing exactly and each cue keeps its
    distance from the end - a fade that finished on the last frame still
    finishes on the last frame, a preload keeps its authored lead into the
    scene that consumes it.

    An **interior** cut puts the cue on the join. Distance-from-the-end means
    nothing here: the scene carries on afterwards, and the cue's job is simply
    to still happen. The join is the first surviving instant, so that is where
    it goes. (This is what the old `tick - length - removed_before` was getting
    wrong; see the module docstring.)

    Deliberately NOT snapped to the frame grid. Cue ticks are not all frame
    aligned to begin with - `EV_FOREE_8510`'s sky preload sits at 1079328, 128
    ticks off a frame - and snapping would shift a cue by up to a frame and
    break the exact spacing this is here to preserve. Cuts are snapped because
    the key correction needs a frame to write to; a cue tick is just a number.

    `restore_preload_lead` is the separate, opt-in heuristic for preloads the
    cuts never touched. It is off by default and is *not* part of rescuing a
    swallowed cue - see the second loop.

    `index` is an `arrays.ArrayIndex`. Given one read from the assets, no cue is
    ever placed in front of its own Times-array neighbour - see `_array_floor`
    for why that is a real constraint and not a precaution. Without one the
    result is exactly what it was before the index existed.
    """
    spans = normalise_cuts(cuts)
    if not spans or not enabled:
        return CollapsePlan(cuts=spans)

    #: cues we cannot place because we cannot read their tick. Reported, never
    #: dropped: an unknown must not be allowed to look like an absence.
    blind = [
        Lost(e["clip"], float("nan"), label_of(e),
             "the extractor could not read this cue's tick, so it cannot be "
             "tested against the cuts - one out-of-range entry rejects a whole "
             "Times array")
        for e in unreadable_cues(cs, clips)
    ]

    cues = relocatable_cues(cs, clips)
    if not cues:
        return CollapsePlan(cuts=spans, lost=tuple(blind))

    #: the whole set, so a cue's drawn position can be worked out against every
    #: cut rather than only the ones before it
    all_cuts = EditState(cuts=spans)
    new_total = cs.total - sum(x.b - x.a for x in spans)
    relocations: List[Relocation] = []
    lost: List[Lost] = list(blind)

    # -- 1. cues the cuts swallow ---------------------------------------------
    #
    # Two rules, because there are two kinds of cut and only one of them has an
    # end to measure from.
    removed_before = 0.0
    inside_target: Dict[int, float] = {}
    inside_why: Dict[int, str] = {}
    #: the join of the cut that swallowed each cue, kept so that a rescue which
    #: turns out to be illegal has somewhere legal to fall back to
    inside_join: Dict[int, float] = {}
    for span in spans:
        length = span.b - span.a
        #: the join, on the edited timeline. Nothing may land after it.
        join = span.a - removed_before
        #: does this cut run off the end of the scene? Only then is the cue's
        #: distance from the end a real quantity worth preserving.
        to_the_end = span.b >= cs.total
        for i, e in enumerate(cues):
            t = e["tick"]
            if not (span.a <= t < span.b):
                continue
            if to_the_end:
                target = round(new_total - (cs.total - t))
                why = ("carried back with the cut, keeping its distance from "
                       "the end")
                if target < 0:
                    # The edited scene is shorter than the lead this cue had.
                    # A Preload only costs memory, so firing it at the top of
                    # the scene is strictly better than losing it; anything
                    # that puts something on screen is not ours to reschedule.
                    if is_preload(e):
                        target, why = 0.0, (
                            "issued at the start of the scene: the edit is "
                            "shorter than the lead it was authored with")
                    else:
                        lost.append(Lost(
                            e["clip"], t, label_of(e),
                            "the edited scene is shorter than the distance "
                            "this cue had from the end, so there is nowhere "
                            "to put it",
                        ))
                        continue
            else:
                # Interior cut. Nothing anchors this cue to the end of the
                # scene - the scene carries on. Fire it where playback resumes.
                target = join
                why = ("fired at the join: the cut that swallowed it is "
                       "interior, so nothing anchors it to the end")
            if target > join:
                target = join
            inside_target[i] = target
            inside_why[i] = why
            inside_join[i] = join
        removed_before += length

    # -- 1b. a Preload must never land on top of its own switch ---------------
    #
    # Putting interior cues on the join is right for each cue on its own, and
    # wrong for a pair. One cut can swallow a `Preload` and the
    # `SwitchToPreloaded` that consumes it, and sending both to the join fires
    # the switch with nothing loaded - the volume flips to a level that is not
    # resident, which is a missing sky or, worse, a missing light rig.
    #
    # Only the Preload moves. It puts nothing on screen, so it is free to be
    # early; the switch is what the player sees and stays where it landed. The
    # authored gap between them is what gets restored, floored at the join
    # before it so a request is never issued in footage already left behind.
    joins: List[float] = []
    _r = 0.0
    for span in spans:
        joins.append(span.a - _r)
        _r += span.b - span.a
    by_vol: Dict[Any, List[int]] = {}
    for i, e in enumerate(cues):
        if e["clip"] == "SwitchStreamingVolume":
            by_vol.setdefault((e["props"] or {}).get("VolumeLabel"), []).append(i)
    for idxs in by_vol.values():
        for n, i in enumerate(idxs):
            if i not in inside_target or not is_preload(cues[i]):
                continue
            for j in idxs[n + 1:]:
                if is_preload(cues[j]):
                    break                      # a later Preload, not a consumer
                if inside_target.get(j) != inside_target[i]:
                    break                      # its switch is elsewhere already
                gap = cues[j]["tick"] - cues[i]["tick"]
                earlier = [x for x in joins if x < inside_target[i]]
                floor_j = max(earlier) if earlier else 0.0
                inside_target[i] = max(inside_target[i] - gap, floor_j, 0.0)
                inside_why[i] = (
                    "pulled back off the join so the switch that consumes it "
                    "keeps the lead the scene authored")
                break

    # -- 2. every cue in order, so nothing overtakes its neighbour -----------
    #
    # A Preload that SURVIVES can still be worse off than the game intended:
    # cuts after it eat into the lead it was given, and cuts before it can
    # leave a join moments earlier, so the engine is still streaming the jump
    # when the request lands. Both are addressed by firing it sooner - which
    # costs nothing, because a Preload puts nothing on screen. A
    # `SwitchToPreloaded` does, and is never moved.
    #
    # The floor keeps streaming cues in order, so a Preload can never be pulled
    # back past a switch that consumes it. It is kept **per volume**: that pair
    # is the only thing that genuinely interacts, and a floor held across
    # unrelated cues would stop a swallowed one landing exactly where the cut
    # says it should - which is the guarantee this whole thing is for.
    floors: Dict[str, float] = {}
    #: where each cue this loop has already settled will actually fire, so the
    #: array floor below can be read off a decision rather than re-derived
    placed: Dict[Tuple[str, float], float] = {}
    for i, e in enumerate(cues):
        t = e["tick"]
        natural = to_edited(all_cuts, t)
        vol = (e["props"] or {}).get("VolumeLabel") \
            if e["clip"] == "SwitchStreamingVolume" else None
        floor = floors.get(vol, 0.0) if vol else 0.0

        if i in inside_target:
            target = max(inside_target[i], floor)
            why = inside_why[i]
            #: the entry in front of this one in its own Times array, which the
            #: built asset will not let it overtake
            bound = _array_floor(index, all_cuts, spans, e, placed)
            if bound is not None and target < bound:
                if is_preload(e):
                    # Free to be early, so put it as early as the array allows
                    # and keep the rescue.
                    target = bound
                    why = (why + "; held at the cue in front of it in its "
                                 "Times array")
                else:
                    # It puts something on screen, so early is worse than late:
                    # a hide landing on its own show is the sky gone for the
                    # rest of the scene. The join is where the patcher would
                    # have put it anyway once `check_relocation_order` refused
                    # the move, and it is always at or after the bound.
                    target = max(inside_join.get(i, bound), bound)
                    why = ("fired at the join: keeping its distance from the "
                           "end would have put it before the cue in front of "
                           "it in its Times array")
        elif natural is None:
            continue                        # inside a cut and already reported
        elif not is_preload(e) or not restore_preload_lead:
            # Not swallowed. Rescuing a cue the cut destroyed is one feature;
            # re-timing one it never touched is a different, speculative one,
            # and welding them to a single switch is what forced EV_FOREE_7512
            # to run with *no* protection in order to stop the second.
            if vol:
                floors[vol] = natural       # stays put, but still holds the line
            placed[(e["seq"], float(t))] = natural
            continue
        else:
            #: what the scene originally gave it to load in
            want = min(natural, new_total - (cs.total - t))
            why = "cuts after it had eaten into its loading time" if want < natural else ""
            # The last place the edit jumped before this cue. A join is a hard
            # relocation for the streaming system, so a request issued just
            # after one is competing with the whole jump for bandwidth - which
            # is how a preload with its full authored lead can still miss.
            #
            # "Just after" measured against the lead itself: if the join is
            # nearer than the time the scene gives the sky to load, it is
            # inside the load window and worth getting ahead of. A cut an age
            # earlier is not - pulling back to that would fire the request in a
            # part of the scene the player left long ago, for no gain.
            before = [x for x in spans if x.b <= t]
            #: earliest it may ever go: never past the cue in front of it, and
            #: never back across the jump *before* the one we are dodging - a
            #: request issued in a part of the scene the player has already
            #: left buys nothing and could fight the current scene's own sky
            lo = floor
            if before:
                last = before[-1]
                j = last.a - sum(x.b - x.a for x in spans if x.b <= last.a)
                if j < want and (want - j) < (new_total - want):
                    # The join is inside the load window. Get AHEAD of it: the
                    # whole complaint is that a request landing on the far side
                    # of a jump competes with the jump for bandwidth, and
                    # issuing it *at* the join is issuing it into the jump -
                    # nought seconds after, the worst instant available.
                    #
                    # The old code could not express this. It set `want = j`
                    # and then floored at `j` too, so `max(want, lo)` was
                    # always exactly `j`: the rule had one possible answer and
                    # it was the one it existed to avoid.
                    #
                    # A jump's cost scales with the footage it skips, so that
                    # is the margin: be ahead of the join by the length of the
                    # cut being taken.
                    want = j - (last.b - last.a)
                    why = ("issued ahead of the join: it was inside the "
                           "window the sky needs to load in")
                    #: floor moves back one jump, so there is room to be early
                    earlier = [x for x in spans if x.b <= last.a]
                    if earlier:
                        prev = earlier[-1]
                        lo = max(lo, prev.a - sum(
                            x.b - x.a for x in spans if x.b <= prev.a))
                else:
                    lo = max(lo, j)
            target = max(round(want), lo, 0.0)
            if why and target > want:
                why += " (as far back as it can go)"
            #: a surviving preload may not be pulled back past its own array
            #: neighbour either - same rule, different reason for moving
            bound = _array_floor(index, all_cuts, spans, e, placed)
            if bound is not None and target < bound:
                target = max(bound, 0.0)
                why = (why + "; held at the cue in front of it in its Times "
                             "array") if why else ""
            if target >= natural:
                if vol:
                    floors[vol] = natural
                placed[(e["seq"], float(t))] = natural
                continue                    # already as early as it can be

        # everything reaching here has somewhere new to be
        relocations.append(Relocation(
            seq=e["seq"],
            clip=e["clip"],
            tick=t,
            new_tick=target,
            at_tick=to_original(all_cuts, target),
            from_end=new_total - target,
            why=why,
            match=_identity(e["props"]),
            label=label_of(e),
        ))
        if vol:
            floors[vol] = target
        placed[(e["seq"], float(t))] = target

    return CollapsePlan(cuts=spans, relocations=tuple(relocations),
                        lost=tuple(lost))


def plan_moves(cs: Cutscene, state: EditState) -> Tuple[List[Relocation], List[Lost]]:
    """The cues the user has dragged, as relocations the patcher can carry out.

    A hand move is authored in ORIGINAL ticks - the space the timeline draws in
    - and the plan wants EDITED ticks, so `to_edited` does the conversion here
    rather than at drag time. That ordering is the whole reason a move survives
    later editing: drag a cue, then cut somewhere ahead of it, and the cue is
    still at the same moment of the footage it was put on.

    Two things can go wrong, and both are reported rather than swallowed:

    * the destination is inside a cut - the user put it somewhere that no
      longer exists, usually by cutting after dragging;
    * the cue's authored tick is inside a cut *and* the destination is too,
      which is the same thing said twice but reads more clearly.

    Note there is no check here that the move keeps its Times array sorted.
    That belongs at the point of the gesture - `core.arrays` clamps the drag so
    an unsortable move cannot be authored in the first place - and
    `patcher.check_relocation_order` is the backstop that catches a plan
    hand-edited or written by an older build.
    """
    out: List[Relocation] = []
    lost: List[Lost] = []
    if not state.moves:
        return out, lost

    new_total = cs.total - sum(x.b - x.a for x in state.cuts)
    for move in sorted(state.moves.values(), key=lambda m: m.tick):
        edited = to_edited(state, move.new_tick)
        if edited is None:
            lost.append(Lost(
                move.clip, move.tick, move.label or move.clip,
                "it was moved to %s, which a later cut removed - drag it "
                "somewhere that survives, or restore that cut"
                % cs.time.format(move.new_tick),
            ))
            continue
        out.append(Relocation(
            seq=move.seq,
            clip=move.clip,
            tick=move.tick,
            new_tick=edited,
            at_tick=move.new_tick,
            from_end=new_total - edited,
            why="moved by hand, %s %s"
                % ("forward" if move.delta > 0 else "back",
                   cs.time.describe_span(abs(move.delta))),
            match=dict(move.match),
            label=move.label or move.clip,
        ))
    return out, lost


def effective(cs: Cutscene, state: EditState,
              index: Any = None) -> Tuple[EditState, CollapsePlan]:
    """The edits as they will be applied, and what is being carried across.

    The cuts themselves never change - this feature moves cues, it does not
    negotiate with the edit - so the state comes back as it went in. It returns
    a pair anyway because every caller wants the plan beside the state, and one
    function computing both is what stops the editor showing one thing and
    building another.

    Two sources of relocation meet here: the automatic rescue of fades and
    streaming commands a cut would swallow, and cues the user dragged. **A hand
    move wins.** In practice they barely overlap - the automatic pass only
    touches `RELOCATABLE_CLIPS`, and dragging is offered for SE, dialogue and
    music - but where they do, a person who moved something deliberately has
    said something the heuristic has not, and two entries for one cue would
    leave the patcher applying whichever it read last.
    """
    auto = plan_collapse(
        cs, state.cuts,
        enabled=state.collapse_to_end,
        restore_preload_lead=state.restore_preload_lead,
        index=index,
    )
    manual, lost = plan_moves(cs, state)
    if not manual and not lost:
        return state, auto

    claimed = {(r.seq, r.tick) for r in manual}
    kept = [r for r in auto.relocations if (r.seq, r.tick) not in claimed]
    return state, replace(
        auto,
        relocations=tuple(kept) + tuple(manual),
        lost=auto.lost + tuple(lost),
    )


# -- reporting -----------------------------------------------------------


def describe(cs: Cutscene, plan: CollapsePlan) -> Tuple[str, bool]:
    """`(line, loud)` for the toolbar. `loud` when something could not move."""
    bits: List[str] = []
    if plan.relocations:
        bits.append(
            "%d cue%s carried into surviving footage (%s)"
            % (
                len(plan.relocations),
                "" if len(plan.relocations) == 1 else "s",
                short_names([r.clip for r in plan.relocations]),
            )
        )
    if plan.lost:
        bits.append("%d could not be moved" % len(plan.lost))
    return " · ".join(bits), bool(plan.lost)
