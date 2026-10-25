"""
Turning a drag into a set of cue moves.

Pure: given the scene, the current edits, a Times-array index and the block
being dragged, this works out every cue that gesture should move, how far it is
actually allowed to go, and what stopped it. The widget does the mouse; this
does the meaning.

Two things make a drag more than "write a new tick".

**A line of dialogue is three cues, not one.** The Voice clip starts the audio,
and the subtitle is a separate on/off pair in `_Text`. Move the voice on its
own and the caption stays behind, which is not what dragging a line of dialogue
means. So the gesture collects the pair and moves all three by the same delta.
Lip sync needs nothing - the phoneme times in the LSD packs are relative to the
clip start, so the mouth follows the voice cue wherever it goes.

**A cue cannot cross its neighbours.** Cues share sorted Times arrays and the
patcher refuses any move that would unsort one - see `core.arrays`. With three
cues moving together the limit is the tightest of the three, so the delta is
clamped once, against the intersection, rather than each cue being clamped
separately into a shape the user did not ask for.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .arrays import ArrayIndex, Limits
from .cues import cue_descriptor, cue_key, event_cue_key, identity
from .edits import CueMove, EditState
from .impact import snap_tick
from .lanes import Lane, LaneItem, can_move
from .timeline import Cutscene

#: Daylight kept between a dragged cue and its neighbour, in frames.
#:
#: A cue landing exactly on its neighbour's tick leaves the array sorted, so
#: the patcher would accept it - but two cues on one tick fire together and
#: whichever the engine honours last is what you get. That is the same
#: ambiguity the silencing pass exists to avoid at a join, and it is not worth
#: reintroducing by hand for the sake of one frame.
NEIGHBOUR_MARGIN_FRAMES = 1


@dataclass
class Drag:
    """What a proposed drag would do.

    `moves` is empty when the gesture is a no-op - dragged back to where it
    started, or blocked before it could move at all - and the caller should not
    commit anything.
    """

    #: (cue key, move) pairs, ready for `edits.with_cue_moves`
    moves: List[Tuple[str, CueMove]] = field(default_factory=list)
    #: how far the block actually moved, in ticks, after snapping and clamping
    delta: float = 0.0
    #: how far the pointer asked it to move
    wanted: float = 0.0
    #: the cue that stopped it going further, if one did
    blocked_by: str = ""
    #: human summary for the status bar
    note: str = ""

    @property
    def clamped(self) -> bool:
        return bool(self.blocked_by) and self.delta != self.wanted

    @property
    def empty(self) -> bool:
        return not self.moves


def _text_events(cs: Cutscene, label: str) -> List[Dict[str, Any]]:
    """The `_Text` on/off pair for one subtitle label."""
    return [
        e for e in cs.events("Text")
        if str(((e.get("props") or {}).get("TextLabel") or "")) == label
    ]


def _companions(cs: Cutscene, item: LaneItem) -> List[Dict[str, Any]]:
    """Cues that have to travel with the one under the pointer.

    A Voice block brings its subtitle pair; a subtitle block brings its own
    *off* event, which has no block of its own because the row draws the pair
    as one range. Everything else travels alone.
    """
    props = item.props or {}
    if item.type == "Voice":
        name = str(props.get("VoiceName") or "")
        # the subtitle label is the voice name with a `$` in front - the same
        # relation `trimmed_subtitle_end` relies on
        return _text_events(cs, "$" + name) if name else []
    if item.type == "Subtitle":
        return _text_events(cs, str(props.get("label") or ""))
    return []


def _move_for_event(seq: str, e: Dict[str, Any]) -> Tuple[str, Dict[str, Any], str]:
    """`(cue key, match, clip)` for a raw event dict.

    The key comes from `cues.event_cue_key` rather than being spelled here, so
    a cue moved by a drag and the same cue found by the preview mixdown hash to
    the same string. Two spellings of one key is how a moved line would keep
    its old sound.
    """
    props = e.get("props") or {}
    return event_cue_key(seq, e) or "", identity(props), str(e.get("clip") or "")


def authored_key(item: LaneItem) -> Optional[str]:
    """The cue key for where the scene authors this block, not where it sits.

    A moved block is drawn at its new tick, so a descriptor taken straight off
    it hashes to that tick and finds nothing in `state.moves`. Everything that
    looks a move up has to ask for the authored tick, and doing it in one place
    is what stops the two spellings drifting apart.
    """
    d = cue_descriptor(item)
    if not d:
        return None
    if item.moved_from is not None:
        d = dict(d)
        d["tick"] = item.moved_from
    return cue_key(d)


def _parts(cs: Cutscene, item: LaneItem) -> List[Tuple[str, CueMove]]:
    """Every cue this gesture moves, at zero delta, ready to be shifted.

    The leader comes first and its key becomes the group id, so dragging any of
    them home later takes the whole gesture with it.

    A subtitle is built out of its `_Text` events rather than out of the block
    on screen. The block's payload is the derived `SubtitleRanges` record -
    label, start, end, text - which carries no `TextLabel`, so an identity
    taken from it would be empty and the patcher would match nothing. The two
    real events carry the field the game looks up.
    """
    out: List[Tuple[str, CueMove]] = []

    if item.type != "Subtitle":
        lead_key = authored_key(item)
        if not lead_key:
            return []
        authored = item.moved_from
        if authored is None:
            authored = item.tick_start if item.tick_start is not None else item.range[0]
        out.append((
            lead_key,
            CueMove(
                seq=item.seq or "",
                clip=item.clip or item.type,
                tick=authored,
                new_tick=authored,
                match=identity(item.props or {}),
                label=item.name or (item.clip or item.type),
            ),
        ))

    for e in _companions(cs, item):
        tick = e.get("tick")
        if tick is None:
            continue
        key, match, clip = _move_for_event("Text", e)
        if any(k == key for k, _m in out):
            continue
        enable = (e.get("props") or {}).get("Enable")
        out.append((
            key,
            CueMove(
                seq="Text",
                clip=clip or "SubTitle",
                tick=tick,
                new_tick=tick,
                match=match,
                label=(item.name if item.type == "Subtitle" and not out
                       else "subtitle %s" % ("on" if enable else "off")),
            ),
        ))

    if not out:
        return []
    lead_key = out[0][0]
    return [
        (k, m if k == lead_key else CueMove(
            seq=m.seq, clip=m.clip, tick=m.tick, new_tick=m.new_tick,
            match=m.match, label=m.label, group=lead_key))
        for k, m in out
    ]


def _limits_for(index: ArrayIndex, move: CueMove,
                labels: Optional[Dict[float, str]] = None) -> Limits:
    return index.limits(move.seq, move.tick, labels)


def propose(cs: Cutscene, state: EditState, index: ArrayIndex,
            lane: Lane, item: LaneItem, wanted_delta: float,
            snap: bool = True) -> Drag:
    """Work out what dragging `item` by `wanted_delta` ticks would do.

    Order matters and is deliberate:

    1. **snap the leader** to whatever is nearby - a shot boundary, a voice
       start, the edge of a cut, otherwise the frame grid. Snapping the delta
       instead would put the block a snapped distance from an unsnapped start,
       which is not what any of the marks on screen mean.
    2. **clamp the delta** against every moving cue's array neighbours at once.
       Clamping after snapping can leave the result off the grid by design: the
       neighbour is a real constraint and the grid is a convenience, and it is
       better to sit one tick inside a hard limit than one frame outside it.
    3. **apply the same delta to all of them**, so a line and its caption stay
       exactly as far apart as the scene wrote them.
    """
    if not can_move(lane, item):
        return Drag(note="that row cannot be dragged")

    parts = _parts(cs, item)
    if not parts:
        return Drag(note="this block carries no name the game looks up, so "
                         "there is nothing to move")

    lead_key, lead = parts[0]
    tolerance = cs.time.ticks_per_frame * 2

    # `wanted_delta` is how far the pointer travelled, so it is measured from
    # where the block is DRAWN - which is not the authored tick once the cue
    # has already been moved. Everything downstream works in deltas from the
    # authored tick, because that is what the plan stores and what the clamp
    # is expressed in, so the two bases are reconciled here and only here.
    # Getting this wrong made a second drag jump the block back to its
    # authored tick before applying the new offset.
    current = lead.tick + (state.moves[lead_key].delta if lead_key in state.moves else 0.0)
    target = current + wanted_delta
    if snap:
        target = snap_tick(cs, state.cuts, target, tolerance, True)
    else:
        target = cs.time.snap_to_frame(target)

    # Home is always reachable. A cue's authored tick need not be frame
    # aligned - EV_FOREE_8510's sky preload sits 128 ticks off one - so
    # without this, dragging a moved cue back would snap to the nearest frame
    # and stop a hair short of where it started, leaving an entry in the plan
    # that says "moved by 128 ticks" and reads as a bug.
    if abs(target - lead.tick) <= tolerance:
        target = lead.tick

    delta = target - lead.tick
    wanted_delta = current + wanted_delta - lead.tick

    margin = cs.time.ticks_per_frame * NEIGHBOUR_MARGIN_FRAMES
    lo_delta, hi_delta = -lead.tick, cs.total - lead.tick
    blocked_lo = blocked_hi = ""
    for _key, move in parts:
        lim = _limits_for(index, move)
        if lim.lo > float("-inf"):
            room = lim.lo + margin - move.tick
            if room > lo_delta:
                lo_delta, blocked_lo = room, lim.lo_label
        if lim.hi < float("inf"):
            room = lim.hi - margin - move.tick
            if room < hi_delta:
                hi_delta, blocked_hi = room, lim.hi_label
        lo_delta = max(lo_delta, -move.tick)
        hi_delta = min(hi_delta, cs.total - move.tick)

    if lo_delta > hi_delta:
        return Drag(wanted=wanted_delta, blocked_by=blocked_lo or blocked_hi,
                    note="there is no room between the cues either side of it")

    clamped = min(max(delta, lo_delta), hi_delta)
    blocked = ""
    if clamped != delta:
        blocked = blocked_lo if clamped == lo_delta else blocked_hi

    if clamped == 0:
        return Drag(wanted=wanted_delta, blocked_by=blocked,
                    note="back where it started")

    moves = [
        (key, CueMove(
            seq=m.seq, clip=m.clip, tick=m.tick, new_tick=m.tick + clamped,
            match=m.match, label=m.label,
            group="" if key == lead_key else lead_key,
        ))
        for key, m in parts
    ]

    note = "%s %s %s" % (
        lead.label,
        "later by" if clamped > 0 else "earlier by",
        cs.time.describe_span(abs(clamped)),
    )
    if len(moves) > 1:
        note += " (with its subtitle)"
    if blocked:
        note += " — stopped by %s" % blocked

    return Drag(moves=moves, delta=clamped, wanted=wanted_delta,
                blocked_by=blocked, note=note)


def revert(state: EditState, item: LaneItem) -> Optional[str]:
    """The cue key to send home, if this block has been moved."""
    key = authored_key(item)
    return key if key and key in state.moves else None
