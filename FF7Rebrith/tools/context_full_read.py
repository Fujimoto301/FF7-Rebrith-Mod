"""Persistent sequential human editorial queue; never mark unread ranges complete."""
import sys,re,hashlib,shutil,uuid
from pathlib import Path
from collections import Counter
from functools import lru_cache
from prepare_chapter9 import W,read,write,txtres
Q='qa/context-full-read/'
OVERRIDES='reference/context-full-read-overrides.json'

def active():return (W/OVERRIDES).exists()

@lru_cache(None)
def decisions():return read(OVERRIDES)['records'] if active() else []

def matches(a,k,before,after):
    return any(r['asset']==a and r['id']==k and after==r['after'] and before in r.get('accepted_before',[r['before']]) for r in decisions())

def overlay(now):
    if 'assets' not in now:return
    for r in decisions():
        p=now['assets'].get(r['asset'],{}).get('entries',{})
        if r['id'] not in p:continue
        assert p[r['id']]==r['after'] or matches(r['asset'],r['id'],p[r['id']],r['after']),r['id']
        p[r['id']]=r['after']

def commit_reviewed():
    rows=read(Q+'corrections.json')['records'];progress=read(Q+'progress.json')
    reviewed={i for r in progress['read_ranges'] for i in range(r['start'],r['end_exclusive'])}
    # Exact historical values only, scoped to each reviewed ID. Frozen snapshots
    # stay untouched and remain independently hash-checked by their own audits.
    history=[]
    for path in ['qa/chapter10/baseline.json','qa/chapter10/recheck/current.json','qa/chapter10/continue-review/current.json','qa/chapter4-door-fix/baseline.json','qa/chapter4-choice-fix/baseline.json','qa/context-recheck/baseline.json',Q+'baseline.json']:
        rev=read(path);snap=Path(rev['snapshot']);ctx=rev['active']
        history.append(read(snap/ctx['combined_source']))
    # A later editorial pass may refine an ID already revised and published.
    # Accept only finite per-ID values from immutable release checkpoints;
    # keep the original frozen baseline as `before` for the cumulative audit.
    published_values={}
    for path in (W/Q/'releases').glob('*/corrections.json'):
        for prior in read(path)['records']:
            published_values.setdefault((prior['asset'],prior['id']),set()).add(prior['after'])
    assert len({(r['asset'],r['id']) for r in rows})==len(rows)
    for r in rows:
        assert r['index'] in reviewed,r['id']
        vals={r['before']}
        vals.update(published_values.get((r['asset'],r['id']),set()))
        for h in history:
            t=h['assets'].get(r['asset'],{}).get('entries',{}).get(r['id'])
            if t is not None:vals.add(t)
        r['accepted_before']=sorted(vals)
    write(OVERRIDES,dict(records=rows,full_editorial_read_complete=progress['semantic_review_complete']))
    decisions.cache_clear()
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);overlay(now);write(ctx['combined_source'],now)
    for path in (W/'translations').glob('chapter*-th.json'):
        p=read(path);overlay(p);write(path,p)
    print('Applied exact reviewed revisions',len(rows),'full read complete:',progress['semantic_review_complete'])

