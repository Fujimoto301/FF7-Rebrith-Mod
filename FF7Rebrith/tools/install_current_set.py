"""Install the explicitly authorized, verified Chapters1/2 trial with rollback."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone

W=Path(__file__).resolve().parents[1]
DEST=Path(r'E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods')
NAMES=['ThaiJP_Chapter1_P'+ext for ext in ('.pak','.utoc','.ucas')]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(inventory=False):
    qa=W/('qa/inventory' if inventory else 'qa/chapter2')
    run=Path(json.loads((qa/'pending-install.json').read_text(encoding='utf-8'))['run'])
    assert run.resolve().is_relative_to((W/'qa/installations').resolve())
    before=json.loads((run/'before.json').read_text(encoding='utf-8'))
    package=json.loads((qa/'package-verification.json').read_text(encoding='utf-8'))
    assert package['all_match_staging'] and len(package['assets'])==21
    assert package['rebirth_oodle_flag']=='8c'
    stage=W/('staging/ThaiJP_Inventory_Working' if inventory else 'staging/ThaiJP_ThroughChapter2_Working')
    assert len(list(stage.rglob('*.uasset')))==21
    for asset in package['assets']:
        assert digest(stage/asset['asset'])==asset['sha256']
    manifest=json.loads((qa/'release-support/checksums.json').read_text(encoding='utf-8'))
    assert set(manifest)==set(NAMES)
    pending=run/'pending'
    pending.mkdir()
    source=W/'dist/ThaiJP_Chapter1_P'
    for name in NAMES:
        assert digest(source/name)==manifest[name]['sha256']
        shutil.copy2(source/name,pending/name)
        assert digest(pending/name)==manifest[name]['sha256']
    DEST.mkdir(parents=True,exist_ok=True)
    # Confirm the installed files still match the backups made before packing.
    originals={Path(r['original']).name:r for r in before if Path(r['original']).parent==DEST}
    for name in NAMES:
        assert name in originals and digest(DEST/name)==originals[name]['sha256'],name
    replaced=[]
    try:
        for name in NAMES:
            os.replace(pending/name,DEST/name)
            replaced.append(name)
        for name in NAMES:
            assert digest(DEST/name)==manifest[name]['sha256'],name
    except Exception:
        for name in replaced:
            shutil.copy2(Path(originals[name]['backup']),DEST/name)
            assert digest(DEST/name)==originals[name]['sha256']
        raise
    # Keep the user's existing test-extraction folder aligned with this release.
    extracted=W/'dist/Chapter1-Test'
    if extracted.is_dir():
        for name in NAMES:
            shutil.copy2(source/name,extracted/name)
            assert digest(extracted/name)==manifest[name]['sha256']
    files=[dict(file=name,path=str(DEST/name),bytes=(DEST/name).stat().st_size,sha256=digest(DEST/name).upper()) for name in NAMES]
    report=dict(content='Chapters1–2 + menus + all-game item/skill effects' if inventory else 'Chapters1–2 + corrected menus and latest proper-name policy',
                installed_at_utc=datetime.now(timezone.utc).isoformat(),destination=str(DEST),
                backup=str(run/'before/installed'),run=str(run),files=files,
                chapter1_dialogue_records=1157,chapter2_dialogue_records=2876,menu_selected_records=583,
                menu_changed_records=533,package_assets=21,
                protected_english_mode_labels=['EASY','NORMAL','ADVANCED','HARD','ACTION','CLASSIC'],
                all_packaged_assets_match_staging=True,verified_after_copy=True,runtime_tested=False)
    if inventory:
        assembly=json.loads((qa/'assembly.json').read_text(encoding='utf-8'))
        report.update(inventory_description_records=assembly['description_records'],inventory_english_names=assembly['english_name_records'],total_text_records=assembly['total_combined_text_records'],working_set_sha256=digest(W/'translations/working-inventory-th.json'))
    for path in {qa/'installation.json',W/'qa/chapter2/installation.json',W/'qa/menu/installation.json',W/'qa/installation-latest.json',run/'installation.json'}:
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(installed_files=3,package_assets=21,destination=str(DEST),backup=report['backup'],verified_after_copy=True),ensure_ascii=False))

if __name__=='__main__':main(inventory='--inventory' in sys.argv)
