"""
gameextract.py - pull the assets this tool needs straight out of a Rebirth
install, writing a loose Zen export tree the rest of the pipeline already
knows how to read.

Why this exists
---------------
Everything downstream (`loosezen.py`, `extract_timeline.py`, `patcher.py`,
`build_mod.py`) reads loose Zen `.uasset` files, which until now meant the user
had to dump them with FModel first. That is a second tool, a second download
and a second set of instructions before anyone sees a cutscene.

pyUE4Parse can read the game's own `.utoc`/`.ucas` containers directly, so we
can do the dump ourselves and extract only what we need. The output is
byte-identical to an FModel export of the same packages - `verify` below is
there to prove that rather than assume it.

Why not retoc
-------------
`retoc unpack` takes a .utoc and an output directory and nothing else: no path
filter. Pointed at Rebirth it writes the entire game to disk before we touch a
cutscene. `retoc to-legacy` does filter, but converts Zen to legacy
`uasset+uexp`, which is the one format `loosezen.py` cannot read.

What it cannot get
------------------
`Mappings.usmap` is a reflection dump, not game content - it is produced by a
dumper attached to the running process, so no amount of reading containers
will yield one. A copy ships with the tool.

NOT YET VERIFIED AGAINST A REAL INSTALL. Written against pyUE4Parse's reader
and the layout of an existing FModel export. Run `verify` before trusting it:

    py -3 gameextract.py verify <game_or_paks> <existing_export_End_dir>
"""

from __future__ import annotations

import argparse
import ctypes
import json
import logging
import os
import shutil
import sys
import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendorpath
vendorpath.require()

import toolconfig

OODLE_DLL = "oo2core_9_win64.dll"

# Asset paths we need, as prefixes *relative to Content/*. Anything outside
# these is left in the container: the whole point is not to unpack 100+ GB.
#
# Each entry says which feature dies without it, because the next person to
# trim this list deserves to know what they are turning off.
WANTED: Tuple[Tuple[str, str], ...] = (
    ("Cut/Game/",            "the cutscenes themselves - nothing works without this"),
    ("Cut/Clips/",           "cue type labels (cuetypes.label_events)"),
    ("Sound/Voice/",         "voice lines, durations and lip sync"),
    ("Sound/SE/Cut/",        "sound effect cues"),
    ("Sound/BGM/",           "music cues and repointing"),
    ("DataObject/Field/",    "cutscene order (CutSceneListLevel)"),
    ("Text/",                "subtitle text"),
)

#: Prefixes that fan out per language. The game ships DE, FR, JP and US, so
#: taking all of them more than doubles the extraction - 144,629 voice packages
#: against 36,157 for one language. The editor looks captions up by the language
#: on the event, so extra languages are not useless, just rarely wanted; US is
#: the default and `--lang` adds more.
PER_LANGUAGE = ("Sound/Voice/", "Text/")
DEFAULT_LANGS = ("US",)

# Extraction is pointless without this one, so a run that finds none of it has
# gone wrong somewhere and should say so rather than finish "successfully".
ESSENTIAL_PREFIX = "Cut/Game/"


# --------------------------------------------------------------------- Oodle

#: Any version from 6 up decodes this game; 5 and older cannot. The filename
#: does not matter to us because we load it by explicit path and inject it into
#: UE4Parse, so a copy called oo2core_6 works as well as oo2core_9.
OODLE_GLOB = "oo2core_*_win64.dll"
OODLE_MIN_VERSION = 6

OODLE_GUIDANCE = """\
  The game's containers are Oodle-compressed and Oodle is proprietary, so it
  cannot be bundled here. Rebirth links it statically, so - unlike most Unreal
  games - there is no copy in the install to borrow either.

  Setup offers to install `pyooz` for you, an open-source decompressor that
  needs nothing else. If you declined that, or it failed, the other way is:

     Drop an `oo2core_<n>_win64.dll` (version 6 or newer) next to the tool.
     It ships loose with a number of games:

         ELDEN RING                           oo2core_6_win64.dll
         DEATH STRANDING DIRECTOR'S CUT       oo2core_7_win64.dll
         DOOM Eternal                         oo2core_8_win64.dll
         Indiana Jones and the Great Circle   oo2core_9_win64.dll

     Searching your game folders for "oo2core" is the quickest way to find one.
     Unreal Engine itself ships one too and is free from the Epic launcher.
"""


class OodleLoadError(Exception):
    """A DLL was found but could not be loaded."""

    def __init__(self, path: str, cause: Exception) -> None:
        super().__init__("%s: %s" % (path, cause))
        self.path = path
        self.cause = cause


def find_oodle_dll(*search_dirs: str) -> Optional[str]:
    """Newest `oo2core_<n>_win64.dll` at or above version 6, across the dirs.

    Deliberately does *not* walk a game install: Rebirth statically links
    Oodle, so walking 150 GB of it to come up empty is just a slow way to fail.
    """
    import glob as _glob
    import re as _re

    best = None
    best_ver = -1
    for d in search_dirs:
        if not d or not os.path.isdir(d):
            continue
        for path in _glob.glob(os.path.join(d, OODLE_GLOB)):
            m = _re.search(r"oo2core_(\d+)_win64\.dll$", path, _re.IGNORECASE)
            if not m:
                continue
            ver = int(m.group(1))
            if ver < OODLE_MIN_VERSION:
                continue
            if ver > best_ver:
                best, best_ver = path, ver
    return best


