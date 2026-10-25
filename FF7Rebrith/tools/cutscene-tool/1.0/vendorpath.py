"""
vendorpath.py - make UE4Parse importable without asking the user to build it.

pyUE4Parse is not on PyPI (the `UE4Parse` 0.0.1 there is an unrelated stub) and
its setup.py cythonises a texture extension unconditionally, so
`pip install git+...` wants a C compiler. On Windows that means MSVC Build
Tools, which is a wholly unreasonable thing to ask of someone who just wants to
edit a cutscene.

The extension is only used by the texture decoder, which this tool never
calls, and UE4Parse already guards the import and falls back to pure Python.
So a plain copy of the package works. `vendor/UE4Parse` is that copy.

It goes on the path *after* trying a real import, so a developer with their own
checkout installed keeps using it and nothing here shadows it. Only a fresh
unzip, where the import fails, falls through to the vendored copy.
"""

from __future__ import annotations

import os
import sys

VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")

_done = False


def ensure() -> str:
    """Return where UE4Parse is coming from: "installed", "vendored", or "".

    Idempotent and cheap after the first call, because it is called from the
    top of four modules that import each other.
    """
    global _done
    if _done:
        return _source()
    _done = True

    _quiet_texture_warning()

    try:
        import UE4Parse  # noqa: F401
        return "installed"
    except ImportError:
        pass

    if os.path.isdir(os.path.join(VENDOR_DIR, "UE4Parse")):
        # Appended, not inserted: if a real install appears later in the same
        # process it should still win.
        if VENDOR_DIR not in sys.path:
            sys.path.append(VENDOR_DIR)
        try:
            import UE4Parse  # noqa: F401
            return "vendored"
        except ImportError:
            pass
    return ""


def _quiet_texture_warning() -> None:
    """Silence UE4Parse's "Cython based texture decoder is not available".

    It fires on import and reads like something is broken. Nothing is: this
    tool parses MovieScene data and never decodes a texture, so the fallback
    is never even entered. Leaving it visible just trains users to ignore
    warnings, which is the opposite of what we want when a real one appears.
    """
    import logging
    logging.getLogger("UE4Parse.Decoder").setLevel(logging.ERROR)


#: UE4Parse logs these at ERROR while carrying on perfectly well, because the
#: .usmap does not describe some MovieScene channel types. The tool has native
#: readers for exactly those - the monkeypatches at the top of
#: extract_timeline.py and transforms.py - so the message is reporting a gap
#: that has already been filled.
#:
#: It is nine lines per cutscene, which over 755 of them buries anything that
#: matters in several thousand lines of false alarm. So it is off by default
#: and `verbose=True` puts it back.
_EXPECTED_NOISE = (
    "UE4Parse.UObjects",
    "UE4Parse.Decoder",
)


def quiet_expected_noise(verbose: bool = False) -> None:
    """Hide the log lines that are expected, and only those.

    Deliberately a named allowlist rather than a blanket level change on the
    root logger: a genuine UE4Parse failure from a module not on this list
    still comes through, and `--verbose` restores everything.
    """
    import logging
    level = logging.DEBUG if verbose else logging.CRITICAL
    for name in _EXPECTED_NOISE:
        logging.getLogger(name).setLevel(level)


def _source() -> str:
    try:
        import UE4Parse
    except ImportError:
        return ""
    where = os.path.dirname(os.path.abspath(UE4Parse.__file__))
    return "vendored" if where.startswith(VENDOR_DIR) else "installed"


def require() -> None:
    """Same, but say something useful instead of an ImportError traceback."""
    if ensure():
        return
    raise SystemExit(
        "UE4Parse is missing.\n\n"
        "It should be bundled at %s.\n"
        "If you are running from a git checkout rather than a release zip,\n"
        "install it with:\n\n"
        "    py -3 -m pip install pycryptodome lz4 pyUsmap pillow\n"
        "    git clone https://github.com/MinshuG/pyUE4Parse\n\n"
        "and put its UE4Parse folder in vendor/.\n"
        % os.path.join(VENDOR_DIR, "UE4Parse")
    )


if __name__ == "__main__":
    src = ensure()
    if src:
        import UE4Parse
        print("UE4Parse: %s (%s)" % (src, os.path.dirname(UE4Parse.__file__)))
    else:
        print("UE4Parse: not available")
