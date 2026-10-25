"""
Is this package actually in the pak?

    python checkpak.py Retarget_Test_P.utoc
    python checkpak.py <utoc> --package /Game/DataObject/Field/8800-FOREE/CutSceneListLevel
    python checkpak.py <utoc> --content retarget_out        # check everything staged

IoStore does not store package paths. A package is identified by an FIoChunkId
whose first eight bytes are `CityHash64(lowercased package name as UTF-16LE)` —
the same hash `loosezen.py` already brute-forces for script objects. Mod paks
built by UnrealReZen carry no directory index at all, so grepping a `.utoc` for
readable names finds nothing even when the package is present. Look for the
hash instead.

Sizes are not evidence of failure. One 42 KB `CutSceneListLevel`, which is mostly
zero bytes, Oodle-compresses to a few KB, and a one-chunk `.utoc` is a few hundred
bytes. Small is what success looks like here.
"""

from __future__ import annotations

import argparse
import os
import sys

from cityhash import cityhash64

CONTENT_MARKER = os.path.join("End", "Content") + os.sep


def package_id(pkg):
    """FIoChunkId's leading eight bytes for a package name like /Game/Foo/Bar."""
    return cityhash64(pkg.lower().encode("utf-16-le"))


def package_of(path, content_root):
    """retarget_out/End/Content/DataObject/.../X.uasset -> /Game/DataObject/.../X"""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(content_root))
    rel = rel.replace("\\", "/")
    marker = "End/Content/"
    if marker in rel:
        rel = rel.split(marker, 1)[1]
    return "/Game/" + os.path.splitext(rel)[0]


def present(raw, pkg):
    pid = package_id(pkg)
    for order in ("little", "big"):
        b = pid.to_bytes(8, order)
        i = raw.find(b)
        if i >= 0:
            return pid, i, order
    return pid, -1, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("utoc")
    ap.add_argument("--package", action="append", default=[],
                    help="/Game/... name; repeatable")
    ap.add_argument("--content", help="staged folder; check every .uasset under it")
    a = ap.parse_args()
    if not os.path.exists(a.utoc):
        raise SystemExit("no such file: %s" % a.utoc)
    raw = open(a.utoc, "rb").read()
    ucas = os.path.splitext(a.utoc)[0] + ".ucas"

    pkgs = list(a.package)
    if a.content:
        for root, _, files in os.walk(a.content):
            for f in files:
                if f.endswith(".uasset"):
                    pkgs.append(package_of(os.path.join(root, f), a.content))
    if not pkgs:
        pkgs = ["/Game/DataObject/Field/8800-FOREE/CutSceneListLevel"]

    print("%s  (%d bytes utoc, %s)"
          % (a.utoc, len(raw),
             "%d bytes ucas" % os.path.getsize(ucas) if os.path.exists(ucas)
             else "NO .ucas beside it — the pak is incomplete"))

    ok = True
    for pkg in sorted(set(pkgs)):
        pid, at, order = present(raw, pkg)
        if at >= 0:
            print("  FOUND    %s\n           chunk id %016x at 0x%x (%s-endian)"
                  % (pkg, pid, at, order))
        else:
            ok = False
            print("  MISSING  %s\n           chunk id %016x not in this utoc" % (pkg, pid))

    if not ok:
        print("\n  If the package name looks wrong, that is the bug: UnrealReZen derives")
        print("  it from the folder layout under --content-path. The tree must be")
        print("  <content>/End/Content/<path>, so that /Game/<path> comes out, and the")
        print("  mount point must stay at the default ../../../ .")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