#: UE4Parse's `Decompress` dispatches on an exact string - "Oodle", "Zlib",
#: "Gzip", "LZ4" - but the name comes verbatim out of the container's own
#: compression-method table, and Rebirth spells it lowercase `oodle`. So every
#: read fails with `NotImplementedError: Unknown Compression Method oodle`
#: despite the decompressor being right there.
#:
#: UE's own comparison is case-insensitive, so matching that is the fix rather
#: than a special case for this game.
_METHOD_SPELLINGS = {
    "oodle": "Oodle",
    "zlib": "Zlib",
    "gzip": "Gzip",
    "lz4": "LZ4",
}


def _install_decompress_shim() -> None:
    """Normalise compression-method names before UE4Parse dispatches on them.

    Patched into `IoStoreReader`'s own namespace: it does
    `from ... import Decompress` at module import, so rebinding the name in the
    source module would come too late to matter.
    """
    from UE4Parse.IO import IoStoreReader as reader_mod

    if getattr(reader_mod, "_method_shim_installed", False):
        return
    original = reader_mod.Decompress

    def decompress(buffer, method, decompressSize=0):
        if isinstance(method, str):
            method = _METHOD_SPELLINGS.get(method.strip().lower(), method)
        return original(buffer, method, decompressSize)

    reader_mod.Decompress = decompress
    reader_mod._method_shim_installed = True


def _use_dll(dll_path: str) -> str:
    """Load the real Oodle by explicit path and hand it to UE4Parse.

    Two things to avoid, both in UE4Parse/Oodle.py:

    * `load_lib()` looks for the DLL in `os.getcwd()`, so whether the tool
      works would depend on which folder you launched it from.
    * When it does not find it there, it **downloads one from a Warframe CDN**.
      A modding tool that quietly fetches a binary from a games publisher on
      first run is not something to ship, so that branch is made unreachable.
    """
    import UE4Parse.Oodle as oodle

    try:
        if os.name == "nt":
            lib = ctypes.WinDLL(dll_path)
        else:
            lib = ctypes.CDLL(dll_path)
    except OSError as e:
        # Not fatal on its own: a DLL can be present and unusable - 32-bit,
        # truncated, or simply a Windows DLL on a non-Windows machine - and
        # `ooz` may still be able to do the job. The caller decides.
        raise OodleLoadError(dll_path, e)

    oodle.lib = lib
    oodle.load_lib = lambda: True   # the download path is now unreachable
    _install_decompress_shim()
    return "dll:%s" % os.path.basename(dll_path)


def _use_ooz() -> Optional[str]:
    """Route Oodle decompression through the open `ooz` decompressor.

    `pyooz` exposes `ooz.decompress(data, out_size)`, which is the same
    contract UE4Parse's `Decompress(buffer, decompressLength)` wants, so this
    is a two-line substitution. It is what makes the tool usable on a machine
    with no proprietary DLL at all - and the only thing that makes the reader
    testable off Windows, since the DLL will not load there.

    `UE4Parse/Assets/Objects/Decompress.py` imports `Decompress` from
    `UE4Parse.Oodle` *inside* the call, so patching the module attribute is
    enough; and it asserts the result's length, so this must return exactly
    `decompressLength` bytes.
    """
    try:
        import ooz
    except ImportError:
        return None

    import UE4Parse.Oodle as oodle

    # `Read` hands us `Align(CompressedSize, 16)` bytes - the block padded to
    # the AES block size, whether or not the container is encrypted - and does
    # not pass the true compressed length. Real Oodle ignores trailing bytes;
    # ooz reads past the end of the stream and fails with "Could not decompress
    # requested amount". Measured on a real block: 6782 compressed bytes padded
    # to 6784, failing aligned and succeeding at the exact length.
    #
    # The true length is therefore within 15 bytes of what we were given, so
    # trimming one byte at a time finds it in at most 16 tries on a buffer of a
    # few KB. Bounded, deterministic, and every attempt is validated by ooz
    # itself refusing to produce the wrong number of bytes - plus `verify`
    # byte-compares the result against an independent FModel export.
    _MAX_PAD = 16

    def decompress(buffer: bytes, decompressLength: int):
        raw = bytes(buffer)
        last = None
        for trim in range(_MAX_PAD):
            candidate = raw if trim == 0 else raw[:-trim]
            if not candidate:
                break
            try:
                out = ooz.decompress(candidate, decompressLength)
            except Exception as e:                      # noqa: BLE001
                last = e
                continue
            if len(out) == decompressLength:
                return out
            last = ValueError("ooz returned %d bytes, expected %d"
                              % (len(out), decompressLength))
        raise RuntimeError(
            "ooz could not decompress %d bytes to %d (tried %d paddings): %s"
            % (len(raw), decompressLength, _MAX_PAD, last))

    oodle.Decompress = decompress
    oodle.load_lib = lambda: True
    _install_decompress_shim()
    return "ooz"


