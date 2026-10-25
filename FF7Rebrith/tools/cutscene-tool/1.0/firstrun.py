"""
firstrun.py - point this at the game and it builds everything the editor needs.

    py -3 firstrun.py                       ask, offering whatever it can find
    py -3 firstrun.py "D:\\...\\REBIRTH"      a game install
    py -3 firstrun.py --export "D:\\...\\End" an FModel/retoc dump you already have
    py -3 firstrun.py --game <path> --yes    no questions, for scripting

What it does, in order
----------------------
1. Works out whether it was handed a game install or an export tree.
2. From a game install: copies Oodle out of it, then reads the containers and
   writes a loose Zen export tree (`gameextract.py`).
3. Rebuilds the subtitle tables FModel would have exported (`txtres.py`).
4. Extracts all 755 cutscene timelines and the manifest (`batch_build.py`).
5. Writes `config.json`, which is what tells the editor it has been set up.

What it deliberately does not do
--------------------------------
**No audio.** Building every scene's voice, music and waveform peaks produces
about 2.8 GB and takes hours. The editor does not need it: `mixdown.render`
builds the preview from the per-cue sources on demand and caches the result, so
audio arrives scene by scene as you open scenes. Checked against the 77 scenes
in the reference extraction that have no pre-rendered .ogg - they preview fine.

**No HTML.** The 755 browser viewer pages are 182 MB and the desktop editor
reads none of them, so `batch_build.py` is run with `--no-html`.

Safe to re-run. Every step skips what is already there, so an interrupted setup
continues rather than starting again.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toolconfig
import vendorpath

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACT_DIR = os.path.join(TOOL_DIR, "extracted")
# ------------------------------------------------------------------ plumbing

def say(msg: str = "") -> None:
    print(msg, flush=True)


def head(n: int, total: int, msg: str) -> None:
    say()
    say("[%d/%d] %s" % (n, total, msg))
    say("-" * (len(msg) + 8))


def ask(prompt: str, default: str = "") -> str:
    try:
        got = input("  %s " % prompt).strip().strip('"')
    except EOFError:
        return default
    return got or default


def yes_no(prompt: str, default: bool = True, assume: bool = False) -> bool:
    if assume:
        return True
    suffix = "[Y/n]" if default else "[y/N]"
    got = ask("%s %s" % (prompt, suffix)).lower()
    if not got:
        return default
    return got.startswith("y")


def die(msg: str):
    say()
    say("  " + msg.replace("\n", "\n  "))
    say()
    raise SystemExit(1)


# ---------------------------------------------------------------- the pieces

# Rebirth links Oodle statically, so - unlike most Unreal games - there is no
# copy in the install to borrow. Walking 150 GB of game folder to come up empty
# is just a slow way to fail, so setup does not try. It looks beside the tool,
# accepts the open `ooz` decompressor if it is installed, and otherwise asks.


def pip_install(package: str, why: str, licence: str,
                assume_yes: bool = False) -> bool:
    """Offer to install a package, and do it. Returns True if it imported.

    Printing a command and asking the user to go and run it is worse than
    running it: they have to leave setup, find a prompt, get the interpreter
    right (`py -3` is not `python` on most Windows boxes), and come back. The
    launcher already installs PySide6 this way, so suggesting a command here
    was just inconsistent.

    The licence is named in the prompt rather than buried in a readme, because
    for `pyooz` that is the whole reason it is a question at all: it is GPLv3
    and this tool is MIT, so pulling it in is the user's decision to make. We
    never redistribute it - this installs into their own environment, at their
    say-so.
    """
    import importlib
    import subprocess

    module = {"pyooz": "ooz",
              "imageio-ffmpeg": "imageio_ffmpeg"}.get(package, package)
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        pass

    say()
    say("  %s can be installed for you:" % package)
    say("      %s   (%s)" % (why, licence))
    if not yes_no("Install it now?", True, assume_yes):
        return False

    say()
    say("  installing %s..." % package)
    # -q because the interesting lines are ours; pip still prints errors.
    rc = subprocess.call([sys.executable, "-m", "pip", "install", "-q", package])
    if rc != 0:
        say("  pip exited with code %d." % rc)
        return False

    # A fresh install lands in site-packages that this process has already
    # scanned, so the finder needs telling before the import will see it.
    importlib.invalidate_caches()
    try:
        importlib.import_module(module)
    except ImportError as e:
        say("  installed, but %s still will not import (%s)." % (module, e))
        return False
    say("  %s is ready." % package)
    return True


def ensure_oodle(assume_yes: bool = False) -> Optional[str]:
    """Settle how containers will be decompressed, or explain and stop.

    Returns the DLL path when one is used, or None when `ooz` will be. Either
    way `gameextract.preload_oodle` makes the final choice; this exists to get
    the file in place and to say something useful when there is nothing to use.
    """
    import gameextract

    local = gameextract.find_oodle_dll(TOOL_DIR, os.path.dirname(TOOL_DIR))
    if local:
        say("  %s" % local)
        if os.path.dirname(os.path.abspath(local)) != TOOL_DIR:
            dest = os.path.join(TOOL_DIR, os.path.basename(local))
            try:
                shutil.copy2(local, dest)
                say("  copied it next to the tool")
                return dest
            except OSError:
                pass
        return local

    try:
        import ooz  # noqa: F401
        say("  using the ooz decompressor (no Oodle DLL needed)")
        return None
    except ImportError:
        pass

    # Nothing found. The quickest fix is one keystroke, so offer that first
    # and only fall back to hunting for a DLL if it is declined or fails.
    if pip_install("pyooz", "an open-source Oodle decompressor",
                   "GPLv3 - installed into your Python, never shipped here",
                   assume_yes):
        return None

    say()
    say(gameextract.OODLE_GUIDANCE.rstrip())
    say()
    if assume_yes:
        die("No Oodle available, pyooz did not install, and --yes means there\n"
            "is nothing to prompt for. Pass a DLL another way, or install\n"
            "pyooz by hand.")

    given = ask("path to an oo2core_*_win64.dll (blank to give up):")
    if not given:
        die("Cannot read the game's containers without Oodle.\n\n"
            "If you have an FModel or retoc export already, setup can use that\n"
            "instead - re-run with:  py -3 firstrun.py --export <End folder>")
    if not os.path.isfile(given):
        die("No such file: %s" % given)
    dest = os.path.join(TOOL_DIR, os.path.basename(given))
    try:
        shutil.copy2(given, dest)
    except OSError as e:
        die("Could not copy it next to the tool: %s" % e)
    say("  copied to %s" % dest)
    return dest


# A .usmap is a dump of the game's own type information, and it is **not
# shipped** with this tool - it is Square Enix's data, not ours to redistribute.
# Nothing parses without one, so this is a hard prerequisite like Python, and
# setup has to be good at asking for it rather than just complaining.

USMAP_GLOB = "*.usmap"
USMAP_MAGIC = 0x30C4

USMAP_GUIDANCE = """\
  A .usmap file describes the game's own types, and every asset in Rebirth is
  stored in a form that cannot be read without one. It is the game's data rather
  than this tool's, so it is not included here.

  It is not in the game folder either - it has to be dumped from the game while
  it is running, with a mappings dumper. Anything that produces a UE4.26-era
  .usmap works; the ones people generally use are Dumper-7 and the UE4SS
  mappings dumper, and retoc's companion `jmap`.

  The dump has to come from the same build of the game you are editing. After a
  patch, an old .usmap will either fail to parse an asset or - worse - parse it
  wrongly, so re-dump when the game updates.

  If you already have one from your other Rebirth modding, point setup at the
  file or at the folder holding it.
