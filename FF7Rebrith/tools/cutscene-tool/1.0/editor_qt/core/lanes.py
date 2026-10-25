"""
Turning a cutscene into rows of blocks.

Pure: `build_lanes(cutscene, edits)` is a function of the scene and the current
edits, nothing else. Adding a track means adding a builder to `LANE_BUILDERS` -
no painting code needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from .characters import VOICE_CODE_SPEAKER, canonical, is_character, speaker_code
from .cues import cue_descriptor, cue_key, cue_label, event_cue_key
from .edits import EditState, kept_seconds
from .text import plain
from .timeline import Cutscene, Subtitle, VoiceLine
from .units import TickRange

#: How long a cue block is drawn - cues are instantaneous, so give them a sliver.
CUE_WIDTH_SECONDS = 0.25


@dataclass
class VoiceHandle:
    #: VoiceName, the key trims are stored under
    name: str
    #: tick the clip fires at
    start: float
    #: natural length of the recording, seconds
    full: float
    #: length after any trim, seconds
    kept: float


@dataclass
class LaneItem:
    """One block on a row. Satisfies the `CueSource` protocol in cues.py."""

    type: str
    props: Dict[str, Any]
    range: TickRange
    name: str
    clip: Optional[str] = None
    seq: Optional[str] = None
    tick_start: Optional[float] = None
    #: present only on voice blocks: drives the trim grip and the ghost tail
    voice: Optional[VoiceHandle] = None
    #: the underlying section or event, shown in the details pane
    source: Any = None
    #: canonical character key (characters.py) - overrides the lane colour
    who: Optional[str] = None
    #: the tick the scene authors this cue at, when the user has dragged it
    #: somewhere else. `range` and `tick_start` are then where it WILL fire, so
    #: the tracker draws what gets built; this is where it came from, which is
    #: what the ghost and the connector are drawn from.
    moved_from: Optional[float] = None

    @property
    def moved(self) -> bool:
        return self.moved_from is not None


@dataclass
class Lane:
    id: str
    label: str
    kind: str  # 'camera' | 'voice' | 'subtitle' | 'lip' | 'vfx' | 'cue' | 'shot' | 'anim'
    #: palette key applied to every block in the row
    cls: str
    #: True for structural rows (camera cuts, shots): clicking a block selects
    #: its *time range*, so DEL performs a ripple cut. Cue rows select the cue.
    range_row: bool
    items: List[LaneItem] = field(default_factory=list)
    #: sorted key ticks drawn as marks along the bottom of the row
    ticks: List[float] = field(default_factory=list)
    #: canonical character key (characters.py) when the whole row belongs to one
    #: person - a split dialogue row. Colours the blocks and the gutter swatch,
    #: so a speaker reads the same here as their pin does on the stage.
    who: Optional[str] = None


def trimmed_subtitle_end(cs: Cutscene, state: EditState, r: Subtitle) -> float:
    """A shortened line pulls its subtitle in to match."""
    v = None
    for x in cs.voice:
        if "$" + x.name == r.label or x.name == r.label:
            v = x
            break
    if v is None:
        return r.end
    keep = state.trims.get(v.name)
    if keep is None:
        return r.end
    return min(r.end, v.tick + keep * cs.time.ticks_per_second)


def in_trimmed_tail(cs: Cutscene, state: EditState, t: float) -> bool:
    """Is this tick inside the silenced tail of a trimmed line?"""
    ticks = cs.time.ticks_per_second
    for v in cs.voice:
        keep = state.trims.get(v.name)
        if keep is None:
            continue
        if v.tick + keep * ticks <= t < v.tick + cs.full_duration(v) * ticks:
            return True
    return False


# -- individual lane builders -------------------------------------------


def _camera_lane(cs: Cutscene, state: EditState) -> Optional[Lane]:
    if not cs.cuts:
        return None
    return Lane(
        id="camera",
        label="Camera cuts (%d)" % len(cs.cuts),
        kind="camera",
        cls="cut",
        range_row=True,
        items=[
            LaneItem(
                type="MovieSceneCameraCutSection",
                props={},
                range=c.range,
                name=c.name,
                source=c.section,
            )
            for c in cs.cuts
        ],
    )


def _voice_lane(cs: Cutscene, state: EditState) -> Optional[Lane]:
    if not cs.voice:
        return None
    ticks = cs.time.ticks_per_second
    items: List[LaneItem] = []
    for v in cs.voice:
        full = cs.full_duration(v)
        kept = kept_seconds(state, v.name, full)
        items.append(
            LaneItem(
                type="Voice",
                seq="Voice",
                props=v.props,
                tick_start=v.tick,
                range=(v.tick, v.tick + kept * ticks),
                # the extraction keeps the game's escaped markup; a block label
                # showing `<i>Cloud</i>:` is worse than either form
                name=plain((v.actor + ": " if v.actor else "") + (v.text or v.name)),
                voice=VoiceHandle(name=v.name, start=v.tick, full=full, kept=kept),
                source=v,
            )
        )
    return Lane(
        id="voice",
        label="Voice (%d)" % len(cs.voice),
        kind="voice",
        cls="vo",
        range_row=False,
        items=items,
    )


#: The row an anonymous line ends up on when nothing can name its speaker.
UNATTRIBUTED = "Unattributed"


def learn_speaker_codes(cs: Cutscene) -> Dict[str, str]:
    """Speaker code -> name, learned from this scene's own labelled lines.

    The extraction names an actor only where it could match a subtitle, so a
    scene typically arrives with a third of its lines anonymous. Those lines
    still carry the speaker code in their VoiceName, and the labelled ones say
    what each code means *here* - so the scene answers its own question before
    the shipped table is consulted.

    A code whose labelled lines disagree is left out entirely rather than
    settled by majority: two names on one code means the assumption behind this
    is wrong for that scene, and a row confidently headed with the wrong
    character is worse than one headed with the code.
    """
    seen: Dict[str, Optional[str]] = {}
    for v in cs.voice:
        actor = plain(v.actor or "").strip()
        code = speaker_code(v.name)
        if not code or not actor or actor == "???":
            continue
        if code in seen and seen[code] != actor:
            seen[code] = None          # contradicted: trust neither
        else:
            seen.setdefault(code, actor)
    return {c: n for c, n in seen.items() if n}


def speaker_of(v, learned: Dict[str, str]) -> str:
    """Who says this line, as a row heading.

    In order of how much the answer is worth: what the scene itself says, what
    this scene's other lines prove its codes mean, then the table counted from
    every extracted scene. Failing all three the code is shown raw - `snk` is a
    poor row heading but it is an honest one, and it still separates that
    speaker's lines from everyone else's, which is the point of the row.
    """
    actor = plain(v.actor or "").strip()
    if actor and actor != "???":
        return actor
    code = speaker_code(v.name)
    if not code:
        return UNATTRIBUTED
    return learned.get(code) or VOICE_CODE_SPEAKER.get(code) or code


def split_voice_by_speaker(cs: Cutscene, lanes: List[Lane]) -> List[Lane]:
    """Fan the one dialogue row out into a row per speaker.

    Lines overlap constantly - a reaction lands under the tail of the line it
    answers, and three-way exchanges bury the middle one completely. On a
    single row the buried block cannot be clicked, so it cannot be trimmed,
    dragged or switched off. Split by speaker they stop colliding, because two
    of a scene's lines that overlap are nearly always two different people
    talking.

    Rows keep `kind='voice'`, so trimming, dragging and the lip-sync follow all
    behave exactly as they do on the combined row. Order is first line spoken,
    which reads like the scene rather than like an alphabet.
    """
    learned = learn_speaker_codes(cs)
    by_name: Dict[str, VoiceLine] = {v.name: v for v in cs.voice}
    out: List[Lane] = []
    for lane in lanes:
        if lane.kind != "voice":
            out.append(lane)
            continue
        groups: Dict[str, List[LaneItem]] = {}
        for item in lane.items:
            v = item.source if item.source is not None else by_name.get(
                item.voice.name if item.voice else "")
            who = speaker_of(v, learned) if v is not None else UNATTRIBUTED
            groups.setdefault(who, []).append(item)
        for who, items in groups.items():
            key = canonical(who)
            out.append(
                Lane(
                    id="voice:%s" % who,
                    label="%s (%d)" % (who, len(items)),
                    kind="voice",
                    cls=lane.cls,
                    range_row=False,
                    items=items,
                    who=key if is_character(key) else None,
                )
            )
    return out


def _subtitle_lane(cs: Cutscene, state: EditState) -> Optional[Lane]:
    if not cs.subtitles:
        return None
    return Lane(
        id="subtitles",
        label="Subtitles (%d)" % len(cs.subtitles),
        kind="subtitle",
        cls="subt",
        range_row=False,
        items=[
            LaneItem(
                type="Subtitle",
                props=r.raw,
                range=(r.start, trimmed_subtitle_end(cs, state, r)),
                name=plain((r.actor + ": " if r.actor else "") + (r.text or r.label)),
                source=r,
            )
            for r in cs.subtitles
        ],
    )


def _lip_lane(cs: Cutscene, state: EditState) -> Optional[Lane]:
    if not cs.lipsync:
        return None
    items: List[LaneItem] = []
    for ln in cs.lipsync:
        for f in ln.frames:
            items.append(
                LaneItem(
                    type="Phoneme",
                    props={
                        "phoneme": f[2],
                        "shapes": f[3],
                        "line": ln.voice,
                        "actor": ln.actor,
                    },
                    range=(f[0], f[1]),
                    name=f[2],
                )
            )
    return Lane(
        id="lipsync",
        label="Lip sync (%d)" % len(items),
        kind="lip",
        cls="lip",
        range_row=False,
        items=items,
    )


def _vfx_lane(cs: Cutscene, state: EditState) -> Optional[Lane]:
    if not cs.vfx:
        return None
    return Lane(
        id="vfx",
        label="VFX (%d)" % len(cs.vfx),
        kind="vfx",
        cls="vfx",
        range_row=False,
        items=[
            LaneItem(
                type="VFX",
                props=x.raw,
                range=(x.start, x.end if x.end is not None else cs.total),
                name=x.name,
                source=x,
            )
            for x in cs.vfx
        ],
    )


#: Which event groups get scanned, and the fallback label if a cue has no clip name.
EVENT_GROUPS: Sequence[tuple] = (
    ("Sound", "SE"),
    ("ManualSE", "SE"),
    ("CutEvent", "Event"),
    ("PlannerEvent", "Planner"),
    ("Constraint", "Constraint"),
    ("Light", "Lighting"),
    ("Character", "Character"),
)

#: Readable row titles for the clip types we know.
CLIP_ROW_LABEL = {
    "Se": "SE",
    "BGM": "Music cues",
    "VibrationSe": "Rumble",
    "Fade": "Fades",
    "ActorDraw": "Actor show/hide",
    "SendStateTrigger": "State triggers",
    "DirLightModify": "Lighting (dir)",
    "EnvLightModify": "Lighting (env)",
    "SwitchStreamingVolume": "Streaming",
    "Constraint": "Constraints",
    "Bind": "Bindings",
    "SubTitle": "Subtitle cues",
    "Voice": "Voice cues",
}

#: Rows appear in this order; anything unknown sorts after, alphabetically.
CLIP_ROW_ORDER = [
    "Fade",
    "ActorDraw",
    "Se",
    "VibrationSe",
    "BGM",
    "DirLightModify",
    "EnvLightModify",
    "SwitchStreamingVolume",
    "SendStateTrigger",
    "Constraint",
    "Bind",
]

#: Voice and subtitles already have dedicated rows.
CLIPS_WITH_OWN_LANE = frozenset({"Voice", "SubTitle"})

#: What kind of thing a cue is, which is what decides its colour.
#:
#: Grouping rather than one hue per clip: a scene can show a dozen cue rows, and
#: a dozen unique colours collide with each other and with the structural rows.
#: A family is learnable - red means the game needs it to progress.
CLIP_FAMILY = {
    "Se": "audio",
    "VibrationSe": "rumble",
    "BGM": "music",
    "Fade": "fade",
    "ActorDraw": "actor",
    "CrowdActorDraw": "actor",
    "ActorGameSpeed": "actor",
    "DirLightModify": "light",
    "EnvLightModify": "light",
    "SendStateTrigger": "flow",
    "Jump": "flow",
    "StoryJump": "flow",
    "Constraint": "rig",
    "Bind": "rig",
    "SwitchStreamingVolume": "system",
}


def clip_family(clip: str) -> str:
    """Palette key for a cue row. Unknown clips get their own muted colour
    rather than borrowing one, so a new clip type is visibly new."""
    return CLIP_FAMILY.get(clip, "evt")


def _cue_lanes(cs: Cutscene, state: EditState) -> List[Lane]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for key, fallback in EVENT_GROUPS:
        for e in cs.events(key):
            g = e.get("clip") or fallback
            entry = dict(e)
            entry["__seq"] = key
            groups.setdefault(g, []).append(entry)

    def order(name: str):
        try:
            i = CLIP_ROW_ORDER.index(name)
        except ValueError:
            i = 99
        return (i, name)

    width = CUE_WIDTH_SECONDS * cs.time.ticks_per_second

    def block_name(e: Dict[str, Any]) -> str:
        """The label inside the block.

        A repointed music trigger is drawn as the track it will actually ask
        for, with the scene's own name after it. The row is the only place the
        edit is visible at a glance, and a BGM block still reading
        `bgm_Nible_029` after you have pointed it somewhere else is precisely
        the sort of quiet disagreement between what is shown and what is built
        that the rest of this editor goes out of its way to avoid.
        """
        label = cue_label(e)
        r = state.repoints.get(event_cue_key(e["__seq"], e) or "")
        return "%s  (was %s)" % (r.to, r.frm) if r else label

    lanes: List[Lane] = []
    for g in sorted(groups, key=order):
        if g in CLIPS_WITH_OWN_LANE:
            continue
        items = groups[g]
        lanes.append(
            Lane(
                id="cue:" + g,
                label="%s (%d)" % (CLIP_ROW_LABEL.get(g, g), len(items)),
                kind="cue",
                cls=clip_family(g),
                range_row=False,
                items=[
                    LaneItem(
                        type=g,
                        clip=e.get("clip"),
                        seq=e["__seq"],
                        props=e.get("props") or {},
                        tick_start=e["tick"],
                        range=(e["tick"], e["tick"] + width),
                        name=block_name(e),
                        source=e,
                    )
                    for e in items
                ],
            )
        )
    return lanes


def _shot_lane(cs: Cutscene, state: EditState) -> Lane:
    return Lane(
        id="shots",
        label="Shots (root)",
        kind="shot",
        cls="shot",
        range_row=True,
        items=[
            LaneItem(
                type=s.get("type", ""),
                props={},
                range=(s["range"][0], s["range"][1]),
                name=s.get("name") or s.get("type", ""),
                source=s,
            )
            for s in cs.shots
            if s.get("range")
        ],
    )


#: Row order, top to bottom. Each builder returns None when the scene has
#: nothing for it, and the row is dropped.
LANE_BUILDERS: List[Callable[[Cutscene, EditState], Any]] = [
    _camera_lane,
    _voice_lane,
    _subtitle_lane,
    _lip_lane,
    _vfx_lane,
    _cue_lanes,
    _shot_lane,
]


#: Clip types the editor lets you drag along its row.
#:
#: Deliberately a short list. Every one of these is a cue the game looks up by
#: name at a tick and nothing else depends on when it fires - a sound, a line,
#: a music change. The ones left out are left out for reasons, not for lack of
#: time: `SendStateTrigger` and `Jump` are how the game progresses,
#: `SwitchStreamingVolume` is already moved by `collapse.py` against a rule it
#: can explain, and `Bind`/`Constraint` are structural - a binding that fires
#: late is an actor attached to nothing for those frames.
MOVABLE_CLIPS = frozenset({"Se", "BGM", "Voice", "SubTitle"})


def can_move(lane: Lane, item: LaneItem) -> bool:
    """Is this block one the user may drag?

    Reads the clip type rather than the row, so a cue that turns up on an
    unexpected row still behaves the way its type says it should.
    """
    if lane.range_row:
        return False
    if lane.kind == "voice":
        return True
    if lane.kind == "subtitle":
        return True
    return (item.clip or item.type) in MOVABLE_CLIPS


def _shift(item: LaneItem, delta: float, origin: float) -> None:
    """Slide a block along its row, remembering where it started."""
    item.range = (item.range[0] + delta, item.range[1] + delta)
    if item.tick_start is not None:
        item.tick_start += delta
    if item.voice is not None:
        item.voice.start += delta
    item.moved_from = origin


def apply_moves(cs: Cutscene, state: EditState, lanes: List[Lane]) -> List[Lane]:
    """Draw every dragged cue where it will fire, not where it was authored.

    The tracker's job is to show what gets built - the same reason `set_edits`
    takes the cuts as they will be APPLIED rather than as they were drawn. A
    moved cue sitting at its old tick with an arrow pointing elsewhere would
    make the timeline something you have to translate; the ghost at
    `moved_from` carries the history instead.

    Lip sync follows its line without being moved by anything here in the plan:
    phoneme times in the LSD packs are relative to the clip start, so in game
    the mouth goes wherever the voice cue goes. Shifting the row keeps the
    preview honest about that rather than implying a desync that will not
    happen.
    """
    if not state.moves:
        return lanes

    #: VoiceName -> how far its line moved, for the lip-sync row
    voice_delta: Dict[str, float] = {}
    for lane in lanes:
        if lane.kind == "lip":
            continue
        for item in lane.items:
            move = state.moves.get(cue_key(cue_descriptor(item)) or "")
            if move is None:
                continue
            origin = item.tick_start if item.tick_start is not None else item.range[0]
            _shift(item, move.new_tick - move.tick, origin)
            if item.voice is not None:
                voice_delta[item.voice.name] = move.new_tick - move.tick

    if voice_delta:
        for lane in lanes:
            if lane.kind != "lip":
                continue
            for item in lane.items:
                delta = voice_delta.get(str((item.props or {}).get("line") or ""))
                if delta:
                    _shift(item, delta, item.range[0])

    for lane in lanes:
        lane.items.sort(key=lambda i: i.range[0])
    return lanes


def apply_relocations(cs: Cutscene, plan, lanes: List[Lane]) -> List[Lane]:
    """Draw the cues `collapse.py` is carrying across a cut where they land.

    Same principle as `apply_moves`, for the other source of relocation. A fade
    rescued out of a cut really does fire at the join, so that is where its
    block belongs; leaving it inside the red band said the opposite of what the
    build was about to do.

    Cues the user moved by hand are skipped - `apply_moves` has already placed
    those, and `collapse.effective` puts both kinds in one list, so without
    this guard a dragged cue would be shifted twice.
    """
    if plan is None or not getattr(plan, "relocations", ()):
        return lanes
    by_key = {(r.seq, r.tick): r for r in plan.relocations}
    for lane in lanes:
        for item in lane.items:
            if item.moved or item.seq is None:
                continue
            origin = item.tick_start if item.tick_start is not None else item.range[0]
            rel = by_key.get((item.seq, origin))
            if rel is None:
                continue
            _shift(item, rel.at_tick - origin, origin)
        lane.items.sort(key=lambda i: i.range[0])
    return lanes


def build_lanes(
    cs: Cutscene, state: EditState, voice_by_speaker: bool = False
) -> List[Lane]:
    """Every row for this scene.

    `voice_by_speaker` is a view preference, not an edit: it changes how the
    same lines are arranged on screen and nothing about what gets built, which
    is why it is an argument here rather than a field on `EditState`.
    """
    out: List[Lane] = []
    for build in LANE_BUILDERS:
        r = build(cs, state)
        if not r:
            continue
        if isinstance(r, list):
            out.extend(r)
        else:
            out.append(r)
    if voice_by_speaker:
        out = split_voice_by_speaker(cs, out)
    return apply_moves(cs, state, out)
