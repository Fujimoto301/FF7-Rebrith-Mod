"""Back up the explicitly authorized inventory installation before packing."""
import hashlib,json,shutil,uuid
from pathlib import Path
from datetime import datetime,timezone
W=Path(__file__).resolve().parents[1]
DEST=Path(r'E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    qa=W/'qa/inventory'
    report=json.loads((qa/'working-assets.json').read_text('utf-8'))
    stage=W/'staging/ThaiJP_Inventory_Working'
    assert len(report['verified_assets'])==21
    assert {p.relative_to(stage).as_posix() for p in stage.rglob('*.uasset')}=={r['asset'] for r in report['verified_assets']}
    for r in report['verified_assets']:assert digest(stage/r['asset'])==r['sha256'],r['asset']
    assert json.loads((qa/'audit.json').read_text('utf-8'))['passed']
    run=W/'qa/installations'/uuid.uuid4().hex
    run.mkdir(parents=True)
    before=[]
    def backup(source,relative):
        if not source.exists():return
        target=run/'before'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        assert digest(source)==digest(target)
        before.append(dict(original=str(source),backup=str(target),sha256=digest(source)))
    for ext in ('.pak','.utoc','.ucas'):
        name='ThaiJP_Chapter1_P'+ext
        assert (DEST/name).is_file(),name
        backup(DEST/name,Path('installed')/name)
        backup(W/'dist/ThaiJP_Chapter1_P'/name,Path('dist')/name)
        backup(W/'dist/Chapter1-Test'/name,Path('extracted')/name)
    backup(W/'dist/ThaiJP_Chapter1_P.zip',Path('zip/ThaiJP_Chapter1_P.zip'))
    for p in ['qa/installation-latest.json','qa/chapter2/installation.json','qa/menu/installation.json','qa/inventory/audit.json','qa/inventory/verification.json','qa/inventory/working-assets.json']:
        backup(W/p,Path('metadata')/p)
    (run/'before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n','utf-8')
    (qa/'pending-install.json').write_text(json.dumps(dict(run=str(run),authorized_request='อันนี้ลงmodได้เลย',prepared_at_utc=datetime.now(timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n','utf-8')
    print('Verified backup:',run,'files:',len(before))
if __name__=='__main__':main()
