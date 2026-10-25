"""
Entry point.

    py -3 -m editor_qt                      defaults, next to the tool
    py -3 -m editor_qt --ev EV_FOREE_8510   open a scene straight away
    py -3 -m editor_qt --timelines <dir>    a different set of extractions

Paths come from config.json, written by firstrun.py; see toolconfig.py for the
precedence. Every flag below overrides it for one run without saving, which is
how you point a second copy at a different extraction.

Nothing here talks to the game or writes to disk beyond the window layout, so
it is safe to run while StartEditor.bat is serving v2/v3 in a browser.
"""

from __future__ import annotations

import argparse
import os
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# toolconfig lives at the tool root, next to setup.py, not inside this package.
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)
import toolconfig  # noqa: E402

# argparse dest -> toolconfig key, for the two that are not spelled the same.
_KEY_ALIASES = {"game_dir": "paks", "engine_version": "engine"}


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="editor_qt", description="FF7 Rebirth cutscene editor (native)"
    )
    # Every default is None on purpose: argparse must not invent a value, or
    # there is no way to tell "user asked for this" from "nobody said", and the
    # config file could never win. toolconfig.resolve fills the blanks.
    p.add_argument("--timelines", default=None,
                   help="folder of extracted <EV>.json timelines")
    p.add_argument("--manifest", default=None,
                   help="manifest.json, for areas and durations in the scene list")
    p.add_argument("--ev", default=None, help="cutscene to open on startup")
    p.add_argument("--content", default=None,
                   help="End/Content — enables animation and lighting rows")
    p.add_argument("--usmap", default=None,
                   help="Mappings.usmap, needed to read the assets")
    p.add_argument("--plans", default=None,
                   help="where edit plans are saved and loaded")
    p.add_argument("--game-dir", default=None, help="the game's Paks folder")
    p.add_argument("--rezen", default=None, help="UnrealReZen.exe")
    p.add_argument("--audiomog", default=None)
    p.add_argument("--engine-version", default=None)
    return p.parse_args(argv)


def settings(argv=None):
    """Flags over config.json over discovery. Returns a plain dict."""
    args = parse_args(argv)
    overrides = {}
    for dest, value in vars(args).items():
        if value is None or dest == "ev":
            continue
        overrides[_KEY_ALIASES.get(dest, dest)] = value
    cfg = toolconfig.resolve(overrides, TOOL_DIR)
    cfg["ev"] = args.ev
    return cfg


def _honour_ffmpeg_path(cfg) -> None:
    """Put a configured ffmpeg on PATH, so the rest of the code can find it.

    `core/waveform.py` and `core/mixdown.py` both invoke the bare name -
    `shutil.which("ffmpeg")`, `subprocess.run(["ffmpeg", ...])` - which means
    ffmpeg has to be on PATH and the `ffmpeg` key in config.json was, until
    now, written by setup and read by nobody.

    Prepending its folder here is the smallest fix that makes the key mean
    something: every existing call site keeps working unchanged, and someone
    who keeps ffmpeg in a tools folder rather than on PATH can say so once at
    setup instead of editing their environment.
    """
    import shutil

    configured = cfg.get("ffmpeg")
    if not configured or not os.path.isfile(configured):
        return
    if shutil.which("ffmpeg"):
        return                      # already reachable; leave PATH alone
    folder = os.path.dirname(os.path.abspath(configured))
    os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")


def main(argv=None) -> int:
    cfg = settings(argv)
    _honour_ffmpeg_path(cfg)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        sys.stderr.write(
            "PySide6 is not installed.\n\n"
            "  py -3 -m pip install PySide6\n\n"
            "The browser editors (StartEditor.bat) are unaffected and still work.\n"
        )
        return 2

    from .core.library import SceneLibrary
    from .ui import theme
    from .ui.main_window import MainWindow, ToolConfig

    if not cfg.get("timelines") or not os.path.isdir(cfg["timelines"]):
        sys.stderr.write(
            "No timelines folder at %s\n\n"
            "Run setup first:\n"
            "    py -3 firstrun.py\n\n"
            "or point this run at an existing extraction:\n"
            "    py -3 -m editor_qt --timelines <dir>\n"
            % (cfg.get("timelines") or "<unset>")
        )
        return 2

    app = QApplication(sys.argv[:1])
    app.setApplicationName("FF7R Cutscene Editor")
    app.setStyle("Fusion")
    app.setStyleSheet(theme.STYLESHEET)

    config = ToolConfig(
        content=cfg.get("content"),
        usmap=cfg.get("usmap"),
        game_dir=cfg.get("paks"),
        rezen=cfg.get("rezen"),
        audiomog=cfg.get("audiomog"),
        plans=cfg.get("plans"),
        timelines=cfg.get("timelines"),
        engine=cfg.get("engine") or "GAME_UE4_26",
    )

    library = SceneLibrary(cfg["timelines"], cfg.get("manifest"))
    win = MainWindow(library, start_scene=cfg.get("ev"), config=config)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
