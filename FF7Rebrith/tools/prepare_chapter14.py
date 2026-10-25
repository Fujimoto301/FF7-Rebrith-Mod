"""Freeze the final rechecked Ch13 release; never reset stable template indices."""
import collections,hashlib,shutil,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter14_scope import scope
def main():
    assert not (W/'reference/chapter14-source.json').exists(),'Never prepare twice'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);c=read('reference/rebirth-jp-corpus.json')
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert digest(W/ctx['combined_source'])=='e128a336eda9b01749107fd5c437807868a383e6364b39020804e7a467b59145'
    snap=W/'qa/chapter14/revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter13/editorial-signoff.json','qa/chapter13/gender/records.json','reference/chapter13-recheck-overrides.json','qa/chapter13/recheck/release-verification.json']
    for p in paths:
        dest=snap/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/p,dest)
    write('qa/chapter14/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:digest(snap/p) for p in paths},source_hashes={str(p.relative_to(W)):digest(p) for p in (W/'source').rglob('*.uasset')}))
    rows=[];ts=[];ix={}
    for a,d in c.items():
        selected=[(k,v,scope(a,k,v['Text'])) for k,v in d.items() if v['Text'] and scope(a,k,v['Text']) and k not in base['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})]
        if not selected:continue
        u=txtres.parse(str(W/'source/End/Content/Text/US'/a))
        for k,v,reason in selected:
            actor=u.get(k,{}).get('MetaData',{}).get('ACTOR','');token=(v['Text'],actor)
            if token not in ix:
                i=len(ts);ix[token]=i;ts.append(dict(index=i,jp=v['Text'],us=u.get(k,{}).get('Text',''),actor=actor,examples=[]))
            i=ix[token];ts[i]['examples'].append(k);rows.append(dict(asset='End/Content/Text/JP/'+a,id=k,Japanese=v,English=u.get(k,{}),template=i,reason=reason))
    write('reference/chapter14-source.json',rows);write('reference/chapter14-templates.json',ts)
    write('reference/chapter14-scope.json',dict(records=len(rows),templates=len(ts),assets=dict(collections.Counter(r['asset'] for r in rows)),categories=dict(collections.Counter(r['reason'] for r in rows)),source_sha256=digest(W/'reference/chapter14-source.json'),future_spoken_story_excluded=[],references=['https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-14-end-of-the-world-walkthrough/','https://gamers-high.com/ff7-rebirth/story/chapter14.html','https://www.youtube.com/watch?v=BIHjKH4c1BI'],reference_limits='Walkthrough boundaries and video metadata; not a full audio/video review',in_game_tested=False))
    cfg=dict(chapters=list(range(1,15)),source='translations/working-through-chapter14-th.json',stage='staging/ThaiJP_ThroughChapter14_Working',qa='qa/chapter14',cluster_map='reference/through-chapter14-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json')
    write('reference/chapter14-build.json',cfg);shutil.copytree(W/ctx['stage'],W/cfg['stage'])
    shutil.copy2(W/'source/End/Content/Text/JP/8900-CAPIT_TxtRes.uasset',W/cfg['stage']/'End/Content/Text/JP/8900-CAPIT_TxtRes.uasset')
    (W/'translations/chapter14').mkdir(exist_ok=True)
    write('qa/chapter14/progress.json',dict(templates=len(ts),read_ranges=[],translated_templates=0,remaining_templates=len(ts),semantic_review_complete=False))
    print(read('reference/chapter14-scope.json'))
if __name__=='__main__':main()
