"""Independent corpus/metadata/registered whole-family and baseline audit."""
import re,hashlib,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres,primary,shared,ui,defer
from assemble_ui_completion import fingerprint

def main():
    cfg=read('reference/chapter9-build.json');base=read('qa/chapter9/baseline.json');old=read(base['base_source']);now=read(cfg['source']);patch=read('translations/chapter9-th.json');rows=read('reference/chapter9-source.json');corpus=read('reference/rebirth-jp-corpus.json');stage=W/cfg['stage'];cm=read(cfg['cluster_map']);seed=read(cfg['seed']);rev=str.maketrans({v:k for k,v in cm.items()})
    assert all(cm[k]==v for k,v in seed.items());assert read('reference/chapter9-scope.json')['source_sha256']==hashlib.sha256((W/'reference/chapter9-source.json').read_bytes()).hexdigest()
    candidates={(f'End/Content/Text/JP/{a}',k) for a,d in corpus.items() for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and (shared(k) or ui(k))) and k not in old['assets'].get(f'End/Content/Text/JP/{a}',{}).get('entries',{})}
    assert candidates=={(r['asset'],r['id']) for r in rows}
    selected={(r['asset'],r['id']):r for r in rows if not r['reason']};assert selected.keys()=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    staged={a:txtres.parse(str(stage/a)) for a in now['assets']};review=[];choices=[];context=[];numbers=[]
    for a,p in old['assets'].items():
        for field in ('entries','actors'):assert all(now['assets'][a][field][k]==v for k,v in p[field].items()),(a,field,'old corrected Ch8 baseline changed')
    for a,p in now['assets'].items():
        for field in ('entries','actors'):assert set(p[field])-set(old['assets'].get(a,{}).get(field,{}))==set(patch['assets'].get(a,{}).get(field,{}))
        for k,t in p['entries'].items():
            assert staged[a][k]['Text'].translate(rev)==t,(k,'round trip')
            assert not re.search('แอริธ|เอเลน่า|เอนเชียนต์แมตเตอร์|นะค่ะ|ไหมค่ะ|เหรอค่ะ',t),(k,t)
            if (a,k) not in selected:continue
            r=selected[(a,k)];src=corpus[Path(a).name][k];assert src==r['Japanese'];assert not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),k
            assert re.findall('</?[^>]+>',src['Text'])==re.findall('</?[^>]+>',t),k
            assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),k
            meta=dict(src.get('MetaData',{}));actual=dict(staged[a][k].get('MetaData',{}))
            if 'ACTOR' in meta:
                assert actual.pop('ACTOR')==p['actors'][k];meta.pop('ACTOR')
            assert actual==meta,(k,'non ACTOR metadata')
            if r['group']=='speech':assert not re.search('[A-Za-z]{2,}',re.sub('<[^>]+>','',t)),(k,'English inside speech')
            item=dict(asset=a,id=k,template=r['template'],group=r['group'],actor=p['actors'].get(k,''),jp=src['Text'],thai=t);review.append(item)
            if r['group']=='system' or 'หรือไม่?' in t or re.search('選|確認|はい|いいえ|引き受け|やめ|直す',src['Text']):choices.append(item)
            if re.search('ครับ|ค่ะ|คะ|ผม|ดิฉัน|นาย|เธอ|พ่อ|แม่|สามี|ภรรยา|แฟน',t):context.append(item)
            jp=unicodedata.normalize('NFKC',re.sub('<[^>]+>','',src['Text']));jn=re.findall(r'\d+',jp);tn=re.findall(r'\d+',re.sub('<[^>]+>','',t))
            if jn or tn or re.search('[一二三四五六七八九十百千万]',jp):numbers.append(dict(item,source_numeric_runs=jn,target_numeric_runs=tn))
    deferred=[r for r in rows if r['reason']]
    for r in deferred:assert staged[r['asset']][r['id']]==r['Japanese'],r['id']
    resident='End/Content/Text/JP/Resident_TxtRes.uasset';wholeUI={k for k,v in corpus['Resident_TxtRes.uasset'].items() if v['Text'] and ui(k)}
    assert all(k in now['assets'][resident]['entries'] for k in wholeUI)
    assert fingerprint()==base['protected']
    for p,h in base['source_hashes'].items():assert hashlib.sha256((W/p).read_bytes()).hexdigest()==h,p
    manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))};assert len(manifest)==26
    prior=read(base['previous_assets']);assert set(manifest)==set(prior)|{str(Path('End/Content/Text/JP/8500-GONGE_TxtRes.uasset'))}
    changed=[a for a in manifest if manifest[a]!=prior.get(a)];assert all('Billboard' in a or Path(a).name in ['4000-MIDGR_TxtRes.uasset','8500-GONGE_TxtRes.uasset','Resident_TxtRes.uasset'] for a in changed)
    verification=read('qa/chapter9/verification.json');assert verification['chapter']==list(range(1,10)) and len(verification['fonts'])==8
    audit=dict(chapter=9,new_records=len(selected),groups=dict(Counter(r['group'] for r in review)),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),previous_records_preserved=30656,old_text_and_ACTOR_preserved=True,working_assets=26,glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],scope_source_records=len(rows),deferred_records=len(deferred),registered_UI_records=len(wholeUI),choice_candidates=len(choices),NPC_records=sum('_NPC_' in r['id'] for r in review),NPC_without_ACTOR=sum('_NPC_' in r['id'] and not r['actor'] for r in review),changed_assets=changed,missing=[],tag_mismatches=[],japanese_remaining=[],source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False)
    for name,data in [('translation-audit',audit),('working-assets',manifest),('review-records',review),('choice-review',choices),('relationship-context-review',context),('number-review',numbers)]:write('qa/chapter9/'+name+'.json',data)
    write('qa/active-working-set.json',dict(stage=cfg['stage'],manifest='qa/chapter9/working-assets.json',audit='qa/chapter9/translation-audit.json',asset_count=26,chapters=list(range(1,10)),combined_source=cfg['source'],cluster_map=cfg['cluster_map'],additional_parts=[['ThaiJP_Chapter3_4_5_P',['8200-JUNOE_TxtRes.uasset']],['ThaiJP_Chapter6_7_P',['8300-CORLE_TxtRes.uasset']],['ThaiJP_Chapter8_P',['8400-GOLDE_TxtRes.uasset']],['ThaiJP_Chapter9_P',['8500-GONGE_TxtRes.uasset']]],superseded_parts=[],shared_file_note='All7latestZIPs required together. Ch9 ownsGONGE; Chapter1MIDGR includesZack; CommonfontsResident.'))
    print(audit)

if __name__=='__main__':main()
