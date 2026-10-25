"""Review every current นาย/เธอ record against speaker and source context."""
import copy,re,shutil,sys,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from audit_chapter11 import digest
Q='qa/pronoun-context/';OV='reference/pronoun-context-overrides.json'

def prepare():
    assert not (W/Q/'baseline.json').exists(),'Keep the original review queue and baseline'
    from assemble_ui_completion import fingerprint
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);corpus=read('reference/rebirth-jp-corpus.json');rows=[]
    for a,p in now['assets'].items():
        us=txtres.parse(str(W/'source/End/Content/Text/US'/Path(a).name));src=corpus[Path(a).name]
        for k,j in src.items():
            t=p['entries'].get(k,'')
            if 'นาย' not in t and 'เธอ' not in t:continue
            rows.append(dict(index=len(rows),asset=a,id=k,thai=t,jp=j['Text'],us=us.get(k,{}).get('Text',''),actor=p['actors'].get(k,j.get('MetaData',{}).get('ACTOR','')),jp_actor=j.get('MetaData',{}).get('ACTOR','')))
    snap=W/Q/'revisions'/uuid.uuid4().hex
    files=[ctx['combined_source'],ctx['manifest'],ctx['cluster_map'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter11/editorial-signoff.json','translations/chapter11-th.json']
    for f in files:
        dest=snap/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/f,dest)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,hashes={f:digest(snap/f) for f in files},protected=fingerprint()))
    write(Q+'queue.json',dict(source_sha256=digest(W/ctx['combined_source']),records=rows))
    write(Q+'progress.json',dict(total=len(rows),reviewed_ranges=[],complete=False))
    write(OV,dict(records=[]))
    print('Frozen',len(rows),'candidate IDs')

def show(start,end):
    for r in read(Q+'queue.json')['records'][start:end]:
        print(f"\n[{r['index']}] {Path(r['asset']).name} {r['id']} |{r['actor']} ({r['jp_actor']})")
        print('JP',r['jp'].replace('\r\n',' / '));print('TH',r['thai'].replace('\r\n',' / '));print('US',r['us'].replace('\r\n',' / '))

def context(indices):
    c=read('reference/rebirth-jp-corpus.json');now=read(read('qa/active-working-set.json')['combined_source']);rows=read(Q+'queue.json')['records']
    for n in indices:
        r=rows[n];a=r['asset'];d=c[Path(a).name];keys=list(d);i=keys.index(r['id']);print('\nCONTEXT',n,r['id'])
        for k in keys[max(0,i-3):i+4]:
            v=d[k];p=now['assets'][a];print(k,'|',p['actors'].get(k,v.get('MetaData',{}).get('ACTOR','')),'|',v['Text'].replace('\r\n',' / '),'|',p['entries'].get(k,'[not translated]').replace('\r\n',' / '))

def decisions():return read(OV)['records'] if (W/OV).exists() else []

def matches(a,k,before,after):
    return any(r['asset']==a and r['id']==k and after==r['after'] and before in r.get('accepted_before',[r['before']]) for r in decisions())

def overlay(now):
    for r in decisions():
        e=now['assets'].get(r['asset'],{}).get('entries',{})
        if r['id'] not in e:continue
        assert e[r['id']]==r['after'] or matches(r['asset'],r['id'],e[r['id']],r['after']),r['id']
        e[r['id']]=r['after']

def commit():
    b=read(Q+'baseline.json');snap=Path(b['snapshot']);ctx=b['active'];old=read(snap/ctx['combined_source']);now=read(ctx['combined_source'])
    expected=copy.deepcopy(old);overlay(expected)
    assert now==expected,'Only commit over the frozen release plus already reviewed pronoun corrections'
    now=copy.deepcopy(old)
    rows=read(Q+'corrections-draft.json')['records'];histpaths=[snap/ctx['combined_source'],W/'translations/working-npc-recheck-th.json']
    for f in ['qa/chapter11/baseline.json','qa/chapter11/recheck/baseline.json','qa/context-full-read/baseline.json','qa/context-recheck/baseline.json']:
        h=read(f);histpaths.append(Path(h['snapshot'])/h['active']['combined_source'])
    histories=[read(p) for p in histpaths]
    for r in rows:
        assert old['assets'][r['asset']]['entries'][r['id']]==r['before']
        r['accepted_before']=sorted({h['assets'].get(r['asset'],{}).get('entries',{}).get(r['id']) for h in histories}-{None})
        assert re.findall('<[^>]+>',r['before'])==re.findall('<[^>]+>',r['after'])
        assert re.findall(r'\d+',r['before'])==re.findall(r'\d+',r['after'])
    write(Q+'historical-inputs.json',dict(files={str(p):digest(p) for p in histpaths}))
    write(OV,dict(records=rows,all499_candidates_reviewed=True))
    overlay(now);write(ctx['combined_source'],now)
    patch=read('translations/chapter11-th.json');overlay(patch);write('translations/chapter11-th.json',patch)
    print('Applied',len(rows),'per-ID corrections; no ID/actor changes')

