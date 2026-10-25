"""
The edit state: everything the user has changed about a cutscene, and the pure
functions that interpret it.

Deliberately plain data - no Qt, no timers, no reference to the cutscene. That
is what makes it snapshottable for undo, serialisable to a plan, and testable
without a window.

Every mutation returns a new state, so the undo stack can keep references
instead of deep copies, and views can compare by identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .cues import CueDescriptor


@dataclass(frozen=True)
class CutSpan:
    """A removed span, half-open [a, b) in original ticks."""

    a: float
    b: float

    @property
    def length(self) -> float:
        return self.b - self.a


@dataclass(frozen=True)
class CueMove:
    """One cue dragged to a new time by hand.

    `tick` is the tick the scene authors the cue at and never changes - it is
    the cue's identity, and the thing `patcher.relocation_offsets` matches on.
    `new_tick` is where the user has put it, in **original** ticks, i.e. the
    same space the timeline is drawn in.

    Storing the destination in original ticks rather than edited ones is the
    decision worth keeping. A move made before a cut, and a cut made before a
    move, then mean the same thing: the cue sits at that moment of the footage,
    and `to_edited` works out where that lands once the cuts close up. Storing
    edited ticks would make a move silently drift every time a cut elsewhere in
    the scene changed.

    `match` is the payload identity the patcher uses to find the cue among
    others of its type - the same `IDENTITY_KEYS`/`DISCRIMINATORS` shape
    collapse.py already writes.

    `group` ties moves that were made by one gesture: dragging a line of
    dialogue moves its Voice cue and the subtitle on/off pair with it, and
    dragging it back has to take all three.
    """

    #: sub-sequence it lives in, e.g. "Sound", "Voice", "Text"
    seq: str
    #: Clip_* type without the prefix, e.g. "Se", "Voice", "BGM", "SubTitle"
    clip: str
    #: where the scene fires it, in ORIGINAL ticks
    tick: float
    #: where it will fire, in ORIGINAL ticks
    new_tick: float
    #: payload fields that identify this cue among others of its type
    match: Dict[str, Any] = field(default_factory=dict)
    label: str = ""
    #: cue key of the move this one was dragged along with, or "" if it leads
    group: str = ""

    @property
    def delta(self) -> float:
        return self.new_tick - self.tick


@dataclass(frozen=True)
class MusicRepoint:
    """One music trigger pointed at a different track.

    The cue keeps its time, its fades and its crossfade flag: the only thing
    that changes is the name the game looks the music up by. Nothing about the
    BGM bank is touched, so a repoint has no effect outside this cutscene -
    which is the whole reason it is preferable to shipping a replaced bank, and
    is what makes it safe on `bgm_silence`, a name 56 scenes share.

    `frm` is part of the identity, not decoration. `patcher.repoint_music`
    will only write over a payload whose `MusicName` still reads `frm`, so a
    plan cannot silently rewrite a cue the scene has since changed.

    `capacity` is what the editor believed the name had room for when the
    choice was made. The patcher measures the real span again and refuses a
    mismatch rather than trusting it - see `music.capacity_of`.
    """

    #: sub-sequence the cue lives in, e.g. "ManualSE", "Sound"
    seq: str
    #: where the scene fires it, in ORIGINAL ticks
    tick: float
    #: the name the scene authored
    frm: str
    #: the name it will carry instead
    to: str
    #: bank and slice `to` addresses, kept for the panel and the report
    bank: str = ""
    slice: int = 0
    #: characters the editor measured the old name as having room for
    capacity: int = 0
    label: str = ""

    @property
    def fits(self) -> bool:
        return len(self.to) <= len(self.frm)


@dataclass(frozen=True)
class PinSpan:
    """An actor pinned shown or hidden over part of the scene only.

    A whole-scene pin is blunt, and EV_FOREE_8514 is why this exists. Its two
    Aeriths alternate between 90s and 95s, and at 95s the scene deliberately
    leaves BOTH on screen for the rest of the take - the clean one is the body
    on the floor behind Cloud. Pinning the clean one Hide to stop the pair
    Z-fighting during those five seconds also removed her from every shot after
    them, because a pin has no end.

    Bounded by the same half-open [a, b) convention as a cut, in ORIGINAL
    ticks. Only the actor's own show/hide commands inside that window are
    rewritten.

    **It layers on top of the whole-scene pin rather than replacing it.** Hide
    for the scene plus Show over one range means "hidden everywhere except
    there", which is the combination 8514 wants and neither pin can express
    alone.

    It means "this actor is in this state THROUGHOUT this window", and the
    patcher gets there by rewriting two things: every command inside the
    window, and the **governing command** - the last one before it, which is
    what the actor's state during the window actually comes from.

    That second part is what makes it usable. Visibility is a step function: it
    changes only where a command exists, and long stretches have none.
    EV_FOREE_8514 has nothing after 95.00s at all, so a range over the final
    shot contains no commands and, without the governing rule, could not
    possibly turn anyone on. With it, the 95.00s command is rewritten and she is
    visible from there to the end - which is what selecting the final shot and
    asking for Show plainly meant.

    The cost of the governing rule is that the state also changes from that
    earlier command onwards, not just from `a`. There is no way around it
    without adding commands, which in-place patching cannot do, and the panel
    says which command it is rather than hiding it.

    One span per actor: setting another replaces it, so a pin can always be
    tweaked or cleared rather than accumulating.
    """

    actor: str
    #: True pins hidden, False pins shown
    hidden: bool
    a: float
    b: float

    def contains(self, t: float) -> bool:
        return self.a <= t < self.b


@dataclass(frozen=True)
class EditState:
    #: sorted, non-overlapping spans removed from the timeline
    cuts: Tuple[CutSpan, ...] = ()
    #: VoiceName -> seconds of audio to keep (shortens a line)
    trims: Dict[str, float] = field(default_factory=dict)
    #: cue key -> descriptor of a cue switched off
    killed: Dict[str, CueDescriptor] = field(default_factory=dict)
    #: cue key -> a cue dragged to a new time. Keyed the same way as `killed`
    #: so the two can be reasoned about together: a cue can be moved, switched
    #: off, or both, and each is looked up by the same identity.
    moves: Dict[str, CueMove] = field(default_factory=dict)
    #: actor pinned visible for the whole scene
    force_visible: Tuple[str, ...] = ()
    #: actor pinned hidden for the whole scene
    force_hidden: Tuple[str, ...] = ()
    #: actors pinned over part of the scene only - see PinSpan
    pin_spans: Tuple[PinSpan, ...] = ()
    #: MusicName -> ship a replacement BGM asset for it
    replace_music: Tuple[str, ...] = ()
    #: cue key -> that trigger pointed at a different track. Keyed the same way
    #: as `killed` and `moves`, so one cue can be moved and repointed and the
    #: three are looked up by the same identity.
    #:
    #: Distinct from `replace_music` on purpose, and the difference is the
    #: whole point: `replace_music` rebuilds a BGM bank, which changes that
    #: music in every scene that plays it; this changes which bank one cue in
    #: one cutscene asks for, and touches nothing else.
    repoints: Dict[str, MusicRepoint] = field(default_factory=dict)
    #: keep the fades and level-streaming commands a cut would remove, by
    #: moving them into surviving footage - see collapse.py.
    #: On by default: losing them is a visible fault (a hard cut) or an
    #: invisible one (the next scene's assets never preload), and neither is
    #: something you would choose.
    collapse_to_end: bool = True
    #: re-time a `Preload` the cuts never touched, when a join lands inside the
    #: window it needs to load in. A separate switch from `collapse_to_end` on
    #: purpose: rescuing a cue the cut destroyed is a repair and is always
    #: wanted, while moving one the cut left alone is a bandwidth guess about
    #: engine behaviour we have not measured. Sharing one switch meant the only
    #: way to decline the guess was to decline the repair too, which is exactly
    #: what EV_FOREE_7512 had to do. Off until the guess is verified in game.
    restore_preload_lead: bool = False


def empty_edits() -> EditState:
    return EditState()


def is_untouched(s: EditState) -> bool:
    """No edit has been made. `collapse_to_end` is deliberately not counted:
    on its own it changes nothing, because it only acts on cuts."""
    return (
        not s.cuts
        and not s.trims
        and not s.killed
        and not s.moves
        and not s.force_visible
        and not s.force_hidden
        and not s.pin_spans
        and not s.replace_music
        and not s.repoints
    )


def normalise_cuts(items: Sequence[CutSpan]) -> Tuple[CutSpan, ...]:
    """Drop empties, sort, and merge anything touching or overlapping."""
    ordered = sorted((x for x in items if x.b > x.a), key=lambda x: x.a)
    out: List[CutSpan] = []
    for x in ordered:
        if out and x.a <= out[-1].b:
            out[-1] = CutSpan(out[-1].a, max(out[-1].b, x.b))
        else:
            out.append(CutSpan(x.a, x.b))
    return tuple(out)


def removed_ticks(s: EditState) -> float:
    return sum(x.b - x.a for x in s.cuts)


def edited_ticks(s: EditState, total: float) -> float:
    return total - removed_ticks(s)


def cut_at(s: EditState, t: float) -> Optional[CutSpan]:
    """The cut containing `t`, if any."""
    for x in s.cuts:
        if x.a <= t < x.b:
            return x
    return None


def skip_over(s: EditState, t: float, total: Optional[float] = None) -> float:
    """Advance `t` past the removed span it lands in, if it lands in one.

    This is what makes playback a preview rather than a recording: pressing
    Space walks the playhead over the joins, so what you watch is what the
    built mod will play.

    One pass is enough. `normalise_cuts` merges anything touching, so no two
    spans are adjacent and landing on `x.b` can never be inside another cut.

    `total` clamps a cut that runs to the end of the scene, which is the case
    that otherwise leaves the playhead a hair past the end and the clock
    deciding on the next frame instead of this one.
    """
    for x in s.cuts:
        if x.a <= t < x.b:
            return min(x.b, total) if total else x.b
    return t


def keep_ranges(s: EditState, total: float) -> List[List[float]]:
    """The segments that survive, in order.

    This is the part the patcher cares about: rebuilding the cutscene means
    remapping every section range and cue tick through this list.
    """
    out: List[List[float]] = []
    cursor: float = 0
    for x in s.cuts:
        if x.a > cursor:
            out.append([cursor, x.a])
        cursor = max(cursor, x.b)
    if cursor < total:
        out.append([cursor, total])
    return out


def to_edited(s: EditState, t: float) -> Optional[float]:
    """Where an original tick lands on the edited timeline - None if removed."""
    shift: float = 0
    for x in s.cuts:
        if x.b <= t:
            shift += x.b - x.a
        elif x.a < t:
            return None
    return t - shift


def to_original(s: EditState, t: float) -> float:
    """The inverse: where an edited tick sits on the original timeline.

    Not the same as adding up every cut before it - a tick that lands *before*
    a cut must not have that cut's length added, or it comes back pointing into
    footage that no longer exists. Walking the cuts in order and stopping at
    the first join past `t` is what makes the answer always land in surviving
    footage, which is the property callers rely on.

    `to_original(to_edited(t)) == t` for every surviving tick.
    """
    removed: float = 0
    for x in s.cuts:
        if t < x.a - removed:       # before this cut's join: nothing more to add
            break
        removed += x.b - x.a
    return t + removed


def kept_seconds(s: EditState, voice_name: str, full_seconds: float) -> float:
    """Seconds of a line that survive the trim (never more than the recording holds)."""
    return min(s.trims.get(voice_name, full_seconds), full_seconds)


# -- immutable updates ---------------------------------------------------


def with_cut(s: EditState, span: CutSpan) -> EditState:
    return replace(s, cuts=normalise_cuts(list(s.cuts) + [span]))


def without_cut(s: EditState, span: CutSpan) -> EditState:
    return replace(s, cuts=tuple(x for x in s.cuts if x is not span))


def with_cuts(s: EditState, cuts: Sequence[CutSpan]) -> EditState:
    return replace(s, cuts=normalise_cuts(cuts))


def with_trim(s: EditState, voice_name: str, keep: Optional[float]) -> EditState:
    trims = dict(s.trims)
    if keep is None:
        trims.pop(voice_name, None)
    else:
        trims[voice_name] = keep
    return replace(s, trims=trims)


def with_cue_toggled(s: EditState, key: str, d: CueDescriptor) -> EditState:
    killed = dict(s.killed)
    if key in killed:
        del killed[key]
    else:
        killed[key] = d
    return replace(s, killed=killed)


def with_cue_moved(s: EditState, key: str, move: CueMove) -> EditState:
    """Put a cue at a new time, replacing any move it already had.

    A move back to the authored tick is a removal, not a zero-length move: it
    keeps the plan clean, and it is what dragging a block back where it came
    from plainly means. Callers snap first, so "back where it came from" is an
    exact comparison rather than a tolerance.
    """
    moves = dict(s.moves)
    if move.new_tick == move.tick:
        moves.pop(key, None)
    else:
        moves[key] = move
    # anything dragged along with this cue follows it out
    for k in [k for k, m in moves.items() if m.group == key and k != key]:
        if move.new_tick == move.tick:
            moves.pop(k, None)
    return replace(s, moves=moves)


def with_cue_moves(s: EditState, items: Sequence[Tuple[str, CueMove]]) -> EditState:
    """Apply a whole gesture at once - a dialogue line and its subtitle pair.

    One state transition rather than three, so undo takes the gesture back as
    the user made it instead of unpicking it a cue at a time.
    """
    moves = dict(s.moves)
    for key, move in items:
        if move.new_tick == move.tick:
            moves.pop(key, None)
        else:
            moves[key] = move
    return replace(s, moves=moves)


def without_cue_move(s: EditState, key: str) -> EditState:
    """Send a cue back to its authored tick, and everything dragged with it."""
    moves = {
        k: m for k, m in s.moves.items() if k != key and m.group != key
    }
    return replace(s, moves=moves)


def without_any_cue_moves(s: EditState) -> EditState:
    return replace(s, moves={})


def move_for(s: EditState, key: Optional[str]) -> Optional[CueMove]:
    return s.moves.get(key) if key else None


def moved_tick(s: EditState, key: Optional[str], authored: float) -> float:
    """Where a cue actually sits now, in original ticks."""
    m = move_for(s, key)
    return m.new_tick if m else authored


#: 'normal' | 'show' | 'hide'
ActorPin = str


def actor_pin(s: EditState, actor: str) -> ActorPin:
    if actor in s.force_visible:
        return "show"
    if actor in s.force_hidden:
        return "hide"
    return "normal"


def with_actor_pin(s: EditState, actor: str, how: ActorPin) -> EditState:
    """Pin an actor for the whole scene.

    A swap is two actors, not one - a clean model and a bloodied one taking
    turns - so pinning a state always clears the opposite pin for that actor
    rather than letting both apply.

    `show` and `hide` KEEP any bounded pin: it is the exception carved out of
    this base state, and clearing it here would make setting the base silently
    throw the exception away. `normal` is the reset, so it clears both.
    """
    visible = [a for a in s.force_visible if a != actor]
    hidden = [a for a in s.force_hidden if a != actor]
    if how == "show":
        visible.append(actor)
    elif how == "hide":
        hidden.append(actor)
    spans = s.pin_spans if how != "normal" else tuple(
        p for p in s.pin_spans if p.actor != actor
    )
    return replace(
        s, force_visible=tuple(visible), force_hidden=tuple(hidden),
        pin_spans=spans,
    )


def pin_spans_for(s: EditState, actor: str) -> Tuple[PinSpan, ...]:
    return tuple(p for p in s.pin_spans if p.actor == actor)


def with_pin_span(s: EditState, span: PinSpan) -> EditState:
    """Set the bounded pin for an actor, replacing any it already had.

    One per actor, so pressing the button again with a different range moves
    it instead of stacking - the previous behaviour left a span on the plan
    with no way to change or remove it.

    The whole-scene pin is deliberately left alone. The two compose: the
    scene-wide pin is the base state and this is the exception carved out of
    it, which is the only way to say "hidden throughout except here".
    """
    keep = tuple(p for p in s.pin_spans if p.actor != span.actor)
    return replace(s, pin_spans=keep + (span,))


def without_actor_pin_span(s: EditState, actor: str) -> EditState:
    """Drop an actor's bounded pin(s), leaving its whole-scene pin alone."""
    return replace(s, pin_spans=tuple(p for p in s.pin_spans if p.actor != actor))


