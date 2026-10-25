"""Whole current-release context inventory; keep machine screening distinct from editorial review."""
import re,sys,uuid,shutil,hashlib
from collections import defaultdict,Counter
from functools import lru_cache
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
Q='qa/context-recheck/'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def active():return (W/'reference/context-recheck-overrides.json').exists()

@lru_cache(None)
def decisions():return read('reference/context-recheck-overrides.json')['records']

@lru_cache(None)
def decision_index():return {(r['asset'],r['id']):r for r in decisions()}

def matches(a,k,before,after):
    if not active():return False
    r=decision_index().get((a,k))
    return bool(r and before in r.get('accepted_before',[r['before']]) and after==r['after'])

def overlay(now):
    if not active():return
    for r in decisions():
        a,k=r['asset'],r['id'];old=now['assets'][a]['entries'][k]
        assert old==r['after'] or matches(a,k,old,r['after']),(a,k,'Unexpected rebuild input')
        now['assets'][a]['entries'][k]=r['after']

def apply():
    rev=read(Q+'baseline.json');ctx=rev['active'];now=read(ctx['combined_source']);overlay(now);write(ctx['combined_source'],now)
    # Keep editable chapter patches consistent, without rewriting frozen templates
    # or snapshots. The final per-ID overlay remains authoritative on rebuild.
    for path in (W/'translations').glob('chapter*-th.json'):
        patch=read(path);changed=False
        for r in decisions():
            p=patch.get('assets',{}).get(r['asset'],{})
            if r['id'] in p.get('entries',{}):p['entries'][r['id']]=r['after'];changed=True
        if changed:write(path,patch)
    print('Applied',len(decisions()),'reviewed per-ID context/glossary corrections')

def audit():
    rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);ctx=rev['active'];old=read(snap/ctx['combined_source']);now=read(ctx['combined_source']);rs=decisions();index={(r['asset'],r['id']):r for r in rs};changed=[]
    from context_full_read import decisions as full_decisions,matches as full_matches,active as full_active,Q as FULL_Q,audit as full_audit
    followup={(r['asset'],r['id']):r for r in full_decisions()}
    for p,h in rev['hashes'].items():assert digest(snap/p)==h,p
    assert old['assets'].keys()==now['assets'].keys()
    corpus=read('reference/rebirth-jp-corpus.json')
    for a,p in old['assets'].items():
        n=now['assets'][a];assert p['entries'].keys()==n['entries'].keys() and p['actors']==n['actors']
        for k,t in p['entries'].items():
            if t==n['entries'][k]:continue
            r=followup.get((a,k),index.get((a,k)));assert r is not None
            assert (r['before']==t and matches(a,k,t,n['entries'][k]) or full_matches(a,k,t,n['entries'][k])) and r['after']==n['entries'][k]
            assert r['jp']==corpus[Path(a).name][k]['Text']
            assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['after'])
            assert re.findall(r'\d+',clean(t))==re.findall(r'\d+',clean(r['after'])),(k,'numbers')
            changed.append((a,k))
    assert set(changed)==set(index)|set(followup)
    assert read(ctx['cluster_map'])==read(snap/ctx['cluster_map'])
    protected=read(FULL_Q+'baseline.json')['protected'] if full_active() else rev['protected']
    from verify_installed_session import verify
    verify(protected)
    prior=read(snap/ctx['manifest']);stage=W/ctx['stage'];current={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))}
    assert current.keys()==prior.keys()
    expected_assets={a for a,k in changed};actual_assets={a.replace('\\','/') for a,h in current.items() if prior[a]!=h}
    assert actual_assets==expected_assets,(actual_assets,expected_assets)
    write(Q+'audit.json',dict(source_sha256=digest(W/ctx['combined_source']),corrected_records=len(changed),total_records=sum(len(p['entries']) for p in now['assets'].values()),changed_assets=sorted(actual_assets),all_other_texts_and_all_ACTOR_preserved=True,all_fonts_and_cluster_assignments_identical=True,all_tags_numbers_and_branch_IDs_preserved=True,source_and_installed_files_unchanged=True,full_manual_40691_line_review=False,in_game_tested=False))
    print('Context corrections verified:',len(changed),'IDs;',len(actual_assets),'text assets; all other records, fonts, actors preserved')
    if full_active():full_audit()

