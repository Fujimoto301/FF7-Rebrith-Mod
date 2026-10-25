"""
The edit plan - the contract between this editor and build_mod.py / patcher.py.

Key order and field names here are deliberate: the Python side reads
`removeRanges`, `trimLines`, `disableCues`, `forceVisible`, `forceHidden`,
`replaceMusic`, `repointMusic`, `playbackRange`, `tickResolution`,
`displayRate` and `ticksPerFrame` by name, and a saved plan must round-trip
back into the editor unchanged. Anything added here must be additive.

Two details exist purely to keep byte-parity with the plans editor_v3 writes,
which are the plans already confirmed working in game:

* `_num` writes an integral tick as `96000`, not `96000.0`. Snapping produces
  floats in Python because ticks_per_frame is a float; JSON would carry that
  through and change the file.
* `_fixed` rounds half-up like JavaScript's toFixed, not half-to-even like
  Python's round.
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable, Dict, List, Optional, Tuple

from .collapse import effective
from .cues import CueDescriptor, cue_key as _cue_key
from .edits import (
    CueMove,
    CutSpan,
    EditState,
    MusicRepoint,
    PinSpan,
    edited_ticks,
    empty_edits,
    keep_ranges,
    normalise_cuts,
)
from .impact import impact_of
from .timeline import Cutscene
from .units import round_half_up

#: Bumping this is safe; the Python side does not read it.
PLAN_TOOL_ID = "ff7r-cutscene-editor v0.4 (ripple)"


def _num(x: float):
    """An integral tick as an int, so JSON matches what editor_v3 wrote."""
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def _fixed(x: float, places: int) -> float:
    """JavaScript `+n.toFixed(places)` - half-up, then back to a number."""
    q = Decimal(1).scaleb(-places)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def repoint_key(seq: str, tick: float, frm: str) -> str:
    """The cue key a music repoint lives under - **derived, never trusted**.

    Everything that has to find a repoint spells the key from the same three
    facts: the sub-sequence, the tick the scene authors the cue at, and the
    name it authors it with. `cues.event_cue_key` does it from a raw event,
    `drag.authored_key` from a block on screen, and this from a plan entry.

    Deriving it here rather than reading the `key` the file carries is what
    makes a plan written by a build that spelled it differently load correctly
    anyway. It cost a session to learn: the window was keying repoints off a
    *moved* block's current tick, so the plan recorded the right cue under a
    key the preview mix could not find, and the editor showed the new track
    while playing the old one.
    """
    return _cue_key({"seq": seq, "tick": _num(tick), "field": "MusicName",
                     "value": frm}) or ""


def to_plan(cs: Cutscene, authored: EditState, index: Any = None) -> Dict[str, Any]:
    """Serialise the current edits. Field order matches the v2/v3 editors.

    `relocateCues` is the one addition that changes bytes: the fades and level
    streaming commands the cuts would otherwise swallow, each with the tick it
    is to be written at. Everything else about the cuts is unchanged.

    Pass `index` (an `arrays.ArrayIndex`) so those ticks are ones the build can
    actually write. Without it a rescue can be planned in front of its own
    Times-array neighbour, which `patcher.check_relocation_order` then refuses -
    leaving the plan describing a build that was never possible.
    """
    ticks = cs.time.ticks_per_second
    tpf = cs.time.ticks_per_frame

    state, collapse = effective(cs, authored, index)

    impact: List[Dict[str, Any]] = []
    for x in state.cuts:
        h = impact_of(cs, x.a, x.b)
        impact.append(
            {
                "range": [_num(x.a), _num(x.b)],
                "seconds": _fixed((x.b - x.a) / ticks, 3),
                "frames": round_half_up((x.b - x.a) / tpf),
                "wholeShots": h.cuts,
                "voiceLines": len(h.lines),
                "splitsVoiceLine": h.mid_line or None,
                "audioOverrunSeconds": _fixed(h.overrun / ticks, 2),
                "strandedSubtitles": h.stranded,
                "lipsyncDesync": h.lip_split,
                "stateTriggers": h.triggers,
                "jumps": len(h.jumps),
            }
        )

    edited = edited_ticks(state, cs.total)

    trim_lines: List[Dict[str, Any]] = []
    for name, keep in state.trims.items():
        v = cs.voice_by_name(name)
        trim_lines.append(
            {
                "voice": name,
                "keepSeconds": keep,
                "originalSeconds": v.raw_duration if v else None,
                "actor": (v.actor if v and v.actor else None) if v else None,
                "tick": _num(v.tick) if v else None,
            }
        )

    return {
        "tool": PLAN_TOOL_ID,
        "cutscene": cs.name,
        "area": cs.area,
        "tickResolution": _num(ticks),
        "displayRate": _num(cs.time.fps),
        "ticksPerFrame": _num(tpf),
        "playbackRange": [_num(cs.playback_range[0]), _num(cs.playback_range[1])],
        "mode": "ripple-delete",
        "removeRanges": [[_num(x.a), _num(x.b)] for x in state.cuts],
        "keepRanges": [[_num(a), _num(b)] for a, b in keep_ranges(state, cs.total)],
        "collapseToEnd": authored.collapse_to_end,
        "restorePreloadLead": authored.restore_preload_lead,
        # Cues dragged by hand, as authored. `toTick` is in ORIGINAL ticks -
        # the space the timeline draws in - which is deliberately NOT the space
        # `relocateCues[].newTick` below speaks. This list is the input the
        # user wrote; that one is the output the patcher carries out, and the
        # conversion between them is `to_edited`. Keeping both means a plan
        # reloads to the same drag even after its cuts have been changed, and
        # `relocateCues` is always re-derived rather than trusted.
        "cueMoves": [
            {
                "key": key,
                "seq": m.seq,
                "clip": m.clip,
                "tick": _num(m.tick),
                "toTick": _num(m.new_tick),
                "seconds": [_fixed(m.tick / ticks, 3), _fixed(m.new_tick / ticks, 3)],
                "deltaSeconds": _fixed(m.delta / ticks, 3),
                "match": m.match,
                "label": m.label,
                "group": m.group,
            }
            for key, m in sorted(state.moves.items(), key=lambda kv: kv[1].tick)
        ],
        "relocateCues": [
            {
                "seq": r.seq,
                "clip": r.clip,
                "tick": _num(r.tick),
                "newTick": _num(r.new_tick),
                "atTick": _num(r.at_tick),
                "fromEnd": _num(r.from_end),
                "why": r.why,
                "match": r.match,
                "label": r.label,
            }
            for r in collapse.relocations
        ],
        "lostCues": [
            {
                "clip": x.clip,
                "tick": _num(x.tick),
                "label": x.label,
                "why": x.reason,
            }
            for x in collapse.lost
        ],
        "disableCues": list(state.killed.values()),
        "forceVisible": list(state.force_visible),
        "forceHidden": list(state.force_hidden),
        # Pins limited to part of the scene. Additive: a build that ignores
        # these leaves those actors on their authored schedule, which is what
        # happened before bounded pins existed.
        "pinSpans": [
            {
                "actor": p.actor,
                "hidden": p.hidden,
                # ticks are int32s in the asset; a range drawn with the
                # mouse is not, so it is rounded before it reaches the plan
                "range": [_num(round(p.a)), _num(round(p.b))],
                "seconds": [_fixed(p.a / ticks, 3), _fixed(p.b / ticks, 3)],
            }
            for p in state.pin_spans
        ],
        "replaceMusic": list(state.replace_music),
        # Music triggers pointed at a different track. `from` is written as
        # well as `to` because the patcher matches on it: a payload whose
        # MusicName no longer reads `from` is left alone and reported, rather
        # than being overwritten on the strength of a tick alone.
        "repointMusic": [
            {
                # written from the same three facts it is read back from, so a
                # plan cannot carry a key that disagrees with its own contents
                "key": repoint_key(r.seq, r.tick, r.frm) or key,
                "seq": r.seq,
                "clip": "BGM",
                "tick": _num(r.tick),
                "seconds": _fixed(r.tick / ticks, 3),
                "field": "MusicName",
                "from": r.frm,
                "to": r.to,
                "bank": r.bank,
                "slice": r.slice,
                "capacity": r.capacity,
                "label": r.label,
            }
            for key, r in sorted(state.repoints.items(), key=lambda kv: kv[1].tick)
        ],
        "trimLines": trim_lines,
        "originalTicks": _num(cs.total),
        "editedTicks": _num(edited),
        "originalSeconds": _fixed(cs.total / ticks, 3),
        "editedSeconds": _fixed(edited / ticks, 3),
        "impact": impact,
    }


class PlanLoadError(ValueError):
    pass


def from_plan(
    cs: Cutscene,
    plan: Any,
    cue_key_of: Callable[[CueDescriptor], Optional[str]],
) -> Tuple[EditState, str]:
    """Read a plan back into edit state.

    Refuses a plan for a different cutscene rather than applying it to the wrong
    scene. Raises PlanLoadError; returns (state, summary) on success.
    """
    if not isinstance(plan, dict):
        raise PlanLoadError("not an edit plan")
    name = plan.get("cutscene")
    if name and name != cs.name:
        raise PlanLoadError(
            "that plan is for %s, this window is showing %s" % (name, cs.name)
        )

    cuts = [CutSpan(a, b) for a, b in (plan.get("removeRanges") or [])]

    trims: Dict[str, float] = {}
    for t in plan.get("trimLines") or []:
        if t.get("voice") and t.get("keepSeconds"):
            trims[t["voice"]] = t["keepSeconds"]

    killed: Dict[str, CueDescriptor] = {}
    for d in plan.get("disableCues") or []:
        k = cue_key_of(d)
        if k:
            killed[k] = d

    # Hand-authored moves. The key is stored rather than recomputed: it has to
    # be the same string the editor derives from a timeline block via
    # `cue_key(cue_descriptor(item))`, and re-deriving it here from a partial
    # record is how the two would drift apart. An entry without one is skipped
    # rather than guessed at - a move nobody can match to a block on screen is
    # a move the user cannot undo.
    moves: Dict[str, CueMove] = {}
    for m in plan.get("cueMoves") or []:
        key = m.get("key")
        if not key or m.get("tick") is None or m.get("toTick") is None:
            continue
        moves[key] = CueMove(
            seq=m.get("seq") or "",
            clip=m.get("clip") or "",
            tick=m["tick"],
            new_tick=m["toTick"],
            match=dict(m.get("match") or {}),
            label=m.get("label") or "",
            group=m.get("group") or "",
        )

    # Repointed music triggers. Keyed exactly as `cueMoves` are, and skipped
    # for the same reason when the key is missing: a repoint nobody can match
    # to a block on screen is one the user cannot see, undo, or trust.
    repoints: Dict[str, MusicRepoint] = {}
    for r in plan.get("repointMusic") or []:
        if not r.get("from") or not r.get("to"):
            continue
        # Re-derived rather than read. A plan written before `authored_key` was
        # used in the window carries the key of the tick a dragged block was
        # drawn at; the `tick` beside it was always the authored one, so the
        # right key can be rebuilt and such a plan heals itself on load.
        key = repoint_key(r.get("seq") or "", r.get("tick") or 0, r["from"]) \
            or r.get("key")
        if not key:
            continue
        repoints[key] = MusicRepoint(
            seq=r.get("seq") or "",
            tick=r.get("tick") or 0,
            frm=r["from"],
            to=r["to"],
            bank=r.get("bank") or "",
            slice=int(r.get("slice") or 0),
            capacity=int(r.get("capacity") or 0),
            label=r.get("label") or "",
        )

    state = EditState(
        cuts=normalise_cuts(cuts),
        trims=trims,
        killed=killed,
        moves=moves,
        force_visible=tuple(plan.get("forceVisible") or []),
        force_hidden=tuple(plan.get("forceHidden") or []),
        pin_spans=tuple(
            PinSpan(p["actor"], bool(p.get("hidden")), p["range"][0], p["range"][1])
            for p in (plan.get("pinSpans") or [])
            if p.get("actor") and p.get("range")
        ),
        replace_music=tuple(plan.get("replaceMusic") or []),
        repoints=repoints,
        # A plan from before this feature has no flag. Defaulting it to True
        # would silently change what an old plan builds, so those load with it
        # off and the toggle is there to turn on.
        collapse_to_end=bool(plan.get("collapseToEnd", False)),
        # Also absent from every plan written before the split. Defaulting it
        # off is what lets a scene take the repair without the guess - the
        # combination that was previously unreachable.
        restore_preload_lead=bool(plan.get("restorePreloadLead", False)),
    )

    parts = []
    if state.cuts:
        parts.append("%d cut%s" % (len(state.cuts), "s" if len(state.cuts) > 1 else ""))
    if trims:
        parts.append("%d trim%s" % (len(trims), "s" if len(trims) > 1 else ""))
    if killed:
        parts.append(
            "%d deleted cue%s" % (len(killed), "s" if len(killed) > 1 else "")
        )
    if moves:
        parts.append("%d moved cue%s" % (len(moves), "s" if len(moves) > 1 else ""))
    if repoints:
        parts.append(
            "%d repointed music cue%s"
            % (len(repoints), "s" if len(repoints) > 1 else "")
        )
    return state, ", ".join(parts)


def plan_changes_something(p: Dict[str, Any]) -> bool:
    """Does this plan ask for any work at all? Mirrors serve_editor.build_plan.

    `cueMoves` counts on its own: moving a sound with no cut anywhere in the
    scene is a complete edit, and before this the build would have refused it
    as empty. `repointMusic` counts for exactly the same reason - swapping the
    music of a scene you have not otherwise touched is a mod in itself.
    """
    return bool(
        p.get("removeRanges") or p.get("disableCues") or p.get("trimLines")
        or p.get("cueMoves") or p.get("repointMusic")
    )


def write_plan(path: str, plan: Dict[str, Any]) -> None:
    """Same shape serve_editor.py writes: indent=1, so diffs stay readable."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=1)