def audit():
    from assemble_ui_completion import fingerprint
    b=read(Q+'baseline.json');snap=Path(b['snapshot']);ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);old=read(snap/b['active']['combined_source']);ds=decisions();ix={(r['asset'],r['id']):r for r in ds}
    for f,h in b['hashes'].items():assert digest(snap/f)==h,f
    assert fingerprint()==b['protected']
    assert old['assets'].keys()==now['assets'].keys()
    changed=[]
    for a,p in old['assets'].items():
        assert p['actors']==now['assets'][a]['actors'] and p['entries'].keys()==now['assets'][a]['entries'].keys()
        for k,t in p['entries'].items():
            n=now['assets'][a]['entries'][k];r=ix.get((a,k))
            assert n==(r['after'] if r else t),(k,'Unreviewed edit')
            if r:
                assert r['before']==t and n!=t
                assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',n) and re.findall(r'\d+',t)==re.findall(r'\d+',n)
                changed.append((a,k))
    assert len(changed)==len(ds)==45
    assert digest(W/ctx['cluster_map'])==digest(snap/b['active']['cluster_map'])
    manifest=read(ctx['manifest']);prior=read(snap/b['active']['manifest'])
    assert manifest.keys()==prior.keys()
    actual={a.replace('\\','/') for a,h in manifest.items() if prior[a]!=h}
    assert actual=={a for a,k in changed}
    assert all(prior[a]==h for a,h in manifest.items() if 'SystemFont' in a)
    progress=read(Q+'progress.json');assert progress['complete'] and progress['reviewed_records']==499 and progress['remaining_records']==0
    queue=read(Q+'queue.json');expected={(a,k) for a,p in old['assets'].items() for k,t in p['entries'].items() if 'นาย' in t or 'เธอ' in t}
    assert expected=={(r['asset'],r['id']) for r in queue['records']}
    results=[]
    for r in queue['records']:
        correction=ix.get((r['asset'],r['id']));t=r['thai']
        lexical=re.sub('นายกเทศมนตรี|นายกฯ|นายแบบ|นายพราน|เจ้านาย|ผู้เป็นนาย|ทำนาย|บทสนทนายาม|อีเธอร์|บราเธอร์','',t)
        kind='correction' if correction else 'lexical_only' if 'นาย' not in lexical and 'เธอ' not in lexical else 'context_kept'
        results.append(dict(r,decision=kind,after=now['assets'][r['asset']]['entries'][r['id']],reason=correction['reason'] if correction else 'JP/US and Thai meaning reviewed: occupational/lexical use only.' if kind=='lexical_only' else 'Read in context; retain male or mixed-party นาย, female reference/address เธอ, quoted/song/pet personification, or the established local conversation. No blanket gender replacement.'))
    write(Q+'decisions.json',dict(source_sha256=digest(W/ctx['combined_source']),records=results))
    report=dict(source_sha256=digest(W/ctx['combined_source']),reviewed_records=499,remaining_records=0,corrected_records=45,kept_records=454,lexical_only_records=sum(r['decision']=='lexical_only' for r in results),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),all_other_text_ACTOR_tags_numbers_fonts_map_preserved=True,changed_assets=sorted(actual),protected_files_unchanged=True,in_game_tested=False)
    write(Q+'audit.json',report);print('Pronoun context audit:',len(results),'read,45 corrected; IDs/actors/fonts/map preserved')

if __name__=='__main__':
    if sys.argv[1]=='--prepare':prepare()
    elif sys.argv[1]=='--show':show(int(sys.argv[2]),int(sys.argv[3]))
    elif sys.argv[1]=='--context':context([int(s) for s in sys.argv[2:]])
    elif sys.argv[1]=='--commit':commit()
    elif sys.argv[1]=='--audit':audit()
