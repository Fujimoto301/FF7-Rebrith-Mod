"""
Cues: the individual events on a track, and what it means to switch one off.

In-place patching cannot delete anything, so a cue is disabled by breaking the
name the game looks up (`EV_FOREE_8510_07` -> `CUT_OREE_8510_07`). That means
only cues that *carry* a name can be disabled at all, and the editor has to be
honest about which those are rather than pretending.

A descriptor identifies a cue to the patcher: which sub-sequence it lives in,
the tick it fires at, and the field holding the name. It is written verbatim
into the edit plan, so its shape is part of the contract with patcher.py -
`disable_cues()` reads exactly these keys. Descriptors are therefore plain
dicts here, not dataclasses: what goes into the plan is what the patcher reads,
with no serialisation layer in between to get it wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .units import TickRange

#: Fields that hold a name the game resolves at runtime, in lookup order.
CUE_NAME_FIELDS = ("VoiceName", "SeName", "MusicName", "TextLabel", "ActorName")

#: Clips the game needs in order to progress. Removing one risks a softlock, so
#: the editor refuses rather than warning - see EDITING.md.
PROTECTED_CLIPS = frozenset({"SendStateTrigger", "Jump", "StoryJump"})

#: Clips switched off by something other than breaking their name.
#:
#: A `Constraint` carries `ActorName`, but that is not a name the game looks
#: anything up by - it says which actor to attach, and the attach happens
#: anyway with the string broken. EV_CORLE_0100 proved it: six flower-lei
#: constraints renamed to `CUT_ORLE_0100_FA0418_00a`.., the patched asset
#: carrying every one, and the leis still on the characters in game.
#:
#: `patcher.detach_constraint` switches one off the way the format actually
#: allows - by turning the payload's own `Detach` flag on, so the cue that put
#: the lei round a neck becomes the cue that takes it off. The plan entry is
#: the same shape as any other; only the mechanism differs, and the name is
#: deliberately left intact because the detach has to resolve the same actor.
DETACH_CLIPS = frozenset({"Constraint"})

#: Payload keys that say *which* cue this is, when one has to be found again in
#: the asset bytes. Written into a plan's `relocateCues[].match`.
#:
#: **This must stay equal to `patcher.DISCRIMINATORS`**, and
#: `test_core.py::MoveIdentity` asserts that it does. The patcher's rule is
#: all-or-nothing: a payload block is a candidate only if every discriminator
#: it carries is also in `match` and agrees. So a key here that the patcher
#: does not know is harmless, but a key the patcher knows and we omit makes the
#: match fail outright - the cue is reported as not found and never moves. The
#: failure is silent-looking from the editor's side, which is exactly why the
#: two lists are pinned together by a test rather than by a comment.
DISCRIMINATORS = (
    "From", "To", "Frame", "White",
    "VolumeLabel", "SwitchLabel", "SwitchType",
    "Labels", "Hidden", "WithoutCollision",
    "TargetName", "MovieName",
    "ActorName", "ActorNames", "SeName", "VoiceName", "MusicName",
    "TextLabel", "TriggerID", "CharaSpec", "Reference",
)


def identity(props: Dict[str, Any]) -> Dict[str, Any]:
    """The subset of a payload that identifies this cue to the patcher."""
    out: Dict[str, Any] = {}
    for k in DISCRIMINATORS:
        if k in props:
            v = props[k]
            out[k] = list(v) if isinstance(v, (list, tuple)) else v
    return out

#: A cue descriptor as written into the plan.
CueDescriptor = Dict[str, Any]


def _s(v: Any) -> Optional[str]:
    return v if isinstance(v, str) and v else None


class CueSource:
    """The minimum a timeline block must expose to be identified as a cue.

    `LaneItem` satisfies this; so does anything else with the same attributes.
    """

    type: str
    clip: Optional[str]
    seq: Optional[str]
    props: Dict[str, Any]
    tick_start: Optional[float]
    range: Optional[TickRange]


def cue_descriptor(s: Any) -> Optional[CueDescriptor]:
    """What would be written to the plan to switch this block off.

    None when the block carries no name to break.
    """
    if s is None:
        return None

    kind = getattr(s, "type", None)
    props: Dict[str, Any] = getattr(s, "props", None) or {}

    if kind == "VFX":
        return {
            "kind": "vfx",
            "name": props.get("name", ""),
            "raw": props.get("raw", ""),
            "start": props.get("start", 0),
            "end": props.get("end"),
            "label": "VFX " + (props.get("name") or ""),
        }

    if kind == "Subtitle":
        # Unchanged shape on purpose. A caption is switched off over a window
        # rather than at a point - 44 lines in this game carry per-language
        # variants of themselves opening up to a couple of seconds apart - but
        # the window is worked out by `patcher.subtitle_lines` from the asset,
        # where the pairing is unambiguous, rather than being carried here.
        # That keeps the plan format alone and means plans saved before any of
        # this get the fix without being rewritten.
        return {
            "seq": "Text",
            "tick": props.get("start", 0),
            "field": "TextLabel",
            "value": str(props.get("label", "")),
            "label": "subtitle "
            + (_s(props.get("actor")) or _s(props.get("label")) or ""),
        }

    seq = getattr(s, "seq", None)
    if not seq:
        return None

    for fieldname in CUE_NAME_FIELDS:
        value = _s(props.get(fieldname))
        if not value:
            continue
        clip = getattr(s, "clip", None) or kind
        tick_start = getattr(s, "tick_start", None)
        if tick_start is None:
            rng = getattr(s, "range", None)
            tick_start = rng[0] if rng else 0
        return {
            "seq": seq,
            "tick": tick_start,
            "field": fieldname,
            "value": value,
            "clip": clip,
            "label": (getattr(s, "clip", None) or seq) + " " + value,
        }
    return None


def event_cue_key(seq: str, e: Dict[str, Any]) -> Optional[str]:
    """The cue key for a raw timeline event, without building a block first.

    Must produce exactly what `cue_key(cue_descriptor(item))` produces for the
    LaneItem the same event becomes, because that is the key `EditState.killed`
    and `EditState.moves` are stored under. Anything reading those maps from
    raw events - the preview mixdown, for one - has to spell the key the same
    way, and one spelling in one place is how that stays true.
    """
    props = e.get("props") or {}
    tick = e.get("tick")
    if tick is None:
        return None
    for fieldname in CUE_NAME_FIELDS:
        value = _s(props.get(fieldname))
        if value:
            return "%s|%s|%s|%s" % (seq, tick, fieldname, value)
    return None


def cue_key(d: Optional[CueDescriptor]) -> Optional[str]:
    """Stable identity for a descriptor - the key of the killed-cue map."""
    if not d:
        return None
    if d.get("kind") == "vfx":
        return "vfx|%s|%s" % (d.get("raw"), d.get("start"))
    return "%s|%s|%s|%s" % (d.get("seq"), d.get("tick"), d.get("field"), d.get("value"))


@dataclass(frozen=True)
class CueRefusal:
    """Whether a block can be switched off on its own, and if not, why -
    so the UI can offer the time-range cut instead of failing silently."""

    ok: bool
    descriptor: Optional[CueDescriptor] = None
    key: Optional[str] = None
    reason: str = ""
    clip: str = ""
    what: str = ""
    range: Optional[TickRange] = None


def can_disable(s: Any) -> CueRefusal:
    what = getattr(s, "clip", None) or getattr(s, "type", None) or "that block"
    d = cue_descriptor(s)
    key = cue_key(d)
    if not d or not key:
        r = getattr(s, "range", None)
        return CueRefusal(
            ok=False,
            reason="unnamed",
            what=what,
            range=r if (r and r[1] > r[0]) else None,
        )
    if d.get("kind") != "vfx" and d.get("clip") in PROTECTED_CLIPS:
        return CueRefusal(ok=False, reason="protected", clip=d["clip"], what=what)
    return CueRefusal(ok=True, descriptor=d, key=key, what=what)


def cue_label(e: Dict[str, Any]) -> str:
    """Human label for a cue block, used as the text inside it on the timeline."""
    p = e.get("props") or {}

    def s(k: str) -> Optional[str]:
        return _s(p.get(k))

    if s("SeName"):
        return s("SeName")
    if s("MusicName"):
        return s("MusicName")
    if s("VoiceName"):
        return s("VoiceName")
    if "From" in p:
        return "fade %s→%s%s" % (
            p.get("From"),
            p.get("To"),
            " (white)" if p.get("White") else "",
        )
    if s("ActorName"):
        if e.get("clip") == "ActorDraw":
            return "%s %s" % (s("ActorName"), "hide" if p.get("Hidden") else "show")
        return s("ActorName")
    if "TriggerID" in p:
        v = p["TriggerID"]
        return ", ".join(str(x) for x in (v if isinstance(v, list) else [v]))
    if "ActorNames" in p:
        v = p["ActorNames"]
        return ", ".join(str(x) for x in (v if isinstance(v, list) else [v])[:2])
    if "VolumeLabel" in p:
        return "%s → %s" % (p.get("VolumeLabel"), p.get("SwitchLabel") or "")
    if s("TargetName"):
        return s("TargetName")
    return e.get("clip") or ""


def actor_of(s: Any) -> Optional[str]:
    """The actor a block pins, if it names one."""
    props = getattr(s, "props", None) or {}
    name = props.get("ActorName")
    return name if isinstance(name, str) and name != "None" else None