def preload_oodle(dll_path: Optional[str] = None,
                  search_dirs: Iterable[str] = (),
                  prefer_ooz: bool = False) -> str:
    """Pick a decompression backend and return a short name for it.

    Order: an explicitly given DLL, then `ooz` if it is installed, then any DLL
    found in `search_dirs`. `prefer_ooz` flips the first two, which is how the
    verification runs on a Linux shell where a Win64 DLL is present but
    unloadable.
    """
    if prefer_ooz:
        got = _use_ooz()
        if got:
            return got

    dll_problem = None
    candidates = []
    if dll_path and os.path.isfile(dll_path):
        candidates.append(dll_path)

    for candidate in candidates:
        try:
            return _use_dll(candidate)
        except OodleLoadError as e:
            dll_problem = e

    got = _use_ooz()
    if got:
        if dll_problem:
            logging.getLogger(__name__).warning(
                "could not load %s (%s); using ooz instead",
                dll_problem.path, dll_problem.cause)
        return got

    found = find_oodle_dll(*search_dirs)
    if found and found != dll_path:
        try:
            return _use_dll(found)
        except OodleLoadError as e:
            dll_problem = e

    detail = ""
    if dll_problem:
        detail = ("  A DLL was found but could not be loaded:\n"
                  "    %s\n"
                  "    %s\n\n"
                  "  Usually it is 32-bit, truncated, or a Windows DLL on a\n"
                  "  non-Windows machine.\n\n" % (dll_problem.path,
                                                  dll_problem.cause))
    raise SystemExit("Cannot read the game's containers without Oodle.\n\n"
                     + detail + OODLE_GUIDANCE)


# ------------------------------------------------------------------ provider

def find_paks(path: str) -> str:
    """Accept the install root, the End folder, or the Paks folder itself.

    Users point at whichever of the three they happen to have open, and being
    fussy about it buys nothing.
    """
    path = os.path.abspath(path)
    candidates = [
        path,
        os.path.join(path, "Paks"),
        os.path.join(path, "Content", "Paks"),
        os.path.join(path, "End", "Content", "Paks"),
    ]
    for c in candidates:
        if os.path.isdir(c) and any(f.lower().endswith(".utoc")
                                    for f in os.listdir(c)):
            return c
    raise SystemExit(
        "No .utoc containers under %s\n\n"
        "Point this at your FINAL FANTASY VII REBIRTH folder, or directly at\n"
        "End/Content/Paks inside it.\n" % path
    )


#: pyUE4Parse substitutes a placeholder partition size for container formats
#: that predate the field, and the placeholder is a real number rather than an
#: unbounded one:
#:
#:     if self.Header.Version < EIoStoreTocVersion.PartitionSize:
#:         self.Header.PartitionCount = 1
#:         self.Header.PartitionSize = 878787
#:
#: Rebirth's containers are version `DirectoryIndex`, i.e. exactly that case.
#: `Read` then computes
#:
#:     partition_index = block.Offset // PartitionSize
#:
#: which for a block 100 MB into the file gives 114, and `FileHandles` holds one
#: stream - so every read dies on `IndexError: list index out of range`. A
#: single partition means the index must always be 0 and the offset must pass
#: through untouched, which is what an effectively unbounded size gives.
#:
#: Patched here rather than in vendor/ so the bundled copy stays an unmodified
#: upstream checkout that can be replaced wholesale.
_UNPARTITIONED = (1 << 63) - 1


def fix_partition_size(provider) -> int:
    """Correct the placeholder partition size on every mounted container."""
    from UE4Parse.IO.IoObjects.FIoStoreTocHeader import EIoStoreTocVersion

    fixed = 0
    seen = set()
    for bucket in ("LoadedContainers", "UnloadedContainers"):
        for container in getattr(provider, bucket, None) or ():
            toc = getattr(container, "TocResource", None)
            header = getattr(toc, "Header", None)
            if header is None or id(header) in seen:
                continue
            seen.add(id(header))
            version = getattr(header, "Version", None)
            if version is None or version >= EIoStoreTocVersion.PartitionSize:
                continue
            if header.PartitionCount <= 1:
                header.PartitionSize = _UNPARTITIONED
                fixed += 1
    return fixed


def open_provider(paks: str, usmap: str, engine: str = "GAME_UE4_26"):
    """A mounted provider over every container in the Paks folder."""
    from UE4Parse.Provider.DefaultFileProvider import DefaultFileProvider
    from UE4Parse.Provider.MappingProvider import MappingProvider
    from UE4Parse.Versions import EUEVersion, VersionContainer

    try:
        ue = getattr(EUEVersion, engine)
    except AttributeError:
        raise SystemExit("Unknown engine version %r. Try GAME_UE4_26.\n" % engine)

    # global.utoc carries script objects and no directory index, so the
    # provider logs an error reading it and carries on. We only ever address
    # packages by name, so an unnamed container has nothing we can use - the
    # message is noise, and loud noise teaches people to ignore real errors.
    import logging
    vfs_log = logging.getLogger("UE4Parse.AbstractVfsFileProvider")
    prior = vfs_log.level
    vfs_log.setLevel(logging.CRITICAL)
    try:
        provider = DefaultFileProvider(paks, VersionContainer(ue))
        provider.initialize()
    finally:
        vfs_log.setLevel(prior)

    # Mounting goes through submit_key even with nothing to decrypt. The key
    # must be None, not a zero key: _mount passes whatever it is handed to
    # ReadDirectoryIndex, so a zero FAESKey makes it attempt AES on plaintext
    # and the mount fails. None is the "unencrypted" value.
    #
    # Containers with no directory index (global.utoc) are skipped by design -
    # we only ever ask for packages by name, so an unnamed container has
    # nothing we can address.
    mounted = provider.submit_key()
    if not mounted:
        raise SystemExit(
            "Mounted 0 containers from %s\n\n"
            "Either the folder holds no readable .utoc/.ucas pairs, or they are\n"
            "encrypted and need a key this tool does not have.\n" % paks
        )

    if not os.path.isfile(usmap):
        raise SystemExit(
            "Mappings.usmap not found at %s\n\n"
            "This is a reflection dump, not game content, so it cannot be\n"
            "extracted from the install. A copy ships with the tool.\n" % usmap
        )
    fixed = fix_partition_size(provider)
    if fixed:
        logging.getLogger(__name__).debug(
            "corrected the partition size on %d container(s)", fixed)

    provider.mappings = MappingProvider(usmap)
    return provider, mounted


