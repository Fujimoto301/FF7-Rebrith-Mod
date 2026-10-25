"""
Finding cutscenes on disk.

The browser build fetched `/manifest.json` and `/timelines/<ev>.json` over HTTP,
which is why StartEditor.bat has to be running before the editor is usable and
why a stale page could be served from cache. A desktop app just reads the
folder, so there is no server, no cache, and no reason for the manifest to
disagree with what is actually extracted.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .text import fold, plain
from .timeline import Cutscene


@dataclass(frozen=True)
class SceneEntry:
    ev: str
    area: str = ""
    duration: float = 0.0
    cuts: int = 0
    lines: int = 0
    has_audio: bool = False
    path: str = ""
    #: first line of the scene, as `Actor: text` - blank for a wordless scene
    preview: str = ""
    #: name, area, cast and every line of dialogue, folded for matching
    haystack: str = ""

    @property
    def display(self) -> str:
        bits = [self.ev]
        if self.duration:
            bits.append("%.1fs" % self.duration)
        if self.area:
            bits.append(self.area)
        return "  ·  ".join(bits)

    @property
    def meta(self) -> str:
        """The right-hand column of a row in the scene list."""
        bits = []
        if self.duration:
            bits.append("%.1fs" % self.duration)
        if self.area:
            bits.append(self.area)
        return "  ·  ".join(bits)


@dataclass(frozen=True)
class SceneMatch:
    """A scene that matched a search, and the line that matched it."""

    entry: SceneEntry
    #: the stretch of dialogue containing the query - blank if the *name* matched
    hit: str = ""

    @property
    def caption(self) -> str:
        """What to show under the name: the matching line, else the first line."""
        return self.hit or self.entry.preview


class SceneLibrary:
    """The folder of extracted timelines, plus whatever the manifest adds."""

    def __init__(self, timelines_dir: str, manifest_path: Optional[str] = None) -> None:
        self.dir = os.path.abspath(timelines_dir)
        self.manifest_path = manifest_path
        self._manifest: Dict[str, Dict[str, Any]] = {}
        self._entries: List[SceneEntry] = []
        #: ev -> [(actor, line)], filled lazily by search
        self._lines: Dict[str, List[Tuple[str, str]]] = {}

    # -- discovery ------------------------------------------------------

    def load(self) -> List[SceneEntry]:
        self._manifest = self._read_manifest()
        entries: List[SceneEntry] = []
        if os.path.isdir(self.dir):
            for fn in sorted(os.listdir(self.dir)):
                if not fn.endswith(".json"):
                    continue
                ev = fn[:-5]
                m = self._manifest.get(ev) or {}
                entries.append(
                    SceneEntry(
                        ev=ev,
                        area=m.get("area") or "",
                        duration=m.get("dur") or 0.0,
                        cuts=m.get("cuts") or 0,
                        lines=m.get("lines") or 0,
                        has_audio=bool(m.get("audio")),
                        path=os.path.join(self.dir, fn),
                        preview=plain(m.get("preview") or ""),
                        haystack=fold(
                            "%s %s %s" % (ev, m.get("area") or "", m.get("search") or "")
                        ),
                    )
                )
        self._entries = entries
        return entries

    @property
    def entries(self) -> List[SceneEntry]:
        return self._entries

    def _read_manifest(self) -> Dict[str, Dict[str, Any]]:
        path = self.manifest_path
        if not path or not os.path.isfile(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            return {}
        if isinstance(raw, dict):
            return {k: v for k, v in raw.items() if isinstance(v, dict)}
        if isinstance(raw, list):
            return {e["ev"]: e for e in raw if isinstance(e, dict) and e.get("ev")}
        return {}

    # -- loading --------------------------------------------------------

    def path_for(self, ev: str) -> str:
        return os.path.join(self.dir, ev + ".json")

    def load_cutscene(self, ev: str) -> Cutscene:
        path = self.path_for(ev)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                "no timeline for %s - has it been extracted?" % ev
            )
        with open(path, "r", encoding="utf-8") as f:
            return Cutscene(json.load(f))

    def audio_path(self, cs: Cutscene) -> Optional[str]:
        """Absolute path of the mixed preview audio, if one was rendered.

        `audio.file` is relative to the timelines folder, e.g. `audio/EV_X.ogg`.
        """
        if not cs.audio or not cs.audio.file:
            return None
        rel = cs.audio.file.replace("\\", "/").lstrip("/")
        path = os.path.join(self.dir, *rel.split("/"))
        return path if os.path.isfile(path) else None

    #: How many matched scenes get their line quoted. A one-letter query matches
    #: hundreds; the ones past the top of the list are not being read, so they
    #: fall back to the scene's opening line rather than costing a file read.
    RESOLVE_LIMIT = 60

    def search(self, needle: str) -> List["SceneMatch"]:
        """Filter by name, area, cast **or spoken line**.

        Two stages, because the two sources are good at different things.

        The manifest's `search` blob is fast - every line of every scene, no
        file I/O - but it is cast names and dialogue run together with spaces,
        so a snippet cut from it can splice a name onto the front of a line and
        read as though the wrong character said it: "Barret Myrna! Wake up" is
        Barret *saying* "Myrna! Wake up".

        So the blob decides *which* scenes match, and then the scene's own
        subtitle records decide *what* to show: a real actor and a real line.
        Timelines are ~7ms each and the parsed lines are cached, so this stays
        instant for the queries a person actually types.

        A scene whose line cannot be quoted - because the match was on a cast
        name, or because it is past `RESOLVE_LIMIT` - shows its opening line
        instead, and is not counted as a dialogue hit.
        """
        n = fold(needle)
        if not n:
            return [SceneMatch(e, "") for e in self._entries]

        out: List[SceneMatch] = []
        budget = self.RESOLVE_LIMIT
        for e in self._entries:
            if n not in e.haystack:
                continue
            if n in fold(e.ev + " " + e.area):
                out.append(SceneMatch(e, ""))     # matched the name, not a line
                continue
            hit = ""
            if budget > 0:
                budget -= 1
                hit = self._matching_line(e.ev, n)
            out.append(SceneMatch(e, hit))
        return out

    def _matching_line(self, ev: str, folded_needle: str) -> str:
        """`Actor: line` for the first subtitle in `ev` containing the query."""
        for actor, line in self._lines_for(ev):
            if folded_needle in line.lower():
                return ("%s: %s" % (actor, line)) if actor else line
        return ""

    def _lines_for(self, ev: str) -> List[Tuple[str, str]]:
        """Every subtitle in a scene as (actor, line), parsed once and kept."""
        cached = self._lines.get(ev)
        if cached is not None:
            return cached
        lines: List[Tuple[str, str]] = []
        try:
            with open(self.path_for(ev), "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in (data.get("events") or {}).get("SubtitleRanges") or []:
                text = plain(r.get("text") or "")
                if text:
                    lines.append((plain(r.get("actor") or ""), text))
        except Exception:
            lines = []   # a timeline that will not parse is not a search failure
        self._lines[ev] = lines
        return lines