def without_global_pin(s: EditState, actor: str) -> EditState:
    """Drop an actor's whole-scene pin, leaving its bounded ones alone."""
    return replace(
        s,
        force_visible=tuple(a for a in s.force_visible if a != actor),
        force_hidden=tuple(a for a in s.force_hidden if a != actor),
    )


@dataclass(frozen=True)
class PinEntry:
    """One pin as the UI lists it - whole-scene and bounded in one shape.

    `span` is None for a whole-scene pin. Listing both together is what makes
    stale ones findable: a bounded pin sits on the plan across sessions, and
    before this the only place it appeared was beside its own actor's row.
    """

    actor: str
    hidden: bool
    span: Optional[PinSpan] = None

    @property
    def is_global(self) -> bool:
        return self.span is None


def all_pins(s: EditState) -> List[PinEntry]:
    """Every visibility pin in the scene, whole-scene first then by time."""
    out = [PinEntry(a, False) for a in s.force_visible]
    out += [PinEntry(a, True) for a in s.force_hidden]
    out.sort(key=lambda e: e.actor)
    spans = sorted(s.pin_spans, key=lambda p: (p.a, p.actor))
    out += [PinEntry(p.actor, p.hidden, p) for p in spans]
    return out


def without_pin_entry(s: EditState, entry: PinEntry) -> EditState:
    if entry.span is None:
        return without_global_pin(s, entry.actor)
    return without_pin_span(s, entry.span)