# ---------------------------------------------------------------- path logic

def content_relative(vfs_path: str) -> Optional[str]:
    """The part of a container path after `Content/`, or None.

    Container paths carry a mount point whose shape varies by engine version
    and packaging ("../../../End/Content/x", "End/Content/x", "Content/x"), and
    the tool has no business caring which. Cutting at the last `Content/` is
    stable across all of them.
    """
    norm = vfs_path.replace("\\", "/")
    marker = "/Content/"
    idx = norm.rfind(marker)
    if idx >= 0:
        return norm[idx + len(marker):]
    if norm.startswith("Content/"):
        return norm[len("Content/"):]
    return None


#: Container directory-index paths carry **no extension** - a package is listed
#: as `End/Content/Cut/Game/<area>/<EV>/<EV>`, not `<EV>.uasset`. The provider
#: strips extensions when indexing and hangs any .ubulk/.uexp off the entry, so
#: one entry is one package and the loose Zen file FModel writes for it is
#: `<name>.uasset`. Everything downstream globs for *.uasset, so the extension
#: has to be put back on the way out - without it the extraction looks like it
#: worked and nothing can read a single file of it.
ASSET_EXT = ".uasset"


def on_disk_name(rel: str) -> str:
    """The filename an FModel export would use for this package."""
    return rel if os.path.splitext(rel)[1] else rel + ASSET_EXT


def wanted_prefixes(only: Optional[Iterable[str]] = None) -> Tuple[str, ...]:
    if not only:
        return tuple(p for p, _why in WANTED)
    # `--only Cut/Game/8800-FOREE` narrows a re-extraction to one area, which
    # is what you want when a single scene has drifted.
    return tuple(o.replace("\\", "/").lstrip("/") for o in only)


def is_wanted(rel: str, prefixes: Tuple[str, ...],
              langs: Iterable[str] = DEFAULT_LANGS) -> bool:
    for p in prefixes:
        if not rel.startswith(p):
            continue
        for lang_prefix in PER_LANGUAGE:
            if not p.startswith(lang_prefix) and not lang_prefix.startswith(p):
                continue
            # `Sound/Voice/<LANG>/...` and `Text/<LANG>/...`: the segment right
            # after the prefix is the language.
            tail = rel[len(lang_prefix):] if rel.startswith(lang_prefix) else ""
            if tail:
                seg = tail.split("/", 1)[0]
                # Only treat it as a language when it looks like one, so a
                # layout change does not silently drop everything.
                if len(seg) == 2 and seg.isupper():
                    return seg in langs
        return True
    return False


# ---------------------------------------------------------------- extraction

def iter_entries(provider):
    """(vfs_path, entry) for everything mounted, tolerating either shape of
    `provider.files` - it is a storage object in some versions and a plain
    dict in others."""
    files = provider.files
    try:
        items = files.items()
    except AttributeError:
        items = iter(files)
    for item in items:
        try:
            name, entry = item
        except (TypeError, ValueError):
            continue
        yield name, entry


#: Measured at 62.7 KB a package over a 24,477-package extraction, so the full
#: 164,796 comes to about 10 GB. Used only to warn before starting, so being
#: approximate is fine; being absent is not. Without it the failure mode is the
#: one hit in testing: twenty minutes in, 122,000 "No space left on device"
#: errors, and a half-written tree that looks like a successful run until you
#: read the counts.
BYTES_PER_PACKAGE = 64 * 1024


def free_space(path: str) -> Optional[int]:
    """Free bytes on the filesystem that will hold `path`, or None.

    Walks up to the nearest directory that exists, because the target is
    usually about to be created.
    """
    probe = os.path.abspath(path)
    while probe and not os.path.isdir(probe):
        parent = os.path.dirname(probe)
        if parent == probe:
            return None
        probe = parent
    try:
        import shutil as _sh
        return _sh.disk_usage(probe).free
    except Exception:                                   # noqa: BLE001
        return None


def check_space(out_root: str, package_count: int) -> Optional[str]:
    """A sentence about insufficient disk, or None when there is room."""
    need = package_count * BYTES_PER_PACKAGE
    have = free_space(out_root)
    if have is None or have >= need:
        return None
    return ("%s needs roughly %.1f GB for %d packages and has %.1f GB free."
            % (out_root, need / 1073741824.0, package_count,
               have / 1073741824.0))


