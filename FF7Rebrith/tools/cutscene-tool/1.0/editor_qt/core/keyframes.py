"""
Animation and lighting keyframes, read live from the game assets.

The extracted timeline JSONs do not carry these - extract_timeline.py never
read `_Character` or `_Light`, and its sections have no channel key times. But
the editor now runs in the same language as the parsers, so rather than
extending the extraction and re-extracting 755 files, the two assets are read
directly from the Content folder when a scene opens. Parse cost is ~0.1s per
scene against real assets, and nothing is written anywhere.

When the Content folder is not configured, or a scene's assets are missing,
there are simply no animation/lighting rows. Missing rows, not errors.

What is read:

* `_Character`: object bindings (actor -> tracks), skeletal animation sections
  (the clip blocks, named by their `RefOnDisconnected` id), and the key times
  of every transform/float channel, unioned per actor.
* `_Light`: every float/bool/color channel key time, unioned per binding, then
  aggregated - one scene has 69 lighting bindings and 370 float sections, and
  69 rows would drown the timeline.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

#: The tool modules (zenasset, transforms) live beside editor_qt, not inside it.
_TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOL_DIR not in sys.path:
    sys.path.insert(0, _TOOL_DIR)


@dataclass(frozen=True)
class AnimClip:
    actor: str
    #: clip id, e.g. `C0010` - the tail of RefOnDisconnected
    clip: str
    start: float
    end: float


@dataclass
class SceneKeys:
    #: animation clip blocks, in time order
    clips: List[AnimClip] = field(default_factory=list)
    #: actor -> sorted, deduplicated key ticks (transform + anim channels)
    actor_keys: Dict[str, List[float]] = field(default_factory=dict)
    #: sorted, deduplicated key ticks across every lighting channel
    light_keys: List[float] = field(default_factory=list)
    #: how many lighting bindings contributed (for the row label)
    light_bindings: int = 0

    @property
    def empty(self) -> bool:
        return not self.clips and not self.actor_keys and not self.light_keys


_USMAP_CACHE: Dict[str, Any] = {}


def _usmap(path: str):
    if path not in _USMAP_CACHE:
        from zenasset import Usmap

        _USMAP_CACHE[path] = Usmap(path)
    return _USMAP_CACHE[path]


def _strip_ev(name: str, ev: str) -> str:
    """`EV_NIBLE_0110_EN0000_00` -> `EN0000_00`."""
    prefix = ev + "_"
    return name[len(prefix):] if name.startswith(prefix) else name


def _channel_times(props: Dict[str, Any]) -> List[float]:
    out: List[float] = []
    for v in props.values():
        times = getattr(v, "times", None)
        if times:
            out.extend(times)
    return out


#: Where a track keeps its sections. `MovieSceneSkeletalAnimationTrack` uses
#: `AnimationSections`, not `Sections` — miss that and every animation clip is
#: unowned, which is exactly how the first version of this produced a row of
#: clips belonging to nobody.
_SECTION_LISTS = ("Sections", "AnimationSections")


def _binding_of_sections(reader, ms: Dict[str, Any]) -> Dict[int, str]:
    """section export index -> binding name, walked through each track."""
    owner: Dict[int, str] = {}
    for b in ms.get("ObjectBindings") or []:
        name = b.get("BindingName") or ""
        for tr in b.get("Tracks") or []:
            ti = tr.get("export")
            if ti is None:
                continue
            tp = reader.read_export(ti) or {}
            for key in _SECTION_LISTS:
                for s in tp.get(key) or []:
                    si = s.get("export") if isinstance(s, dict) else None
                    if si is not None:
                        owner[si] = name
    return owner


def _load_character(path: str, usmap, ev: str) -> Tuple[List[AnimClip], Dict[str, List[float]]]:
    import transforms as T

    r = T.Reader2(path, usmap)
    ms_idx = r.find("MovieScene")
    if not ms_idx:
        return [], {}
    ms = r.read_export(ms_idx[0]) or {}
    owner = _binding_of_sections(r, ms)

    clips: List[AnimClip] = []
    keys: Dict[str, List[float]] = {}

    for i, cls in enumerate(r.classNames):
        if cls == "MovieSceneSkeletalAnimationSection":
            p = r.read_export(i) or {}
            rng = p.get("SectionRange") or {}
            a, b = rng.get("lower", 0), rng.get("upper", 0)
            if b <= a:
                continue   # zero-length parking slots between takes
            ref = str((p.get("Params") or {}).get("RefOnDisconnected") or "")
            actor = _strip_ev(owner.get(i, ""), ev)
            clip = _strip_ev(ref, ev)
            if actor and clip.startswith(actor + "_"):
                clip = clip[len(actor) + 1:]
            clips.append(AnimClip(actor=actor or "?", clip=clip or "anim",
                                  start=a, end=b))
            keys.setdefault(actor or "?", []).extend(_channel_times(p))
        elif cls in ("MovieScene3DTransformSection", "MovieSceneFloatSection"):
            p = r.read_export(i) or {}
            actor = _strip_ev(owner.get(i, ""), ev)
            if actor:
                keys.setdefault(actor, []).extend(_channel_times(p))

    clips.sort(key=lambda c: (c.actor, c.start))
    return clips, {a: sorted(set(t)) for a, t in keys.items() if t}


def _load_light(path: str, usmap) -> Tuple[List[float], int]:
    import transforms as T

    r = T.Reader2(path, usmap)
    ticks: List[float] = []
    contributing = set()
    ms_idx = r.find("MovieScene")
    owner: Dict[int, str] = {}
    if ms_idx:
        owner = _binding_of_sections(r, r.read_export(ms_idx[0]) or {})

    for i, cls in enumerate(r.classNames):
        if cls in ("MovieSceneFloatSection", "MovieSceneBoolSection",
                   "MovieSceneColorSection"):
            p = r.read_export(i) or {}
            times = _channel_times(p)
            if times:
                ticks.extend(times)
                contributing.add(owner.get(i, i))
    return sorted(set(ticks)), len(contributing)


def load(content_dir: Optional[str], usmap_path: Optional[str],
         area: Optional[str], ev: str) -> Optional[SceneKeys]:
    """Keys for one scene, or None when the assets are not reachable.

    `content_dir` is the End/Content folder; the scene's loose assets live at
    `Cut/Game/<area>/<EV>/`.
    """
    if not content_dir or not usmap_path or not area:
        return None
    if not os.path.isfile(usmap_path):
        return None
    ev_dir = os.path.join(content_dir, "Cut", "Game", area, ev)
    char_path = os.path.join(ev_dir, ev + "_Character.uasset")
    light_path = os.path.join(ev_dir, ev + "_Light.uasset")
    if not os.path.isfile(char_path) and not os.path.isfile(light_path):
        return None

    try:
        usmap = _usmap(usmap_path)
    except Exception:
        return None

    out = SceneKeys()
    if os.path.isfile(char_path):
        try:
            out.clips, out.actor_keys = _load_character(char_path, usmap, ev)
        except Exception:
            pass   # a character file that will not parse costs its rows, not the scene
    if os.path.isfile(light_path):
        try:
            out.light_keys, out.light_bindings = _load_light(light_path, usmap)
        except Exception:
            pass
    return None if out.empty else out


def build_key_lanes(keys: Optional[SceneKeys]) -> List[Any]:
    """Lanes for the timeline: one per animated actor, one for lighting.

    An actor's row holds its clip blocks *and* its key ticks - the marks are
    drawn along the bottom of the row, so a join landing between keys is
    visible right where the clip is.
    """
    from .characters import canonical
    from .lanes import Lane, LaneItem

    if not keys:
        return []
    lanes: List[Lane] = []

    by_actor: Dict[str, List[AnimClip]] = {}
    for c in keys.clips:
        by_actor.setdefault(c.actor, []).append(c)
    actors = sorted(set(by_actor) | set(keys.actor_keys))

    for actor in actors:
        clips = by_actor.get(actor, [])
        ticks = keys.actor_keys.get(actor, [])
        lane = Lane(
            id="anim:" + actor,
            label="Anim %s (%d clip%s, %d keys)"
            % (actor, len(clips), "" if len(clips) == 1 else "s", len(ticks)),
            kind="anim",
            cls="anim",
            range_row=False,
            items=[
                LaneItem(
                    type="AnimClip",
                    props={"actor": c.actor, "clip": c.clip,
                           "start": c.start, "end": c.end},
                    range=(c.start, c.end),
                    name=c.clip,
                    who=canonical(c.actor),
                    source=c,
                )
                for c in clips
            ],
        )
        lane.ticks = ticks
        lanes.append(lane)

    if keys.light_keys:
        lane = Lane(
            id="lightkeys",
            label="Light keys (%d, %d bindings)"
            % (len(keys.light_keys), keys.light_bindings),
            kind="anim",
            cls="light",
            range_row=False,
            items=[],
        )
        lane.ticks = keys.light_keys
        lanes.append(lane)
    return lanes
