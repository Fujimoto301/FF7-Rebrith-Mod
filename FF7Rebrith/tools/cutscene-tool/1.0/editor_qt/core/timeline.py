"""
The shape of a timeline JSON, as produced by extract_timeline.py, and a
`Cutscene` facade that turns it into the handful of derived views the rest of
the app actually wants.

Nothing here mutates. Everything downstream reads a Cutscene and keeps its own
edit state separately, so "what the game contains" and "what we are changing
about it" never get tangled - that separation is what makes new features cheap
to add.

Raw dicts are kept alongside the typed views on purpose: cue descriptors are
written into the edit plan verbatim, and the plan is a contract with
patcher.py. Retyping a subtitle into a dataclass and back would be one more
place for that contract to drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .units import TimeBase, TickRange, parse_range


@dataclass(frozen=True)
class CameraCut:
    """A camera cut, numbered the way the UI labels them (C01, C02...)."""

    id: int
    name: str
    range: TickRange
    section: Dict[str, Any]


@dataclass(frozen=True)
class VoiceLine:
    tick: float
    name: str
    actor: str
    text: str
    #: natural length of the recording in seconds, defaulted to 1 when unknown
    duration: float
    #: duration exactly as extracted - None when the VO file was never found
    raw_duration: Optional[float]
    props: Dict[str, Any]


@dataclass(frozen=True)
class Subtitle:
    label: str
    start: float
    end: float
    text: str
    actor: str
    raw: Dict[str, Any]


def pair_subtitles(events: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """`_Text` on/off events paired into one range per line on screen.

    Paired per LANGUAGE, then merged. 44 lines in this game carry a
    per-language variant of themselves - the same label opening two or three
    times, at ticks up to a couple of seconds apart, one per EEndCutLangType.
    Pairing on the label alone walks straight through those: the German "on" is
    still open when the Japanese "off" arrives, so those two get paired with
    each other and the events left over are dropped on the floor. The block the
    editor draws is then one variant's range, attributed to whichever pair
    happened to close first, and the other variants have no block at all.

    A line is one thing on screen whatever language it is read in, so the
    variants are merged back into a single range spanning all of them. Two
    separate uses of one label never overlap - measured, 0 of 86 consecutive
    pairs - so merging by overlap cannot fuse two distinct lines into one
    block.

    Shared with `extract_timeline.py`, which writes the same ranges into the
    timeline JSON for the browser viewer. One implementation, because two would
    disagree eventually and the disagreement would be invisible.
    """
    paired: List[Dict[str, Any]] = []
    open_by_key: Dict[Any, Dict[str, Any]] = {}
    for e in sorted([x for x in events if x.get("tick") is not None],
                    key=lambda x: x["tick"]):
        p = e.get("props") or {}
        label = p.get("TextLabel")
        if label is None:
            continue
        key = (label, p.get("Language"))
        if p.get("Enable"):
            open_by_key[key] = e
        elif key in open_by_key:
            st = open_by_key.pop(key)
            paired.append({"label": label,
                           "start": st["tick"], "end": e["tick"],
                           "text": st.get("text"), "actor": st.get("actor")})
    merged: List[Dict[str, Any]] = []
    for r in sorted(paired, key=lambda x: (x["label"], x["start"])):
        prev = merged[-1] if merged else None
        if (prev and prev["label"] == r["label"]
                and r["start"] < prev["end"] and prev["start"] < r["end"]):
            prev["start"] = min(prev["start"], r["start"])
            prev["end"] = max(prev["end"], r["end"])
            prev["text"] = prev["text"] or r["text"]
            prev["actor"] = prev["actor"] or r["actor"]
            continue
        merged.append(dict(r))
    merged.sort(key=lambda x: x["start"])
    return merged


@dataclass(frozen=True)
class VfxWindow:
    name: str
    raw_name: str
    start: float
    end: Optional[float]
    raw: Dict[str, Any]


@dataclass(frozen=True)
class LipLine:
    actor: str
    voice: str
    #: `[startTick, endTick, phoneme, {viseme: weight}]`
    frames: List[Sequence[Any]]


@dataclass(frozen=True)
class SceneSample:
    """Sampled actor and camera positions, for the stage preview."""

    ev: str
    ticks: List[float]
    fps: float
    step: int
    #: `[x, y, z, yaw]` per sample
    actors: List[Dict[str, Any]]
    #: `[x, y, z, roll, pitch, yaw, fov]` per sample
    cam: List[Optional[List[float]]]
    cuts: List[Sequence[float]]

    @staticmethod
    def of(raw: Optional[Dict[str, Any]]) -> Optional["SceneSample"]:
        if not raw or not raw.get("ticks"):
            return None
        return SceneSample(
            ev=raw.get("ev", ""),
            ticks=list(raw.get("ticks") or []),
            fps=raw.get("fps") or 30,
            step=raw.get("step") or 1,
            actors=list(raw.get("actors") or []),
            cam=list(raw.get("cam") or []),
            cuts=list(raw.get("cuts") or []),
        )


@dataclass(frozen=True)
class AudioInfo:
    file: str
    lang: str = ""
    placed: int = 0
    missing: int = 0
    duration: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def of(raw: Optional[Dict[str, Any]]) -> Optional["AudioInfo"]:
        if not raw or not raw.get("file"):
            return None
        return AudioInfo(
            file=raw["file"],
            lang=raw.get("lang") or "",
            placed=raw.get("placed") or 0,
            missing=raw.get("missing") or 0,
            duration=raw.get("duration") or 0.0,
            raw=raw,
        )


def _s(v: Any) -> str:
    """A non-empty string, or ''. Mirrors the `str()` helper in cues.ts."""
    return v if isinstance(v, str) and v else ""


class Cutscene:
    """Read-only view of one extracted timeline."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.name: str = data.get("cutscene", "")
        self.area: Optional[str] = data.get("area")

        root = (data.get("sequences") or {}).get("Root")
        if not root:
            raise ValueError("timeline for %s has no Root sequence" % self.name)

        meta = root.get("meta") or {}
        self.time = TimeBase(
            tick_resolution=(meta.get("tickResolution") or {}).get("Numerator"),
            display_rate=(meta.get("displayRate") or {}).get("Numerator"),
        )
        self.playback_range: TickRange = parse_range(meta.get("playbackRange")) or (0, 0)
        #: length of the untouched scene, in ticks
        self.total: float = self.playback_range[1] - self.playback_range[0]

        self.cuts: List[CameraCut] = self._build_cuts()
        self.voice: List[VoiceLine] = self._build_voice()
        self.subtitles: List[Subtitle] = self._build_subtitles()
        self.vfx: List[VfxWindow] = self._build_vfx()
        self.lipsync: List[LipLine] = self._build_lipsync()
        self.scene: Optional[SceneSample] = SceneSample.of(data.get("scene"))
        self.audio: Optional[AudioInfo] = AudioInfo.of(data.get("audio"))

    # -- construction ---------------------------------------------------

    def _sections(self, seq: str) -> List[Dict[str, Any]]:
        s = (self.data.get("sequences") or {}).get(seq) or {}
        return list(s.get("sections") or [])

    def _build_cuts(self) -> List[CameraCut]:
        raw = [
            s
            for s in self._sections("Camera")
            if s.get("type") == "MovieSceneCameraCutSection" and s.get("range")
        ]
        pairs = []
        for s in raw:
            r = parse_range(s.get("range"))
            if r:
                pairs.append((s, r))
        pairs.sort(key=lambda p: p[1][0])
        return [
            CameraCut(id=i, name="C%02d" % (i + 1), range=r, section=s)
            for i, (s, r) in enumerate(pairs)
        ]

    def _build_voice(self) -> List[VoiceLine]:
        out: List[VoiceLine] = []
        for e in (self.data.get("events") or {}).get("Voice") or []:
            if e.get("tick") is None:
                continue
            props = e.get("props") or {}
            out.append(
                VoiceLine(
                    tick=e["tick"],
                    name=str(props.get("VoiceName") or ""),
                    actor=e.get("actor") or "",
                    text=e.get("text") or "",
                    duration=e.get("duration") if e.get("duration") else 1.0,
                    raw_duration=e.get("duration"),
                    props=props,
                )
            )
        return out

    def _build_subtitles(self) -> List[Subtitle]:
        # Re-paired from the `_Text` events rather than read straight out of
        # the JSON's `SubtitleRanges`. Both are produced by `pair_subtitles`,
        # so for anything extracted since they are the same list - but 755
        # timelines were extracted before the per-language pairing existed, and
        # doing it here means those get the corrected ranges without every
        # scene having to be extracted again. `SubtitleRanges` is still the
        # fallback for a timeline that carries no raw Text events.
        events = self.data.get("events") or {}
        raw = pair_subtitles(events.get("Text") or [])
        if not raw:
            raw = events.get("SubtitleRanges") or []
        out = [
            Subtitle(
                label=r.get("label", ""),
                start=r.get("start", 0),
                end=r.get("end", 0),
                text=r.get("text") or "",
                actor=r.get("actor") or "",
                raw=r,
            )
            for r in raw
        ]
        out.sort(key=lambda r: r.start)
        return out

    def _build_vfx(self) -> List[VfxWindow]:
        return [
            VfxWindow(
                name=x.get("name", ""),
                raw_name=x.get("raw", ""),
                start=x.get("start", 0),
                end=x.get("end"),
                raw=x,
            )
            for x in (self.data.get("vfx") or [])
        ]

    def _build_lipsync(self) -> List[LipLine]:
        return [
            LipLine(
                actor=ln.get("actor") or "",
                voice=ln.get("voice") or "",
                frames=list(ln.get("frames") or []),
            )
            for ln in (self.data.get("lipsync") or [])
        ]

    # -- derived views --------------------------------------------------

    @property
    def shots(self) -> List[Dict[str, Any]]:
        """Sections on the root sequence that represent whole shots."""
        return [
            s
            for s in self._sections("Root")
            if s.get("type")
            in ("MovieSceneCinematicShotSection", "MovieSceneSubSection")
        ]

    def events(self, key: str) -> List[Dict[str, Any]]:
        """Events of one kind, skipping any with no tick to place them at."""
        group = (self.data.get("events") or {}).get(key)
        if not isinstance(group, list):
            return []
        return [e for e in group if isinstance(e, dict) and e.get("tick") is not None]

    def full_duration(self, v: VoiceLine) -> float:
        """Natural length of a line, floored so a very short one is still grabbable."""
        return max(0.35, v.duration or 1.0)

    def cut_at(self, t: float) -> Optional[CameraCut]:
        for c in self.cuts:
            if c.range[0] <= t < c.range[1]:
                return c
        return None

    def actors_with_visibility(self) -> List[str]:
        """Every actor the scene explicitly shows or hides - the actor panel's list."""
        out = set()
        for group in (self.data.get("events") or {}).values():
            for e in group or []:
                if not isinstance(e, dict):
                    continue
                p = e.get("props") or {}
                name = p.get("ActorName")
                if "Hidden" in p and isinstance(name, str) and name != "None":
                    out.add(name)
        return sorted(out)

    def visibility_commands(self, actor: str) -> List[Sequence[Any]]:
        """`[(tick, hidden)]` for one actor, in time order.

        A pin rewrites these commands, so a pin over a stretch containing none
        does nothing at all - which is easy to draw by accident, since the
        stretch you care about is often the one *after* the last command. The
        UI counts them so it can say so instead of silently no-op-ing.
        """
        out: List[Sequence[Any]] = []
        for group in (self.data.get("events") or {}).values():
            for e in group or []:
                if not isinstance(e, dict) or e.get("tick") is None:
                    continue
                p = e.get("props") or {}
                if p.get("ActorName") == actor and "Hidden" in p:
                    out.append((e["tick"], bool(p["Hidden"])))
        out.sort(key=lambda x: x[0])
        return out

    def voice_by_name(self, name: str) -> Optional[VoiceLine]:
        for v in self.voice:
            if v.name == name:
                return v
        return None

    def subtitle_at(self, t: float) -> Optional[Subtitle]:
        for r in self.subtitles:
            if r.start <= t < r.end:
                return r
        return None

    def summary(self) -> str:
        t = self.time
        return (
            "%g ticks/s · %g fps · %.2fs · %d frames · %d cuts · %d voice lines"
            % (
                t.ticks_per_second,
                t.fps,
                self.total / t.ticks_per_second,
                round(self.total / t.ticks_per_frame),
                len(self.cuts),
                len(self.voice),
            )
        )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "<Cutscene %s %.2fs>" % (self.name, self.total / self.time.ticks_per_second)


def iter_all_events(cs: Cutscene) -> Iterable[Dict[str, Any]]:
    for group in (cs.data.get("events") or {}).values():
        for e in group or []:
            if isinstance(e, dict):
                yield e