def extract(provider, out_root: str,
            only: Optional[Iterable[str]] = None,
            dry_run: bool = False,
            langs: Iterable[str] = DEFAULT_LANGS,
            allow_low_space: bool = False,
            progress: Optional[Callable[[int, int, str], None]] = None
            ) -> Dict[str, object]:
    """Write every wanted package to out_root/Content/<relative path>.

    Returns counts and, importantly, the per-prefix tally - a run that writes
    40,000 files but none under Cut/Game/ has not worked, and only the tally
    shows that.
    """
    prefixes = wanted_prefixes(only)
    targets: List[Tuple[str, str, object]] = []

    for vfs_path, entry in iter_entries(provider):
        rel = content_relative(vfs_path)
        if rel is None or not is_wanted(rel, prefixes, langs):
            continue
        targets.append((rel, vfs_path, entry))

    per_prefix: Dict[str, int] = {p: 0 for p in prefixes}
    for rel, _vfs, _e in targets:
        for p in prefixes:
            if rel.startswith(p):
                per_prefix[p] += 1
                break

    total = len(targets)
    written = skipped = failed = 0
    errors: List[str] = []
    space_warning = check_space(out_root, total)

    if not dry_run and space_warning and not allow_low_space:
        raise SystemExit(
            "Not enough disk space.\n\n  %s\n\n"
            "Point --out (or firstrun's --extract-to) at a drive with room, or\n"
            "pass --allow-low-space to try anyway.\n" % space_warning)

    if not dry_run:
        # Key on the path: a tie would otherwise compare the entry
        # objects, and FIoStoreEntry/FPakEntry have no ordering.
        for i, (rel, vfs_path, entry) in enumerate(
                sorted(targets, key=lambda t: (t[0], t[1]))):
            dest = os.path.join(out_root, "Content",
                                on_disk_name(rel).replace("/", os.sep))
            if progress and (i % 200 == 0 or i == total - 1):
                progress(i + 1, total, rel)
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                data = _entry_bytes(entry)
                if data is None:
                    failed += 1
                    errors.append("%s: no data" % rel)
                    continue
                # Same bytes already there? Leave the file alone so mtimes stay
                # meaningful and a re-run is cheap.
                if os.path.isfile(dest) and os.path.getsize(dest) == len(data):
                    with open(dest, "rb") as f:
                        if f.read() == data:
                            skipped += 1
                            continue
                tmp = dest + ".part"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, dest)
                written += 1
            except Exception as e:                      # noqa: BLE001
                failed += 1
                if len(errors) < 20:
                    errors.append("%s: %r" % (rel, e))

    # "Did we get any cutscenes?" is a sanity check on a *full* extraction. A
    # targeted run has been told exactly what to fetch - `--only Cut/Clips/` is
    # a perfectly good request - so the check does not apply and is reported as
    # not applicable rather than as a failure.
    #
    # Within a full run, count anything *under* Cut/Game/ rather than looking
    # the key up: `--only Cut/Game/8800-FOREE/` makes the key that narrower
    # string, and a lookup for "Cut/Game/" would miss it.
    if only:
        essential = None
    else:
        essential = sum(n for pfx, n in per_prefix.items()
                        if pfx.startswith(ESSENTIAL_PREFIX)
                        or ESSENTIAL_PREFIX.startswith(pfx))

    return {
        "total": total,
        "written": written,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
        "per_prefix": per_prefix,
        "essential": essential,
        "space_warning": space_warning,
    }


def _entry_bytes(entry) -> Optional[bytes]:
    """The package's decompressed bytes.

    `get_data()` hands back a BinaryStream over the chunk; what we want on disk
    is exactly those bytes, which is what makes the output comparable to an
    FModel export.
    """
    data = entry.get_data()
    if data is None:
        return None
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    for attempt in ("read", "readBytes"):
        fn = getattr(data, attempt, None)
        if fn is None:
            continue
        try:
            data.seek(0, 0)
        except Exception:                               # noqa: BLE001
            pass
        try:
            raw = fn()
            if raw:
                return bytes(raw)
        except Exception:                               # noqa: BLE001
            continue
    base = getattr(data, "base_stream", None)
    if base is not None:
        try:
            base.seek(0)
            return bytes(base.read())
        except Exception:                               # noqa: BLE001
            pass
    return None


# ----------------------------------------------------------- FModel sidecars

# Two loaders in extract_timeline.py read FModel's *JSON* exports rather than
# the .uasset: `load_subtitles` wants Text/<lang>/<area>_TxtRes.json and
# `load_vo_durations` wants Properties.Duration out of the Sound/Voice JSONs.
# Both return {} when the file is absent, so a container-only extraction still
# produces working timelines - just with no caption text, which you would
# notice immediately in the editor.
#
# So we regenerate the subtitle tables ourselves. `txtres.py` reads
# EndTextResource directly, because pyUE4Parse cannot: the class derives from
# MemoryMappedAsset and a normal parse yields only {Type, Name, Outer,
# Properties}. That reader is checked against FModel's own export of all 142
# areas - 56,157 caption lines, byte-identical - so these sidecars are not a
# lossy approximation of an FModel dump, they are the same thing.
#
# VO durations are not regenerated. They live in SQEXSEADSound and only affect
# how long a voice bar is drawn; `load_vo_durations` degrades to {} and the
# timings still come from the sequence itself.


