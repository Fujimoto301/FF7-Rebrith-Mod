"""Selective raw Zen export; reads the game, writes only this mod workspace.

Container reader: AdenAvalonian/FFVII-Rebirth-CutsceneTool (MIT), vendored
pyUE4Parse (MIT); their notices remain in tools/cutscene-tool/1.0/licenses.
"""
from pathlib import Path
import json
import logging
import sys

WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
sys.path[:0] = [str(ROOT / "tools/python-libs"), str(WORK / "tools/cutscene-tool/1.0")]
import gameextract as reader
from UE4Parse.Provider.DefaultFileProvider import DefaultFileProvider
from UE4Parse.Versions import EUEVersion, VersionContainer

GAME = Path(r"E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH")


def main():
    logging.disable(logging.WARNING)
    reader.preload_oodle()
    provider = DefaultFileProvider(str(GAME / "End/Content/Paks"), VersionContainer(EUEVersion.GAME_UE4_26))
    provider.initialize()
    mounted = provider.submit_key()
    if not mounted:
        raise RuntimeError("No game containers mounted")
    reader.fix_partition_size(provider)
    selected = []
    for name, entry in reader.iter_entries(provider):
        lower = name.lower()
        is_text = any(f"/text/{lang}/" in lower for lang in ("jp", "us")) and "txtres" in lower
        is_font = "font" in lower and ("/menu/" in lower or "/ui/" in lower)
        if not (is_text or is_font):
            continue
        rel = Path(name + ("" if Path(name).suffix else ".uasset"))
        out = WORK / "source" / rel
        if not out.resolve().is_relative_to((WORK / "source").resolve()):
            raise RuntimeError("Unsafe export path")
        out.parent.mkdir(parents=True, exist_ok=True)
        data = reader._entry_bytes(entry)
        if data is None:
            raise RuntimeError(f"No bytes for {name}")
        out.write_bytes(data)
        selected.append(dict(asset=str(rel).replace("\\", "/"), bytes=len(data), type="text" if is_text else "font"))
    report = dict(game=str(GAME), mounted_containers=mounted, exported_assets=selected)
    (WORK / "source/extraction-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(dict(texts=sum(e["type"] == "text" for e in selected), fonts=sum(e["type"] == "font" for e in selected))))


if __name__ == "__main__":
    main()
