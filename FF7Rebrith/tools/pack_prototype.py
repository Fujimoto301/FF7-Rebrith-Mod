"""Pack locally and verify every asset by independently reading the archive."""
from pathlib import Path
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import uuid

WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
sys.path[:0] = [str(ROOT / "tools/python-libs"), str(WORK / "tools/cutscene-tool/1.0")]
import gameextract as reader
from UE4Parse.Provider.DefaultFileProvider import DefaultFileProvider
from UE4Parse.Versions import EUEVersion, VersionContainer


def main(package_name="ThaiJP_Prototype_P", expected_assets=17, stage_override=None, qa_override=None, target_override=None, font_license=None):
    qa = WORK / (qa_override or ("qa/chapter1" if package_name == "ThaiJP_Chapter1_P" else "qa"))
    target = WORK / target_override if target_override else WORK / "dist" / package_name
    target.mkdir(parents=True, exist_ok=True)
    # Build in a fresh directory and promote only after independent readback.
    pack_runs = qa / "pack-runs"
    pack_runs.mkdir(parents=True, exist_ok=True)
    pack_run = pack_runs / uuid.uuid4().hex
    pack_run.mkdir()
    # Exclude installed mods from the base provider. Otherwise an existing mod
    # can contribute its container data when the same asset IDs are repacked.
    game_paks = Path(r"E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks")
    base_root = qa / "base-pak-links"
    base_root.mkdir(parents=True, exist_ok=True)
    base_paks = base_root / uuid.uuid4().hex
    base_paks.mkdir()
    for source in game_paks.iterdir():
        if source.is_file() and source.suffix.lower() in (".pak", ".utoc", ".ucas"):
            os.link(source, base_paks / source.name)
    tool = WORK / "tools/UnrealReZen/UnrealReZen.exe"
    stage = WORK / stage_override if stage_override else WORK / "staging" / package_name
    output = pack_run / (package_name + ".utoc")
    command = [str(tool), "--game-dir", str(base_paks),
               "--content-path", str(stage), "--engine-version", "GAME_UE4_26",
               "--compression-format", "Oodle", "--output-path", str(output)]
    try:
        with (qa / "pack.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, cwd=tool.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    finally:
        assert base_paks.resolve().is_relative_to(base_root.resolve())
        # Remove only our temporary hard links; original game paths stay intact.
        for link in base_paks.iterdir():
            assert link.is_file()
            link.unlink()
        base_paks.rmdir()
    archive = output.with_suffix(".ucas")
    if not output.exists() or not archive.exists():
        raise RuntimeError("Pack tool produced no output")
    # Rebirth-specific Oodle block flag correction, documented by the tool's
    # maintainer: https://github.com/rm-NoobInCoding/UnrealReZen/issues/58
    with archive.open("r+b") as stream:
        first = stream.read(1)
        if first == b"\xcc":
            stream.seek(0)
            stream.write(b"\x8c")
        elif first != b"\x8c":
            raise ValueError(f"Unexpected Oodle first byte: {first.hex()}")
    logging.disable(logging.CRITICAL)
    reader.preload_oodle()
    provider = DefaultFileProvider(str(pack_run), VersionContainer(EUEVersion.GAME_UE4_26))
    provider.initialize()
    if not provider.submit_key():
        raise RuntimeError("Unable to mount completed mod")
    reader.fix_partition_size(provider)
    verified = []
    for name, entry in reader.iter_entries(provider):
        rel = Path(name + ("" if Path(name).suffix else ".uasset"))
        reference = stage / rel
        raw = reader._entry_bytes(entry)
        if not reference.exists() or raw != reference.read_bytes():
            raise ValueError(f"Archive mismatch: {name}")
        verified.append(dict(asset=str(rel).replace("\\", "/"), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    if len(verified) != len(list(stage.rglob("*.uasset"))) or len(verified) != expected_assets:
        raise ValueError(f"Archive does not contain exactly the intended {expected_assets} assets")
    report = dict(assets=verified, all_match_staging=True, rebirth_oodle_flag="8c", runtime_tested=False)
    (qa / "package-verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    packed_paths = [pack_run / (package_name + ext) for ext in (".pak", ".utoc", ".ucas")]
    assert all(p.is_file() for p in packed_paths)
    for packed_path in packed_paths:
        shutil.copyfile(packed_path, target / packed_path.name)
    if font_license:
        shutil.copyfile(WORK / "tools/fonts" / font_license, target / font_license)
    elif package_name == "ThaiJP_Chapter1_P":
        shutil.copyfile(WORK / "tools/fonts/NotoSansThai-OFL.txt", target / "NotoSansThai-OFL.txt")
    else:
        shutil.copyfile(WORK / "tools/fonts/OFL.txt", target / "Sarabun-OFL.txt")
    print(f"Verified {len(verified)} assets after the Rebirth Oodle correction")


if __name__ == "__main__":
    if "--inventory" in sys.argv:
        main("ThaiJP_Chapter1_P",21,stage_override="staging/ThaiJP_Inventory_Working",qa_override="qa/inventory")
    elif "--through-chapter2" in sys.argv:
        main("ThaiJP_Chapter1_P",21,stage_override="staging/ThaiJP_ThroughChapter2_Working",qa_override="qa/chapter2")
    elif "--menus" in sys.argv:
        main("ThaiJP_Chapter1_P",20,stage_override="staging/ThaiJP_Working",qa_override="qa/menu")
    elif "--chapter1" in sys.argv:
        main("ThaiJP_Chapter1_P",20)
    else:
        main()