def write_txtres_sidecars(content_root: str,
                          langs: Optional[Iterable[str]] = None,
                          progress: Optional[Callable[[str], None]] = None
                          ) -> Dict[str, object]:
    """Emit <area>_TxtRes.json beside each extracted <area>_TxtRes.uasset.

    `langs=None` means every language folder that was extracted, because
    `collect_events` looks up captions by the language on the event, not just
    US.
    """
    import txtres

    text_root = os.path.join(content_root, "Text")
    if not os.path.isdir(text_root):
        return {"made": 0, "failed": 0, "skipped": 0, "unparsed": [],
                "note": "no Content/Text was extracted"}

    if langs is None:
        langs = sorted(d for d in os.listdir(text_root)
                       if os.path.isdir(os.path.join(text_root, d)))

    made = failed = skipped = 0
    unparsed: List[str] = []
    for lang in langs:
        d = os.path.join(text_root, lang)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith("_TxtRes.uasset"):
                continue
            src = os.path.join(d, fn)
            dest = os.path.join(d, fn[:-len(".uasset")] + ".json")
            # An FModel export already sitting here is authoritative - never
            # overwrite the user's own dump with ours.
            if os.path.isfile(dest):
                skipped += 1
                continue
            if progress:
                progress("%s/%s" % (lang, fn))
            try:
                payload = txtres.to_fmodel_json(src, lang)
                tmp = dest + ".part"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, default=str)
                os.replace(tmp, dest)
                made += 1
            except Exception as e:                      # noqa: BLE001
                failed += 1
                if len(unparsed) < 10:
                    unparsed.append("%s/%s: %s" % (lang, fn, e))
    return {"made": made, "failed": failed, "skipped": skipped,
            "unparsed": unparsed}


#: `load_vo_durations` reads `Properties.Duration` out of FModel's JSON for each
#: SQEXSEADSound. pyUE4Parse cannot supply it: the asset uses Zen unversioned
#: property serialisation and the parse dies on `SoundNameIndexTable`
#: ("Missing prop mappings for type WeDon'tCare?"), returning no properties at
#: all.
#:
#: Reading it out of the bytes was tried and rejected. The layout looks fixed -
#: a 19-entry name map in all 2,500 assets checked, the float at the same four
#: offsets - but a fixed-offset read matched FModel on only 93.8% of them. A
#: reader that is silently wrong one time in sixteen is worse than none.
#:
#: So the duration is derived from the audio instead, which is the thing the
#: number describes. `audio_build.find_all_hca` already reads the embedded HCA
#: header, where duration is `blocks * 1024 / sample_rate` - no guessing and no
#: schema needed. Checked against FModel's value on 2,500 assets: 100% agree
#: within 0.06s, none further off, though none are bit-exact either. That gap is
#: the encoder rounding up to whole blocks, and 0.06s is one or two frames on a
#: bar that only shows how long a line runs.
VO_DURATION_TOLERANCE_NOTE = "derived from the HCA header, +/-0.06s"


def write_vo_duration_sidecars(content_root: str,
                               langs: Optional[Iterable[str]] = None,
                               progress: Optional[Callable[[str], None]] = None
                               ) -> Dict[str, object]:
    """Emit the per-voice JSON `load_vo_durations` looks for."""
    import audio_build

    voice_root = os.path.join(content_root, "Sound", "Voice")
    if not os.path.isdir(voice_root):
        return {"made": 0, "skipped": 0, "failed": 0,
                "note": "no Sound/Voice was extracted"}

    if langs is None:
        langs = sorted(d for d in os.listdir(voice_root)
                       if os.path.isdir(os.path.join(voice_root, d)))

    made = skipped = failed = 0
    for lang in langs:
        cut = os.path.join(voice_root, lang, "Cut")
        if not os.path.isdir(cut):
            continue
        for area in sorted(os.listdir(cut)):
            adir = os.path.join(cut, area)
            if not os.path.isdir(adir):
                continue
            if progress:
                progress("%s/%s" % (lang, area))
            for ev in sorted(os.listdir(adir)):
                evd = os.path.join(adir, ev)
                if not os.path.isdir(evd):
                    continue
                for fn in sorted(os.listdir(evd)):
                    if not fn.endswith(".uasset"):
                        continue
                    dest = os.path.join(evd, fn[:-len(".uasset")] + ".json")
                    # An FModel export here is authoritative - it carries the
                    # authored value, which is exact.
                    if os.path.isfile(dest):
                        skipped += 1
                        continue
                    try:
                        with open(os.path.join(evd, fn), "rb") as f:
                            streams = audio_build.find_all_hca(f.read())
                        if not streams:
                            failed += 1
                            continue
                        dur = max(st["dur"] for st in streams)
                        if not dur:
                            failed += 1
                            continue
                        payload = [{
                            "Type": "SQEXSEADSound",
                            "Name": fn[:-len(".uasset")],
                            "Properties": {"Duration": round(dur, 3)},
                        }]
                        tmp = dest + ".part"
                        with open(tmp, "w", encoding="utf-8") as f:
                            json.dump(payload, f)
                        os.replace(tmp, dest)
                        made += 1
                    except Exception:                   # noqa: BLE001
                        failed += 1
    return {"made": made, "skipped": skipped, "failed": failed}


# --------------------------------------------------------------- verification

