"""Create a trial ZIP with font license in its readable archive comment."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

WORK = Path(__file__).resolve().parents[1]
DIST = WORK / "dist"


def main(package_name="ThaiJP_Prototype_P", expected_assets=17, qa_override=None, target_override=None, zip_override=None, guide_override=None):
    target = WORK / target_override if target_override else DIST / package_name
    qa = WORK / (qa_override or ("qa/chapter1" if package_name == "ThaiJP_Chapter1_P" else "qa"))
    report = json.loads((qa / "package-verification.json").read_text(encoding="utf-8"))
    assert report["all_match_staging"] and len(report["assets"]) == expected_assets
    assert report["rebirth_oodle_flag"] == "8c"
    guide = "README-CHAPTER1.md" if package_name == "ThaiJP_Chapter1_P" else "README-PROTOTYPE.md"
    if qa_override == "qa/menu":
        guide = "README-MENU-TRIAL.md"
    elif qa_override == "qa/chapter2":
        guide = "README-CHAPTER2-TRIAL.md"
    elif qa_override == "qa/inventory":
        guide = "README-INVENTORY-TRIAL.md"
    if guide_override:
        guide = guide_override
    support = qa / "release-support" if package_name == "ThaiJP_Chapter1_P" else target
    support.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WORK / guide, support / "README.md")
    names = [package_name + ext for ext in (".pak", ".utoc", ".ucas")]
    manifest = {name: {"bytes": (target / name).stat().st_size,
                      "sha256": hashlib.sha256((target / name).read_bytes()).hexdigest()}
                for name in names}
    (support / "checksums.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    license_name = "NotoSansThai-OFL.txt" if package_name == "ThaiJP_Chapter1_P" else "Sarabun-OFL.txt"
    license_comment = b""
    if package_name == "ThaiJP_Chapter1_P":
        license_source = WORK / "tools/fonts/NotoSansThai-OFL.txt"
        shutil.copyfile(license_source, support / license_name)
        license_comment = b"Embedded Thai font license and copyright notice (UTF-8):\n\n" + license_source.read_bytes()
        assert len(license_comment) <= 65535
    files = names if package_name == "ThaiJP_Chapter1_P" else names + ["README.md", license_name, "checksums.json"]
    path = WORK / zip_override if zip_override else DIST / (package_name + ".zip")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.comment = license_comment
        for name in files:
            archive.write(target / name, name)
    with zipfile.ZipFile(path) as archive:
        assert archive.namelist() == files
        assert archive.comment == license_comment
        assert archive.testzip() is None
        for name in names:
            assert archive.read(name) == (target / name).read_bytes()
    if package_name == "ThaiJP_Chapter1_P":
        # Only these known support files are removed from the trial folder.
        # Preserve copies in QA before removing the redundant originals.
        for name in ("README.md", "checksums.json", license_name):
            redundant = target / name
            if redundant.exists():
                shutil.copyfile(redundant, support / ("previous-" + name))
                redundant.unlink()
    print(f"Created and verified {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    if "--inventory" in sys.argv:
        main("ThaiJP_Chapter1_P",21,qa_override="qa/inventory")
    elif "--through-chapter2" in sys.argv:
        main("ThaiJP_Chapter1_P",21,qa_override="qa/chapter2")
    elif "--menus" in sys.argv:
        main("ThaiJP_Chapter1_P",20,qa_override="qa/menu")
    elif "--chapter1" in sys.argv:
        main("ThaiJP_Chapter1_P",20)
    else:
        main()
