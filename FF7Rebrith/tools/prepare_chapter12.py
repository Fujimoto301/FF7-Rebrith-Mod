"""Freeze the final45-pronoun-correction Ch11 release and stable Ch12 indices."""
import collections,hashlib,re,shutil,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter12_scope import scope
def main():
    assert not (W/'reference/chapter12-source.json').exists(),'Never reset stable chapter indices'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);c=read('reference/rebirth-jp-corpus.json')
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert digest(W/ctx['combined_source'])=='40693dad0d32bd096011020cdb51486209cd8f3fea5255716ca07eab50b3e69c'
    snap=W/'qa/chapter12/revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter11/editorial-signoff.json','reference/context-recheck-overrides.json','reference/context-full-read-overrides.json','reference/chapter11-recheck-overrides.json','reference/pronoun-context-overrides.json']
    for p in paths:
        dest=snap/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/p,dest)
    write('qa/chapter12/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:digest(snap/p) for p in paths},source_hashes={str(p.relative_to(W)):digest(p) for p in (W/'source').rglob('*.uasset')}))
    rows=[];ts=[];ix={}
    for a,d in c.items():
        selected=[(k,v,scope(a,k,v['Text'])) for k,v in d.items() if v['Text'] and scope(a,k,v['Text']) and k not in base['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})]
        if not selected:continue
        u=txtres.parse(str(W/'source/End/Content/Text/US'/a))
        for k,v,reason in selected:
            actor=u.get(k,{}).get('MetaData',{}).get('ACTOR','')
            token=(v['Text'],actor)
            if token not in ix:
                i=len(ts);ix[token]=i;ts.append(dict(index=i,jp=v['Text'],us=u.get(k,{}).get('Text',''),actor=actor,examples=[]))
            i=ix[token];ts[i]['examples'].append(k);rows.append(dict(asset='End/Content/Text/JP/'+a,id=k,Japanese=v,English=u.get(k,{}),template=i,reason=reason))
    write('reference/chapter12-source.json',rows);write('reference/chapter12-templates.json',ts)
    write('reference/chapter12-scope.json',dict(records=len(rows),templates=len(ts),assets=dict(collections.Counter(r['asset'] for r in rows)),categories=dict(collections.Counter(r['reason'] for r in rows)),source_sha256=digest(W/'reference/chapter12-source.json'),future_spoken_story_excluded=['C3310,C3320,C3330,C3340,C3410,C3510','Temple/Capital boss families'],all11_Ch12_odd_jobs=True,all_date_and_LOVELESS_variants=True,references=['https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-12-a-golden-key-walkthrough/','https://gamefaqs.gamespot.com/ps5/371123-final-fantasy-vii-rebirth/faqs/81141/ch12-a-golden-key'],in_game_tested=False))
    cfg=dict(chapters=list(range(1,13)),source='translations/working-through-chapter12-th.json',stage='staging/ThaiJP_ThroughChapter12_Working',qa='qa/chapter12',cluster_map='reference/through-chapter12-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json')
    write('reference/chapter12-build.json',cfg);shutil.copytree(W/ctx['stage'],W/cfg['stage'])
    (W/'translations/chapter12').mkdir(exist_ok=True)
    write('qa/chapter12/progress.json',dict(templates=len(ts),read_ranges=[],translated_templates=0,remaining_templates=len(ts),semantic_review_complete=False))
    print(read('reference/chapter12-scope.json'))
if __name__=='__main__':main()