def verify(paks: str, usmap: str, export_root: str, oodle: Optional[str],
           limit: int = 40, engine: str = "GAME_UE4_26",
           prefer_ooz: bool = False) -> Dict[str, object]:
    """Byte-compare container extraction against an existing FModel export.

    This is the test that says the game-folder path is correct rather than
    merely plausible. An FModel dump of the same game build is an independent
    implementation of the same job, so matching it byte for byte on a sample of
    real packages is strong evidence; a mismatch localises the problem to a
    named asset instead of "cutscenes look wrong".

    Compares only packages present in both, and reports the three outcomes
    separately - identical, differing, and absent from the export - because
    "absent" is usually the export being partial, not a bug here.
    """
    # Validate the two paths the user typed *before* touching Oodle. Loading a
    # DLL first means a mistyped folder is reported as a decompression problem,
    # which sends people off fixing the wrong thing.
    paks = find_paks(paks)

    export_content = toolconfig.content_within(export_root)
    if not export_content:
        raise SystemExit(
            "No Content/Cut/Game under %s - that does not look like an "
            "FModel export.\n" % export_root
        )

    backend = preload_oodle(oodle, (os.path.dirname(os.path.abspath(__file__)),),
                            prefer_ooz)
    provider, mounted = open_provider(paks, usmap, engine)

    same: List[str] = []
    differ: List[Tuple[str, int, int]] = []
    missing: List[str] = []
    unreadable: List[str] = []

    # Collect the comparable set first, then sample it evenly. Taking the first
    # `limit` in sorted order would only ever check 0000-COMON, and a reader
    # that works on one area is not evidence about the others - the areas differ
    # in which containers they live in and how their blocks are compressed.
    # One walk of the export, then set membership - not an os.path.isfile per
    # container entry. There are 121,838 Cut/Game packages in the containers
    # against ~12,000 in a typical export, and stat-ing each of them across a
    # mounted folder took longer than the whole rest of the check.
    export_cut = os.path.join(export_content, *ESSENTIAL_PREFIX.strip("/").split("/"))
    on_disk_rel = {}
    for root, _dirs, files in os.walk(export_cut):
        for f in files:
            full = os.path.join(root, f)
            rel_os = os.path.relpath(full, export_content)
            on_disk_rel[rel_os.replace(os.sep, "/")] = full

    comparable = []
    for vfs_path, entry in sorted(iter_entries(provider), key=lambda kv: kv[0]):
        rel = content_relative(vfs_path)
        if rel is None or not rel.startswith(ESSENTIAL_PREFIX):
            continue
        full = on_disk_rel.get(on_disk_name(rel))
        if full is None:
            if len(missing) < 50:
                missing.append(rel)
            continue
        comparable.append((rel, entry, full))

    if limit and len(comparable) > limit:
        stride = len(comparable) / float(limit)
        sample = [comparable[int(i * stride)] for i in range(limit)]
    else:
        sample = comparable

    areas = set()
    checked = 0
    for rel, entry, on_disk in sample:
        checked += 1
        parts = rel.split("/")
        if len(parts) > 2:
            areas.add(parts[2])
        try:
            got = _entry_bytes(entry)
        except Exception as e:                          # noqa: BLE001
            unreadable.append("%s: %r" % (rel, e))
            continue
        if got is None:
            unreadable.append("%s: no data" % rel)
            continue
        with open(on_disk, "rb") as f:
            want = f.read()
        if got == want:
            same.append(rel)
        else:
            differ.append((rel, len(got), len(want)))

    return {
        "backend": backend,
        "mounted": mounted,
        "comparable": len(comparable),
        "areas": len(areas),
        "checked": checked,
        "identical": len(same),
        "differing": differ[:20],
        "differing_total": len(differ),
        "missing_from_export": len(missing),
        "missing_sample": missing[:10],
        "unreadable": unreadable[:10],
        "verdict": ("pass" if same and not differ and not unreadable
                    else "fail" if (differ or unreadable)
                    else "inconclusive"),
    }


# ----------------------------------------------------------------------- CLI