def audit():
    rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);ctx=rev['active'];old=read(snap/ctx['combined_source']);now=read(ctx['combined_source']);index={(r['asset'],r['id']):r for r in decisions()};changed=[]
    for p,h in rev['hashes'].items():assert digest(snap/p)==h,p
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        n=now['assets'][a];assert p['entries'].keys()==n['entries'].keys() and p['actors']==n['actors']
        for k,t in p['entries'].items():
            if t==n['entries'][k]:continue
            r=index[a,k];assert r['before']==t and r['after']==n['entries'][k]
            assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['after'])
            assert re.findall(r'\d+',t)==re.findall(r'\d+',r['after']),(k,'numbers')
            changed.append((a,k))
    assert set(changed)==set(index)
    assert read(ctx['cluster_map'])==read(snap/ctx['cluster_map'])
    from assemble_ui_completion import fingerprint
    from verify_installed_session import verify
    verify(rev['protected'])
    prior=read(snap/ctx['manifest']);stage=W/ctx['stage'];current={str(p.relative_to(stage)):digest(p) for p in stage.rglob('*.uasset')}
    assert current.keys()==prior.keys()
    actual={a.replace('\\','/') for a,h in current.items() if prior[a]!=h};assert actual=={a for a,k in changed}
    progress=read(Q+'progress.json')
    write(Q+'audit.json',dict(source_sha256=digest(W/ctx['combined_source']),corrected_records=len(changed),total_records=progress['total_records'],reviewed_records=progress['reviewed_records'],remaining_records=progress['remaining_records'],full_editorial_read_complete=progress['semantic_review_complete'],all_other_text_ACTOR_fonts_map_preserved=True,changed_assets=sorted(actual),in_game_tested=False))
    print('Full-read revision verified',len(changed),'changes;',progress['reviewed_records'],'read;',progress['remaining_records'],'remaining')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare():
    assert not (W/Q/'baseline.json').exists(),'Preserve this revision baseline'
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);c=read('reference/rebirth-jp-corpus.json');rows=[]
    from assemble_ui_completion import fingerprint
    snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter10/editorial-signoff.json','reference/context-recheck-overrides.json']
    for p in paths:
        dest=snap/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/p,dest)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,hashes={p:digest(snap/p) for p in paths},protected=fingerprint()))
    # Main story first in narrative chapter order; each source file's native
    # row order retained inside a family. NPC/quest/common queues follow.
    chapter={'C1910':1,'C1920':2,'C2010':2,'C2110':3,'C2120':4,'C2210':4,'C2310':5,'C2320':5,'C2410':6,'C2510':7,'C2520':7,'C2610':8,'C2620':8,'C2630':8,'C2710':9,'C2810':9,'C2910':10,'C3010':10}
    for a,p in now['assets'].items():
        us=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')))
        for k,j in c[Path(a).name].items():
            if k not in p['entries']:continue
            t=p['entries'][k];prefix=k.lstrip('$').split('_')[0]
            queue=f"{chapter[prefix]:02d}-main" if prefix in chapter else '11-scene-NPC-quest' if not a.endswith(('Resident_TxtRes.uasset','0005-TITLB_TxtRes.uasset')) else '12-common'
            if not re.search('[\u0e00-\u0e7f]',t):queue='13-English-UI-notation'
            rows.append(dict(asset=a,id=k,jp=j['Text'],us=us.get(k,{}).get('Text',''),thai=t,actor=p['actors'].get(k,''),queue=queue))
    rows.sort(key=lambda r:r['queue'])
    for i,r in enumerate(rows):r['index']=i
    write(Q+'queue.json',rows);write(Q+'progress.json',dict(source_sha256=digest(W/ctx['combined_source']),total_records=len(rows),counts=dict(Counter(r['queue'] for r in rows)),read_ranges=[],reviewed_records=0,remaining_records=len(rows),semantic_review_complete=False,in_game_tested=False))
    write(Q+'corrections.json',dict(records=[]))
    print(read(Q+'progress.json'))

def show(start,end):
    rows=read(Q+'queue.json')
    for r in rows[start:end]:
        print(r['index'],r['id'],r['actor'],'|',r['jp'].replace('\r','').replace('\n',' / '),'→',r['thai'].replace('\r','').replace('\n',' / '))

def record(start,end,notes):
    rows=read(Q+'queue.json');p=read(Q+'progress.json');assert 0<=start<end<=len(rows)
    existing={i for r in p['read_ranges'] for i in range(r['start'],r['end_exclusive'])};assert not existing&set(range(start,end))
    p['read_ranges'].append(dict(start=start,end_exclusive=end,records=end-start,notes=notes,reading='JP/current Thai sequential editorial comparison; same-ID US and wider neighbors opened separately where needed. Not runtime/audio verification.'))
    p['reviewed_records']=len(existing)+end-start;p['remaining_records']=len(rows)-p['reviewed_records'];p['semantic_review_complete']=p['remaining_records']==0;write(Q+'progress.json',p);print('Read',p['reviewed_records'],'remaining',p['remaining_records'])

if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    elif '--show' in sys.argv:show(int(sys.argv[-2]),int(sys.argv[-1]))
    elif '--record' in sys.argv:record(int(sys.argv[-3]),int(sys.argv[-2]),sys.argv[-1])
    elif '--commit-reviewed' in sys.argv:commit_reviewed()
    elif '--audit' in sys.argv:audit()
