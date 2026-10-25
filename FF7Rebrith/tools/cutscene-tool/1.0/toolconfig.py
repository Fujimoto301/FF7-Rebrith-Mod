"""
toolconfig.py - where the editor's paths come from.

Precedence, highest wins:

  1. command-line flags
  2. config.json, next to this file (written by firstrun.py)
  3. auto-discovery of the layouts this tool has historically sat in
  4. nothing, and the editor degrades - see ToolConfig in
     editor_qt/ui/main_window.py, which is already written to cope

Why a JSON file and not QSettings: firstrun.py, the batch scripts and the
launcher .bat all need to read these paths, and only one of the three has Qt.
A file next to the tool is readable by all of them, survives a copy of the
whole folder to another machine, and can be corrected in Notepad when a drive
letter changes - which is the actual failure mode, not a corrupt registry.

Nothing here touches the game. Reading a config never creates one; only
firstrun.py writes.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Any, Dict, Optional

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_NAME = "config.json"
SCHEMA = 1

# Keys that hold a filesystem path, so `resolve` can quietly drop the ones that
# have stopped existing rather than handing the editor a stale drive letter.
PATH_KEYS = (
    "game_root", "paks", "content", "usmap", "timelines", "manifest",
    "plans", "rezen", "audiomog", "ffmpeg", "oodle",
)

DEFAULTS: Dict[str, Any] = {
    "schema": SCHEMA,
    # "game" when the assets were extracted from an install by gameextract.py,
    # "export" when they came from an FModel/retoc dump the user already had.
    "source": None,
    "game_root": None,     # the FINAL FANTASY VII REBIRTH folder
    "paks": None,          # <game_root>/End/Content/Paks
    "content": None,       # the End/Content we read assets from
    "usmap": None,
    "timelines": None,
    "manifest": None,
    "plans": None,
    "rezen": None,
    "audiomog": None,
    "ffmpeg": None,
    "oodle": None,         # oo2core_9_win64.dll, needed to read containers
    "engine": "GAME_UE4_26",
}


def config_path(tool_dir: str = TOOL_DIR) -> str:
    return os.path.join(tool_dir, CONFIG_NAME)


def exists(tool_dir: str = TOOL_DIR) -> bool:
    """Has setup ever completed? The launcher asks this to decide its mode."""
    return os.path.isfile(config_path(tool_dir))


def load(tool_dir: str = TOOL_DIR) -> Dict[str, Any]:
    """The saved config, or an empty dict. Never raises: a config we cannot
    parse is a config we ignore, because the alternative is an editor that
    will not start until the user finds and deletes a file."""
    try:
        with open(config_path(tool_dir), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save(data: Dict[str, Any], tool_dir: str = TOOL_DIR) -> str:
    """Write config.json atomically, so an interrupted setup cannot leave a
    half-written file that then silently fails to parse."""
    out = dict(DEFAULTS)
    out.update(data)
    out["schema"] = SCHEMA
    path = config_path(tool_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)
    return path


# ---------------------------------------------------------------- discovery

def _first_existing(*candidates: Optional[str]) -> Optional[str]:
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _sibling(name: str, tool_dir: str) -> Optional[str]:
    """Inside the tool folder, or one level up beside it.

    Both are real layouts: a release has everything under the tool folder,
    whereas a working copy sits inside an `End` export next to Content and
    Mappings.usmap. Checking the tool folder first means a shipped copy wins
    over whatever happens to be in the parent.
    """
    return _first_existing(os.path.join(tool_dir, name),
                           os.path.join(os.path.dirname(tool_dir), name))


def _on_path(exe: str) -> Optional[str]:
    return shutil.which(exe)


def _usmap_near(tool_dir: str) -> Optional[str]:
    """Any `*.usmap` beside the tool, or one level up.

    Not just `Mappings.usmap`: the file is not shipped with the tool, so it is
    whatever the user's dumper happened to call it. `Mappings.usmap` wins when
    present, then the newest.
    """
    import glob
    for folder in (tool_dir, os.path.dirname(tool_dir)):
        hits = glob.glob(os.path.join(folder, "*.usmap"))
        if not hits:
            continue
        exact = [h for h in hits
                 if os.path.basename(h).lower() == "mappings.usmap"]
        return exact[0] if exact else max(hits, key=os.path.getmtime)
    return None


def steam_libraries() -> list:
    """Steam library roots, from libraryfolders.vdf.

    Enough parsing to pull the `"path"` values out; this file is a nested VDF
    and a real parser would be more code than the job needs. Returns [] on any
    surprise - a missing Steam is not an error, just one fewer place to look.
    """
    roots = []
    if sys.platform != "win32":
        return roots
    bases = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
        os.path.expandvars(r"%ProgramFiles%\Steam"),
    ]
    for base in bases:
        vdf = os.path.join(base, "steamapps", "libraryfolders.vdf")
        if not os.path.isfile(vdf):
            continue
        try:
            text = open(vdf, "r", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith('"path"'):
                continue
            parts = line.split('"')
            if len(parts) >= 4:
                roots.append(parts[3].replace("\\\\", "\\"))
    return roots


def find_game_root() -> Optional[str]:
    """A Rebirth install, if one is sitting in an obvious place.

    Only ever a suggestion the user confirms - setup shows what it found and
    lets them browse instead. We look for End/Content/Paks rather than the
    folder name, because that is the thing we actually need to read.
    """
    names = ("FINAL FANTASY VII REBIRTH", "FINAL FANTASY VII  REBIRTH")
    for lib in steam_libraries():
        for name in names:
            cand = os.path.join(lib, "steamapps", "common", name)
            if os.path.isdir(os.path.join(cand, "End", "Content", "Paks")):
                return cand
    return None


def paks_for(game_root: Optional[str]) -> Optional[str]:
    if not game_root:
        return None
    p = os.path.join(game_root, "End", "Content", "Paks")
    return p if os.path.isdir(p) else None


def looks_like_export(path: Optional[str]) -> bool:
    """Is this an FModel/retoc dump we can read cutscenes out of?

    The marker is Content/Cut/Game, because that is what batch_build.py walks.
    Accepts either the `End` folder or the Content folder itself, which is the
    distinction users get wrong most often.
    """
    if not path or not os.path.isdir(path):
        return False
    for root in (os.path.join(path, "Content"), path):
        if os.path.isdir(os.path.join(root, "Cut", "Game")):
            return True
    return False


def content_within(path: Optional[str]) -> Optional[str]:
    """Normalise whatever the user pointed at to the End/Content folder."""
    if not path or not os.path.isdir(path):
        return None
    for root in (os.path.join(path, "Content"), path):
        if os.path.isdir(os.path.join(root, "Cut", "Game")):
            return root
    return None


def discover(tool_dir: str = TOOL_DIR) -> Dict[str, Any]:
    """Best guesses with no config and no questions asked.

    This is what makes a fresh copy of the tool start up with the animation
    and lighting rows already working when it happens to be unzipped inside an
    export tree, which is how it was developed.
    """
    found: Dict[str, Any] = {}
    found["content"] = content_within(_sibling("Content", tool_dir)) \
        or content_within(os.path.dirname(tool_dir))
    found["usmap"] = _usmap_near(tool_dir)
    found["rezen"] = _first_existing(os.path.join(tool_dir, "UnrealReZen.exe"),
                                     _on_path("UnrealReZen.exe"))
    found["audiomog"] = _first_existing(_sibling("AudioMog.exe", tool_dir),
                                        _on_path("AudioMog.exe"))
    found["ffmpeg"] = _first_existing(_on_path("ffmpeg"),
                                      os.path.join(tool_dir, "ffmpeg.exe"),
                                      os.path.join(tool_dir, "bin", "ffmpeg.exe"))
    found["oodle"] = _first_existing(os.path.join(tool_dir, "oo2core_9_win64.dll"),
                                     _sibling("oo2core_9_win64.dll", tool_dir))
    found["timelines"] = os.path.join(tool_dir, "browser_v2", "timelines")
    found["manifest"] = os.path.join(tool_dir, "browser_v2", "manifest.json")
    found["plans"] = os.path.join(tool_dir, "plans")
    game = find_game_root()
    if game:
        found["game_root"] = game
        found["paks"] = paks_for(game)
    return {k: v for k, v in found.items() if v}


def resolve(overrides: Optional[Dict[str, Any]] = None,
            tool_dir: str = TOOL_DIR,
            drop_missing: bool = True) -> Dict[str, Any]:
    """The merged view the editor and the batch scripts both run on.

    `drop_missing` throws away paths that no longer exist, which is the common
    case after a drive letter changes or a game is uninstalled. Dropping is
    better than keeping: ToolConfig already explains a missing path in the UI,
    whereas a dead path produces a parse error three layers down.
    """
    merged = dict(DEFAULTS)
    merged.update(discover(tool_dir))
    merged.update({k: v for k, v in load(tool_dir).items() if v is not None})
    if overrides:
        merged.update({k: v for k, v in overrides.items() if v is not None})
    if drop_missing:
        for key in PATH_KEYS:
            # timelines/plans are allowed not to exist yet - they get created.
            if key in ("timelines", "plans"):
                continue
            if merged.get(key) and not os.path.exists(merged[key]):
                merged[key] = None
    return merged


if __name__ == "__main__":
    print(json.dumps(resolve(), indent=2, sort_keys=True))