def _progress(done: int, total: int, rel: str) -> None:
    """One rewritten line on a terminal, occasional lines when redirected.

    `\r` only means "redraw" to a terminal. Piped to a file or a log it is just
    another character, so a 164,000-package run becomes one unreadable line
    megabytes long - which is exactly what happens when someone sends you their
    setup log.
    """
    pct = (100 * done // total) if total else 100
    if sys.stdout.isatty():
        sys.stdout.write("\r  %3d%%  %6d/%-6d  %-52s"
                         % (pct, done, total, rel[-52:]))
    elif done == total or done % 2000 == 1:
        sys.stdout.write("  %3d%%  %6d/%-6d\n" % (pct, done, total))
    sys.stdout.flush()


def _report_extract(stats: Dict[str, object]) -> int:
    print()
    if stats.get("space_warning"):
        print("  DISK           : %s" % stats["space_warning"])
    print("  packages found : %d" % stats["total"])
    print("  written        : %d" % stats["written"])
    print("  already there  : %d" % stats["skipped"])
    if stats["failed"]:
        print("  FAILED         : %d" % stats["failed"])
    print()
    print("  by area:")
    for prefix, count in sorted(stats["per_prefix"].items()):
        why = dict(WANTED).get(prefix, "")
        flag = "" if count else "   <-- nothing found"
        print("    %-22s %6d  %s%s" % (prefix, count, why, flag))
    for err in stats["errors"]:
        print("    ! %s" % err)
    if stats["essential"] == 0:
        print()
        print("  Nothing was found under %s, so no cutscenes were extracted."
              % ESSENTIAL_PREFIX)
        print("  The containers mounted but do not hold what we expected -")
        print("  check this is a Rebirth install and not another UE game.")
        return 1
    return 0 if not stats["failed"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="gameextract",
        description="Extract the assets the cutscene editor needs from a "
                    "Rebirth install.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    cfg = toolconfig.resolve({}, os.path.dirname(os.path.abspath(__file__)))

    e = sub.add_parser("extract", help="write a loose Zen export tree")
    e.add_argument("game", help="the game folder, or End/Content/Paks inside it")
    e.add_argument("out", help="where to write the export tree (an 'End' folder)")
    e.add_argument("--usmap", default=cfg.get("usmap"))
    e.add_argument("--oodle", default=cfg.get("oodle"))
    e.add_argument("--engine", default=cfg.get("engine") or "GAME_UE4_26")
    e.add_argument("--only", action="append",
                   help="limit to a path prefix, e.g. Cut/Game/8800-FOREE "
                        "(repeatable)")
    e.add_argument("--dry-run", action="store_true",
                   help="count what would be extracted and stop")
    e.add_argument("--no-sidecars", action="store_true",
                   help="skip regenerating the TxtRes JSON subtitle tables")
    e.add_argument("--prefer-ooz", action="store_true",
                   help="use the open ooz decompressor even if a DLL is present")
    e.add_argument("--allow-low-space", action="store_true",
                   help="extract even when the target drive looks too small")

    v = sub.add_parser("verify", help="byte-compare against an FModel export")
    v.add_argument("game", help="the game folder, or End/Content/Paks inside it")
    v.add_argument("export", help="an existing export tree (the 'End' folder)")
    v.add_argument("--usmap", default=cfg.get("usmap"))
    v.add_argument("--oodle", default=cfg.get("oodle"))
    v.add_argument("--engine", default=cfg.get("engine") or "GAME_UE4_26")
    v.add_argument("--limit", type=int, default=40,
                   help="how many packages to compare (default 40)")
    v.add_argument("--prefer-ooz", action="store_true",
                   help="use the open ooz decompressor even if a DLL is present")

    a = ap.parse_args(argv)

    if a.cmd == "extract":
        paks = find_paks(a.game)
        backend = preload_oodle(
            a.oodle, (os.path.dirname(os.path.abspath(__file__)),), a.prefer_ooz)
        print("Reading %s" % paks)
        print("  oodle via %s" % backend)
        provider, mounted = open_provider(paks, a.usmap, a.engine)
        print("  mounted %d container(s)" % mounted)
        t0 = time.time()
        stats = extract(provider, os.path.abspath(a.out), only=a.only,
                        dry_run=a.dry_run,
                        allow_low_space=a.allow_low_space,
                        progress=None if a.dry_run else _progress)
        rc = _report_extract(stats)
        if a.dry_run:
            print("\n  (dry run - nothing written)")
            return rc
        print("\n  %.1fs" % (time.time() - t0))
        if rc == 0 and not a.no_sidecars:
            content = os.path.join(os.path.abspath(a.out), "Content")
            print("\n  subtitle tables:")
            side = write_txtres_sidecars(content)
            print("    written %d, already present %d, failed %d"
                  % (side["made"], side.get("skipped", 0), side["failed"]))
            for u in side["unparsed"]:
                print("    ! %s" % u)
            if side["failed"] and not side["made"]:
                print("    Subtitle text will be missing from the editor.")
                print("    An FModel JSON export of Content/Text/US fixes it.")

            print("\n  voice durations:")
            vo = write_vo_duration_sidecars(content)
            print("    written %d, already present %d, no audio found %d"
                  % (vo["made"], vo.get("skipped", 0), vo["failed"]))
        return rc

    if a.cmd == "verify":
        res = verify(a.game, a.usmap, a.export, a.oodle, a.limit, a.engine,
                     a.prefer_ooz)
        print()
        print("  oodle backend           : %s" % res["backend"])
        print("  containers mounted      : %d" % res["mounted"])
        print("  comparable packages     : %d" % res["comparable"])
        print("  packages compared       : %d  (across %d areas)"
              % (res["checked"], res["areas"]))
        print("  byte-identical          : %d" % res["identical"])
        print("  differing               : %d" % res["differing_total"])
        for rel, got, want in res["differing"]:
            print("      %-50s got %d, export %d" % (rel[-50:], got, want))
        print("  unreadable              : %d" % len(res["unreadable"]))
        for u in res["unreadable"]:
            print("      %s" % u)
        print("  in game, not in export  : %d" % res["missing_from_export"])
        for m in res["missing_sample"]:
            print("      %s" % m)
        print()
        print("  VERDICT: %s" % res["verdict"].upper())
        if res["verdict"] == "pass":
            print("  Container extraction matches the FModel export byte for")
            print("  byte. The game-folder path can be trusted.")
        elif res["verdict"] == "inconclusive":
            print("  Nothing comparable was found. Check that the export and")
            print("  the install are the same game build.")
        return 0 if res["verdict"] == "pass" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