"""


def usmap_problem(path: str) -> Optional[str]:
    """None when this looks like a usable .usmap, otherwise why it is not.

    Worth checking at setup rather than letting it fail several layers down
    inside a parse, where the error says nothing about the file you chose.
    """
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError as e:
        return "could not be read (%s)" % e
    if len(head) < 10:
        return "is too short to be a .usmap"
    magic = int.from_bytes(head[0:2], "little")
    if magic != USMAP_MAGIC:
        return ("does not start with the .usmap magic (got 0x%04X, expected "
                "0x%04X) - is it really a mappings dump?" % (magic, USMAP_MAGIC))
    version = head[2]
    # Version 0 puts the compression method straight after the version byte.
    # Later versions can carry an engine-version block first, which we do not
    # need to decode just to sanity-check the file.
    if version == 0 and head[3] != 0:
        return ("is compressed (method %d). The reader in zenasset.py only "
                "handles uncompressed dumps - re-export it without "
                "compression." % head[3])
    return None


def find_usmap(*places: Optional[str]) -> Optional[str]:
    """First usable .usmap among the given files and folders.

    Accepts a folder as readily as a file, because people keep a folder of dumps
    rather than one file at a known path, and accepts any name - dumpers are not
    consistent about calling it Mappings.usmap. A file named exactly
    Mappings.usmap wins, then the newest.
    """
    import glob as _glob

    for place in places:
        if not place:
            continue
        if os.path.isfile(place):
            if usmap_problem(place) is None:
                return place
            continue
        if not os.path.isdir(place):
            continue
        hits = [h for h in _glob.glob(os.path.join(place, USMAP_GLOB))
                if usmap_problem(h) is None]
        if not hits:
            continue
        preferred = [h for h in hits
                     if os.path.basename(h).lower() == "mappings.usmap"]
        if preferred:
            return preferred[0]
        return max(hits, key=os.path.getmtime)
    return None


def ensure_usmap(cfg: dict, given: Optional[str] = None,
                 assume_yes: bool = False) -> str:
    """Settle which .usmap to use, copying it next to the tool once found.

    The copy is the point: it means this is asked once, not every time setup
    runs, and the path recorded in config.json keeps working if the original
    folder moves.
    """
    found = find_usmap(given, cfg.get("usmap"), TOOL_DIR,
                       os.path.dirname(TOOL_DIR))
    if not found and given:
        # They named something specific and it was not usable - say why, rather
        # than silently falling through to a prompt as if they had said nothing.
        if os.path.exists(given):
            problem = usmap_problem(given) if os.path.isfile(given) \
                else "contains no usable .usmap"
            die("%s %s" % (given, problem))
        die("No such file or folder: %s" % given)

    if not found:
        say()
        say(USMAP_GUIDANCE.rstrip())
        say()
        if assume_yes:
            die("No .usmap found and running with --yes, so there is nothing to\n"
                "prompt for. Pass --usmap <file or folder>.")
        answer = ask("path to a .usmap file, or the folder holding one "
                     "(blank to give up):")
        if not answer:
            die("Setup cannot continue without a .usmap.")
        found = find_usmap(answer)
        if not found:
            if os.path.isfile(answer):
                die("%s %s" % (answer, usmap_problem(answer)))
            if os.path.isdir(answer):
                die("No usable .usmap in %s" % answer)
            die("No such file or folder: %s" % answer)

    say("  %s" % found)
    if os.path.dirname(os.path.abspath(found)) != TOOL_DIR:
        dest = os.path.join(TOOL_DIR, os.path.basename(found))
        try:
            shutil.copy2(found, dest)
            say("  copied it next to the tool, so this is only asked once")
            return dest
        except OSError as e:
            say("  (could not copy it next to the tool: %s - using it in "
                "place)" % e)
    return found


def run_extract(game_root: str, usmap: str, oodle: Optional[str],
                extract_dir: str = EXTRACT_DIR) -> str:
    """Containers -> a loose Zen export tree under <extract_dir>/End.

    Measured at 62.7 KB a package over 24,477 of them, so the full 164,796
    comes to about 10 GB. Worth being able to put that on another drive rather
    than wherever the tool was unzipped.
    """
    import gameextract

    out = os.path.join(extract_dir, "End")
    paks = gameextract.find_paks(game_root)
    say("  reading %s" % paks)

    backend = gameextract.preload_oodle(oodle, (TOOL_DIR,))
    say("  oodle via %s" % backend)
    provider, mounted = gameextract.open_provider(paks, usmap)
    say("  mounted %d container(s)" % mounted)

    stats = gameextract.extract(provider, out, progress=gameextract._progress)
    say()
    say("  %d packages, %d written, %d already present"
        % (stats["total"], stats["written"], stats["skipped"]))
    if stats["essential"] == 0:
        die("Nothing was found under Cut/Game/, so no cutscenes were\n"
            "extracted. The containers mounted but hold something other than\n"
            "what we expected - is this really a Rebirth install?")
    if stats["failed"]:
        say("  %d package(s) failed:" % stats["failed"])
        for e in stats["errors"][:5]:
            say("    ! %s" % e)

    say()
    say("  subtitle tables...")
    content = os.path.join(out, "Content")
    side = gameextract.write_txtres_sidecars(content)
    say("    %d written, %d already present, %d failed"
        % (side["made"], side.get("skipped", 0), side["failed"]))
    for u in side["unparsed"][:5]:
        say("    ! %s" % u)

    say()
    say("  voice durations...")
    vo = gameextract.write_vo_duration_sidecars(content)
    say("    %d written, %d already present, %d without audio"
        % (vo["made"], vo.get("skipped", 0), vo["failed"]))
    return out


def run_timelines(content: str, usmap: str, out_dir: str,
                  limit: int = 0, verbose: bool = False) -> int:
    """All 755 timelines plus the manifest. The slow step, and resumable."""
    cut_game = os.path.join(content, "Cut", "Game")
    if not os.path.isdir(cut_game):
        die("No Cut/Game under %s - nothing to extract." % content)

    cmd = [sys.executable, os.path.join(TOOL_DIR, "batch_build.py"),
           cut_game, usmap, out_dir, "--no-html"]
    if not verbose:
        cmd.append("--quiet")
    if limit:
        cmd += ["--limit", str(limit)]
    say("  %s" % " ".join(os.path.basename(c) if i == 1 else c
                          for i, c in enumerate(cmd[1:], 1)))
    say()
    # Streamed rather than captured: this runs for a long time and the user
    # needs to see it moving.
    return subprocess.call(cmd, cwd=TOOL_DIR)


#: The three things that are not required but gate a feature each. Until now
#: setup discovered them silently and mentioned the missing ones in its closing
#: summary - after the fifteen-minute timeline build, by which point the user
#: has stopped reading and the line scrolls past. Asking up front costs one
#: prompt and means nobody finds out their Build button is dead a week later.
#:
#: (name, what it gates, what to look for, where it usually comes from)
OPTIONAL = (
    ("ffmpeg", "preview audio and the waveform", "ffmpeg",
     "ffmpeg.org, or any build already on your machine. Give the path to\n"
     "     ffmpeg.exe and setup will put its folder on PATH for the editor."),
    ("rezen", "Build & install", "UnrealReZen.exe",
     "github.com/rm-NoobInCoding/UnrealReZen - not bundled here because it\n"
     "     is GPL v3 and shipping the binary without its source would not\n"
     "     honour that."),
    ("audiomog", "BGM in the preview mix", "AudioMog.exe",
     "the AudioMog release page. Only needed if you want music in previews;\n"
     "     voice and SE work without it."),
)


def install_ffmpeg(assume_yes: bool) -> Optional[str]:
    """Offer to install a static ffmpeg, and put it where the code looks.

    `imageio-ffmpeg` ships a self-contained ffmpeg build and tells you where it
    put it. The catch is the filename: it lands as `ffmpeg-linux-x86_64-v7.0.2`
    or similar, and every call site in `core/waveform.py` and `core/mixdown.py`
    runs the bare name `ffmpeg`, so `shutil.which` would never find it.

    So it gets linked (or copied, on Windows) next to the tool under the plain
    name, and `editor_qt/app.py` puts the tool folder on PATH at startup. That
    keeps all four call sites untouched.
    """
    if not pip_install("imageio-ffmpeg",
                       "a self-contained ffmpeg build, about 80 MB",
                       "the wrapper is BSD; the ffmpeg binary it fetches is "
                       "LGPL/GPL", assume_yes):
        return None
    try:
        import imageio_ffmpeg
        src = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:                              # noqa: BLE001
        say("  installed, but could not locate the binary (%s)." % e)
        return None
    if not src or not os.path.isfile(src):
        say("  installed, but the binary is missing.")
        return None

    dest = os.path.join(TOOL_DIR, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if os.path.abspath(src) == os.path.abspath(dest):
        return dest
    try:
        if os.path.exists(dest):
            return dest
        if os.name == "nt":
            shutil.copy2(src, dest)
            say("  copied ffmpeg next to the tool")
        else:
            os.symlink(src, dest)
            say("  linked ffmpeg next to the tool")
    except OSError as e:
        # Not fatal: the binary exists, it is just not on PATH under the plain
        # name. Record where it is and let the user decide.
        say("  could not place it next to the tool (%s)" % e)
        return src
    return dest


def ensure_optional(cfg: dict, overrides: dict, assume_yes: bool) -> dict:
    """Offer to fill in the optional tools. Never blocks - each one skipped
    just means the feature it gates stays off, which the editor already
    explains in place."""
    import shutil as _sh

    out = {}
    for key, gates, looks_for, where in OPTIONAL:
        given = overrides.get(key)
        found = None
        if given and os.path.isfile(given):
            found = given
        elif given and os.path.isdir(given):
            cand = os.path.join(given, looks_for)
            found = cand if os.path.isfile(cand) else None
        if not found:
            existing = cfg.get(key)
            if existing and os.path.isfile(existing):
                found = existing
        if not found and key == "ffmpeg":
            found = _sh.which("ffmpeg")
        if not found:
            found = find_near(looks_for)

        if found:
            say("  %-9s %s" % (key, found))
            out[key] = found
            continue

        say("  %-9s not found - %s will be unavailable" % (key, gates))

        # ffmpeg is the one of the three we can fetch ourselves.
        if key == "ffmpeg":
            got = install_ffmpeg(assume_yes)
            if got:
                out[key] = got
                continue

        if assume_yes:
            continue
        say("     %s" % where)
        answer = ask("   path to %s (blank to skip):" % looks_for)
        if not answer:
            continue
        if os.path.isdir(answer):
            answer = os.path.join(answer, looks_for)
        if not os.path.isfile(answer):
            say("     no %s there - skipping" % looks_for)
            continue
        out[key] = answer
        say("     using %s" % answer)
    return out


def find_near(name: str) -> Optional[str]:
    """`name` beside the tool, or one level up."""
    for folder in (TOOL_DIR, os.path.dirname(TOOL_DIR)):
        cand = os.path.join(folder, name)
        if os.path.isfile(cand):
            return cand
    return None


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _oodle_for_config() -> Optional[str]:
    """Whichever DLL sits beside the tool, so later runs need no search."""
    import gameextract
    return gameextract.find_oodle_dll(TOOL_DIR)


# --------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="firstrun",
        description="Set up the FF7 Rebirth cutscene editor.")
    ap.add_argument("path", nargs="?",
                    help="a Rebirth install, or an FModel export tree")
    ap.add_argument("--game", help="treat the path as a game install")
    ap.add_argument("--export", help="treat the path as an FModel export tree")
    ap.add_argument("--yes", action="store_true",
                    help="accept every prompt; for scripting")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N cutscenes (a smoke test)")
    ap.add_argument("--skip-timelines", action="store_true",
                    help="extract assets but do not build timelines")
    ap.add_argument("--verbose", action="store_true",
                    help="show UE4Parse's expected channel-mapping errors")
    ap.add_argument("--usmap", metavar="PATH",
                    help="a .usmap file, or a folder holding one. Required the "
                         "first time; copied next to the tool afterwards")
    ap.add_argument("--ffmpeg", metavar="PATH",
                    help="ffmpeg.exe, or the folder holding it")
    ap.add_argument("--rezen", metavar="PATH",
                    help="UnrealReZen.exe, or the folder holding it")
    ap.add_argument("--audiomog", metavar="PATH",
                    help="AudioMog.exe, or the folder holding it")
    ap.add_argument("--extract-to", default=EXTRACT_DIR, metavar="DIR",
                    help="where to put the extracted assets - about 10 GB, so "
                         "another drive is often the right answer "
                         "(default: extracted/ beside the tool)")
    a = ap.parse_args(argv)

    vendorpath.quiet_expected_noise(a.verbose)

    say()
    say("  FF7 Rebirth cutscene editor - setup")
    say("  " + "=" * 35)

    src = vendorpath.ensure()
    if not src:
        die("UE4Parse is not available and no bundled copy was found in\n"
            "vendor/. A release zip includes it; a git checkout does not.")

    cfg = toolconfig.resolve({}, TOOL_DIR)

    game = a.game or (a.path if a.path and not a.export else None)
    export = a.export or (a.path if a.path and a.export is None and
                          toolconfig.looks_like_export(a.path) else None)
    if export:
        game = None

    # --- decide the source ------------------------------------------------
    if not game and not export:
        found = cfg.get("game_root") or toolconfig.find_game_root()
        say()
        if found:
            say("  Found a Rebirth install at:")
            say("    %s" % found)
            if yes_no("Use it?", True, a.yes):
                game = found
        if not game:
            say()
            say("  Point setup at either:")
            say("    - your FINAL FANTASY VII REBIRTH folder, or")
            say("    - an FModel/retoc export (the 'End' folder)")
            say()
            given = ask("path:")
            if not given:
                die("Nothing to set up from.")
            if toolconfig.looks_like_export(given):
                export = given
                say("  that looks like an export tree")
            else:
                game = given
                say("  treating that as a game install")

    # +1 for the .usmap step and +1 for optional tools, which both routes need.
    steps = 5 if game else 4
    step = 0

    step += 1
    head(step, steps, "Game type mappings (.usmap)")
    usmap = ensure_usmap(cfg, a.usmap, a.yes)

    # --- assets -----------------------------------------------------------
    if game:
        game = os.path.abspath(game)
        if not os.path.isdir(game):
            die("No such folder: %s" % game)
        step += 1
        head(step, steps, "Oodle")
        oodle = ensure_oodle(a.yes)

        step += 1
        head(step, steps, "Reading the game containers")
        end_dir = run_extract(game, usmap, oodle, a.extract_to)
        content = os.path.join(end_dir, "Content")
        source = "game"
        paks = toolconfig.paks_for(game)
    else:
        export = os.path.abspath(export)
        content = toolconfig.content_within(export)
        if not content:
            die("No Content/Cut/Game under\n    %s\n\n"
                "That does not look like an FModel export. Point setup at the\n"
                "'End' folder, or at the Content folder inside it." % export)
        step += 1
        head(step, steps, "Using an existing export")
        say("  %s" % content)
        source = "export"
        game = None
        paks = None

    # --- optional tools ---------------------------------------------------
    step += 1
    head(step, steps, "Optional tools")
    extras = ensure_optional(
        cfg, {"ffmpeg": a.ffmpeg, "rezen": a.rezen, "audiomog": a.audiomog},
        a.yes)

    # --- timelines --------------------------------------------------------
    out_dir = os.path.join(TOOL_DIR, "browser_v2")
    if a.skip_timelines:
        say()
        say("  skipping timelines (--skip-timelines)")
    else:
        step += 1
        head(step, steps, "Extracting cutscene timelines")
        say("  755 scenes, a few seconds each. Interrupting is safe - setup")
        say("  resumes where it stopped.")
        t0 = time.time()
        rc = run_timelines(content, usmap, out_dir, a.limit, a.verbose)
        if rc != 0:
            die("batch_build.py exited with code %d. Nothing was saved to\n"
                "config.json, so setup can simply be run again." % rc)
        say("  %.0fs" % (time.time() - t0))

    # --- config -----------------------------------------------------------
    timelines = os.path.join(out_dir, "timelines")
    data = {
        "source": source,
        "game_root": game,
        "paks": paks,
        "content": content,
        "usmap": usmap,
        "timelines": timelines,
        "manifest": os.path.join(out_dir, "manifest.json"),
        "plans": os.path.join(TOOL_DIR, "plans"),
        "rezen": extras.get("rezen") or cfg.get("rezen"),
        "audiomog": extras.get("audiomog") or cfg.get("audiomog"),
        "ffmpeg": extras.get("ffmpeg") or shutil.which("ffmpeg")
        or cfg.get("ffmpeg"),
        "oodle": _oodle_for_config(),
        "engine": cfg.get("engine") or "GAME_UE4_26",
    }
    os.makedirs(data["plans"], exist_ok=True)
    path = toolconfig.save(data, TOOL_DIR)

    # --- report -----------------------------------------------------------
    n = 0
    if os.path.isdir(timelines):
        n = len([f for f in os.listdir(timelines) if f.endswith(".json")])

    say()
    say("  Done")
    say("  " + "=" * 35)
    say("  timelines   : %d" % n)
    say("  assets      : %s" % content)
    say("  config      : %s" % path)
    say()
    off = [gates for key, gates, _l, _w in OPTIONAL if not data.get(key)]
    if off:
        say("  Off for now: %s." % ", ".join(off))
        say("  Re-run setup, or drop the tool beside this one, to enable.")
        say()
    say("  Audio is built per scene as you open scenes, so the first play of")
    say("  a cutscene takes a moment and later ones are instant.")
    say()
    say("  Start the editor with CutsceneEditor.bat")
    say()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        say()
        say("  interrupted - nothing was broken, re-run to continue")
        raise SystemExit(130)