def review_ledger():
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);rev=read(Q+'baseline.json');inventory=read(Q+'inventory.json');records=read(Q+'all-record-contexts.json');changed=decision_index()
    assert inventory['source_sha256']==rev['hashes'][ctx['combined_source']]
    assert {(r['asset'],r['id']) for r in records}=={(a,k) for a,p in now['assets'].items() for k in p['entries']}
    choices=[]
    for g in read(Q+'scene-choice-groups.json'):
        a=g['asset'];lines=[dict(id=r['id'],jp=r['jp'],us=r['us'],before=r['thai'],after=now['assets'][a]['entries'][r['id']]) for r in g['records']]
        choices.append(dict(index=g['index'],asset=a,lines=lines,changed_ids=[r['id'] for r in lines if r['before']!=r['after']],review='Compared complete question and all source-ID answers; affirmative/negative branch identity preserved. Related spoken context inspected for ambiguous replies. No runtime branch test.'))
    write(Q+'choice-semantic-review.json',dict(source_sha256=digest(W/ctx['combined_source']),reviewed_groups=len(choices),records=sum(len(g['lines']) for g in choices),groups=choices))
    short=[]
    for g in read(Q+'reused-short-dialogue.json'):
        short.append(dict(index=g['index'],jp=g['jp'],old_shared_translation=g['thai'],same_ID_US_variants=g['english_variants'],context_depth='JP/Thai/US variant comparison for all348 groups; full source neighbors inspected for selected high-risk decisions.',occurrences=[dict(asset=r['asset'],id=r['id'],current=now['assets'][r['asset']]['entries'][r['id']],changed=(r['asset'],r['id']) in changed) for r in g['records']]))
    write(Q+'short-dialogue-review.json',dict(source_sha256=digest(W/ctx['combined_source']),groups=short,all348_variant_groups_compared=True,full_manual_every_dialogue_record=False))
    shared=read(Q+'shared-prompt-contexts.json')
    write(Q+'shared-prompt-review.json',dict(source_sha256=digest(W/ctx['combined_source']),candidates=len(shared),records=[dict(id=r['id'],jp=r['jp'],us=r['us'],current=now['assets'][r['asset']]['entries'][r['id']],decision='Placeholder question-mark name, or existing contextual UI prompt retained.' if (r['asset'],r['id']) not in changed else changed[r['asset'],r['id']]['decisions']) for r in shared]))
    japanese=[];bad=[]
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            if re.search('[\u3040-\u30ff\u3400-\u9fff]',t):japanese.append(dict(asset=a,id=k,text=t,decision='Official US piano C octave marker; allowed notation, not untranslated Japanese.'))
            if re.search(r'นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|ค่ะ\s*\?|([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',clean(t)):bad.append((a,k))
    assert not bad
    assert {r['id'] for r in japanese}=={'$minigame_piano_C2','$minigame_piano_C2_sharp'}
    write(Q+'corpus-screen.json',dict(source_sha256=digest(W/ctx['combined_source']),all_records_screened=len(records),mechanical_checks=['ID/actor retention','full staged source roundtrip and metadata','all selected family coverage','gender evidence regression','Japanese residual and malformed Thai endings/marks','source-specific canonical glossary','font/native Latin/numeric preservation'],japanese_notation_exceptions=japanese,manual_scene_choice_groups=201,manual_shared_prompt_candidates=len(shared),compact_short_variant_groups=348,full_manual_40691_line_review=False,all_runtime_branches_tested=False))
    print('Saved separate editorial ledgers:201 choice blocks,348 short-variant groups,',len(shared),'shared candidates; full40691 structural screen; no claim of full manual/runtime review')
def prepare():
    assert not (W/Q/'baseline.json').exists(),'Preserve context-review snapshot'
    ctx=read('qa/active-working-set.json');snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['manifest'],ctx['cluster_map'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter10/editorial-signoff.json']
    paths += [str(p.relative_to(W)) for p in (W/'translations').glob('chapter*-th.json')]
    for rel in paths:
        dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dest)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:digest(snap/p) for p in paths}))
    print('Saved full-current-release context review baseline')
