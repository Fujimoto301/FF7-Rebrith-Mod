"""Freeze the fully reviewed Ch1-10 base; create stable Ch11 source indices."""
import collections,hashlib,re,shutil,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter11_scope import primary,shared,defer

def main():
    assert not (W/'reference/chapter11-source.json').exists(),'Preserve immutable Ch11 indices'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);c=read('reference/rebirth-jp-corpus.json')
    assert hashlib.sha256((W/ctx['combined_source']).read_bytes()).hexdigest()=='63c3e1515ac4130a05bf8126af2a50362e6a7c832a2d81613c4559e8a1f43802'
    snap=W/'qa/chapter11/revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter10/editorial-signoff.json','reference/context-recheck-overrides.json','reference/context-full-read-overrides.json']
    for rel in paths:
        target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,target)
    write('qa/chapter11/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:hashlib.sha256((snap/p).read_bytes()).hexdigest() for p in paths},source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    rows=[];ts=[];ix={};late=[]
    for a,d in c.items():
        candidates=[(k,v) for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and shared(k))]
        if not candidates:continue
        rel='End/Content/Text/JP/'+a;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v in candidates:
            if k in base['assets'].get(rel,{}).get('entries',{}):continue
            r=dict(asset=rel,id=k,Japanese=v,English=us.get(k,{}),reason=defer(k))
            if r['reason']:late.append(r);continue
            actor=re.sub('<[^>]+>','',us.get(k,{}).get('MetaData',{}).get('ACTOR',''))
            # Exact duplicates retained as templates only within their actor.
            token=(v['Text'],actor)
            if token not in ix:
                i=len(ts);ix[token]=i;ts.append(dict(index=i,jp=v['Text'],us=us.get(k,{}).get('Text',''),actor=actor,examples=[]))
            i=ix[token];ts[i]['examples'].append(k);r['template']=i;rows.append(r)
    write('reference/chapter11-source.json',rows);write('reference/chapter11-templates.json',ts);write('reference/chapter11-deferred.json',late)
    write('reference/chapter11-scope.json',dict(records=len(rows),templates=len(ts),assets=dict(collections.Counter(r['asset'] for r in rows)),deferred=len(late),source_sha256=hashlib.sha256((W/'reference/chapter11-source.json').read_bytes()).hexdigest(),boundaries={'main':'C3110 only; C3210 begins Chapter12','odd_jobs':'NIBLE_QST_01/02; QST03 explicitly deferred','NPC':'All NIBLT_NPC_20 states, NIBLS boss dialogue and CHADL_QST_06','shared':'Nibel Chadley/MAI, Snaps, Dale/Turner, Odin and full regional-intel families'},references=['https://www.powerpyx.com/final-fantasy-7-vii-rebirth-my-white-haired-angel-walkthrough/','https://www.powerpyx.com/final-fantasy-7-vii-rebirth-lament-of-the-damned-walkthrough/'],in_game_tested=False))
    cfg=dict(chapters=list(range(1,12)),source='translations/working-through-chapter11-th.json',stage='staging/ThaiJP_ThroughChapter11_Working',qa='qa/chapter11',cluster_map='reference/through-chapter11-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json')
    write('reference/chapter11-build.json',cfg);shutil.copytree(W/ctx['stage'],W/cfg['stage'])
    (W/'translations/chapter11').mkdir(exist_ok=True)
    print(read('reference/chapter11-scope.json'))

if __name__=='__main__':main()