def without_any_pins(s: EditState) -> EditState:
    return replace(s, force_visible=(), force_hidden=(), pin_spans=())


def without_pin_span(s: EditState, span: PinSpan) -> EditState:
    return replace(s, pin_spans=tuple(p for p in s.pin_spans if p != span))


def with_music_repointed(s: EditState, key: str, r: MusicRepoint) -> EditState:
    """Point one music trigger at a different track.

    Choosing the track the scene already plays is a removal rather than a
    no-op entry, for the same reason dragging a cue back to its authored tick
    is: it keeps the plan free of edits that change nothing, and it is what
    picking the current track plainly means.
    """
    out = dict(s.repoints)
    if r.to == r.frm:
        out.pop(key, None)
    else:
        out[key] = r
    return replace(s, repoints=out)


def without_music_repoint(s: EditState, key: str) -> EditState:
    """Send one trigger back to the track the scene authored."""
    if key not in s.repoints:
        return s
    out = dict(s.repoints)
    del out[key]
    return replace(s, repoints=out)


def repoint_for(s: EditState, key: Optional[str]) -> Optional[MusicRepoint]:
    return s.repoints.get(key) if key else None


def music_name_at(s: EditState, key: Optional[str], authored: str) -> str:
    """What a music cue will actually ask for once the plan is built."""
    r = repoint_for(s, key)
    return r.to if r else authored


def with_music_toggled(s: EditState, music_name: str) -> EditState:
    if music_name in s.replace_music:
        return replace(
            s, replace_music=tuple(a for a in s.replace_music if a != music_name)
        )
    return replace(s, replace_music=s.replace_music + (music_name,))