def clean(t):return re.sub('<[^>]+>','',t).strip()
def inventory():
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);corpus=read('reference/rebirth-jp-corpus.json');records=[];short=defaultdict(list);groups=[]
    for a,p in now['assets'].items():
        source=corpus[Path(a).name];us=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')));keys=[k for k,v in source.items() if v['Text']];pos={k:i for i,k in enumerate(keys)};pending=[]
        for k,t in p['entries'].items():
            j=source[k]['Text'];u=us.get(k,{}).get('Text','');i=pos[k]
            r=dict(asset=a,id=k,jp=j,us=u,thai=t,actor=p['actors'].get(k,''),
                before=[dict(id=n,jp=source[n]['Text'],us=us.get(n,{}).get('Text',''),thai=p['entries'].get(n)) for n in keys[max(0,i-2):i]],
                after=[dict(id=n,jp=source[n]['Text'],us=us.get(n,{}).get('Text',''),thai=p['entries'].get(n)) for n in keys[i+1:i+3]])
            records.append(r)
            if len(clean(j))<=12 and not k.endswith('_sys') and not a.endswith('Resident_TxtRes.uasset'):
                short[clean(j),t].append(r)
        # All consecutive scene _sys blocks, with the spoken trigger and following line.
        for i,k in enumerate(keys):
            if k.endswith('_sys') and k in p['entries']:
                if pending and i!=pending[-1][0]+1:
                    groups.append((a,pending));pending=[]
                pending.append((i,k))
            elif pending:groups.append((a,pending));pending=[]
        if pending:groups.append((a,pending))
    write(Q+'all-record-contexts.json',records)
    indexed={(r['asset'],r['id']):r for r in records};out=[]
    for a,g in groups:
        rs=[indexed[a,k] for i,k in g]
        out.append(dict(index=len(out),asset=a,records=rs,scope='complete consecutive scene UI block; before/after context retained'))
    write(Q+'scene-choice-groups.json',out)
    reused=[]
    for (j,t),rs in short.items():
        forms={clean(r['us']) for r in rs}
        if len(rs)<2 or len(forms)<2:continue
        reused.append(dict(index=0,jp=j,thai=t,records=rs,english_variants=sorted(forms),occurrences=len(rs)))
    reused.sort(key=lambda r:(-len(r['english_variants']),-r['occurrences']))
    for i,r in enumerate(reused):r['index']=i
    write(Q+'reused-short-dialogue.json',reused)
    summary=dict(source_sha256=digest(W/ctx['combined_source']),records=len(records),scene_choice_groups=len(out),scene_choice_records=sum(len(g['records']) for g in out),reused_short_groups=len(reused),reused_short_records=sum(r['occurrences'] for r in reused),all_contexts_have_JP_US_and_adjacent_records=True,manual_semantic_review_complete=False)
    write(Q+'inventory.json',summary);print(summary)
def show(kind,start,end):
    data=read(Q+('scene-choice-groups.json' if kind=='choices' else 'reused-short-dialogue.json'))
    for r in data[start:end]:
        print('\nGROUP',r['index'],Path(r.get('asset','')).name,r.get('jp',''),'=>',r.get('thai',''))
        if kind!='choices':print('US variants:',r['english_variants'])
        for x in r['records']:
            if kind=='choices':print(x['id'],x['jp'].replace('\r\n',' / '),'=>',x['thai'].replace('\r\n',' / '),'|',x['us'].replace('\r\n',' / '))
            else:print(x['id'],x['actor'],'|',x['us'].replace('\r\n',' / '))
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    elif '--inventory' in sys.argv:inventory()
    elif '--choices' in sys.argv:show('choices',int(sys.argv[-2]),int(sys.argv[-1]))
    elif '--short' in sys.argv:show('short',int(sys.argv[-2]),int(sys.argv[-1]))
    elif '--apply' in sys.argv:apply()
    elif '--audit' in sys.argv:audit()
    elif '--review-ledger' in sys.argv:review_ledger()
