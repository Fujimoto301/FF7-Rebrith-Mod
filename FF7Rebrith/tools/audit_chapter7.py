"""Source/stage/corpus/choice/metadata/gender regression audit for Ch7."""
import hashlib,re,unicodedata
from pathlib import Path
from collections import Counter
from assemble_chapter7 import W,read,write,txtres,JP
from prepare_chapter7 import in_scope
from chapter7_scope import reason
from chapter7_supplement import family
from assemble_ui_completion import fingerprint
import verify_chapter1 as verify

def main():
    cfg=read('reference/chapter7-build.json');stage=W/cfg['stage'];base=read('qa/chapter7/baseline.json')
    old=read(base['base_source']);now=read(cfg['source']);patch=read('translations/chapter7-th.json')
    c=read('reference/rebirth-jp-corpus.json');rows=read('reference/chapter7-source.json');sup=read('reference/chapter7-supplement-source.json')
    defer=read('reference/chapter7-deferred.json');dkeys={(r['asset'],r['id']) for r in defer}
    assert {(a,k) for a,d in c.items() for k,v in d.items() if v['Text'] and in_scope(a,k)}=={(Path(r['asset']).name,r['id']) for r in rows}
    assert {r['id'] for r in defer}=={r['id'] for r in rows if reason(r['id'])}
    cm=read(cfg['cluster_map']);seed=read(cfg['seed']);assert all(cm[k]==v for k,v in seed.items())
    rev=str.maketrans({v:k for k,v in cm.items()});staged={a:txtres.parse(str(stage/a)) for a in now['assets']}
    for a,p in old['assets'].items():
        for field in ('entries','actors'):assert all(now['assets'][a][field][k]==v for k,v in p[field].items())
    for a,p in now['assets'].items():
        for field in ('entries','actors'):assert set(p[field])-set(old['assets'][a][field])==set(patch['assets'].get(a,{}).get(field,{}))
    expected={(r['asset'],r['id']) for r in rows if (r['asset'],r['id']) not in dkeys}|{(r['asset'],r['id']) for r in sup if r['mode']!='existing'}
    assert expected=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    reviews=[];context=[];number_review=[];choices=[];groups=Counter()
    for a,k in sorted(expected):
        src=c[Path(a).name][k];actual=staged[a][k];t=now['assets'][a]['entries'][k];actor=now['assets'][a]['actors'].get(k,'')
        assert t==patch['assets'][a]['entries'][k]==actual['Text'].translate(rev),(k,'round trip')
        assert t.strip() and not JP.search(t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',src['Text']),k
        meta=dict(src.get('MetaData',{}));target=dict(actual.get('MetaData',{}))
        if 'ACTOR' in meta:
            assert target.pop('ACTOR')==actor and actor and not JP.search(actor),k
            meta.pop('ACTOR')
        assert meta==target,(k,'non-ACTOR metadata')
        system=k.endswith('_sys');speech=any(r['id']==k and r['asset']==a for r in rows) or any(r['id']==k and r['family']=='speech' for r in sup)
        if speech and not system:assert not re.search('[A-Za-z]{2,}',re.sub('<[^>]+>','',t)),(k,'proper name left English in speech')
        if system and src['Text']=='はい':assert t=='ใช่',k
        if system and src['Text']=='いいえ':assert t=='ไม่ใช่',k
        assert not re.search('นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|เซคเตอร์เจ็ด',t),k
        if system or 'หรือไม่?' in t:choices.append(dict(asset=a,id=k,jp=src['Text'],thai=t))
        if re.search('ครับ|ค่ะ|คะ(?=[^\u0e00-\u0e7f]|$)|ผม|ดิฉัน|นาย|เธอ|พ่อ|แม่|พี่|น้อง|สามี|ภรรยา|แฟน|หนุ่ม|สาว|ชาย|หญิง',t):context.append(dict(id=k,actor=actor,jp=src['Text'],thai=t))
        j=re.sub('<[^>]+>','',unicodedata.normalize('NFKC',src['Text']));th=re.sub('<[^>]+>','',t)
        jn=re.findall(r'\d+',j);tn=re.findall(r'\d+',th)
        if jn or tn or re.search('[一二三四五六七八九十百千万]',j):number_review.append(dict(id=k,jp=src['Text'],thai=t,source_numeric_runs=jn,target_numeric_runs=tn))
        group='system' if system else 'speech' if speech else 'UI';groups[group]+=1
        reviews.append(dict(asset=a,id=k,group=group,actor=actor,jp=src['Text'],thai=t))
    for r in defer:
        assert staged[r['asset']][r['id']]==c[Path(r['asset']).name][r['id']],r['id']
    # The full UI family, including existing entries, must be represented in staging.
    resident='End/Content/Text/JP/Resident_TxtRes.uasset'
    inventoried={r['id'] for r in sup if r['asset']==resident and r['family']!='speech'}
    assert inventoried=={k for k,v in c['Resident_TxtRes.uasset'].items() if v['Text'] and family(k)}
    for k in inventoried:assert staged[resident][k]['Text'].translate(rev)==now['assets'][resident]['entries'][k],k
    assert fingerprint()==base['protected']
    for p,h in base['source_hashes'].items():assert hashlib.sha256((W/p).read_bytes()).hexdigest()==h
    vf=read('qa/chapter7/verification.json');assert vf['chapter']==list(range(1,8)) and len(vf['fonts'])==8
    manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))}
    previous=read(base['previous_assets']);assert set(manifest)==set(previous) and len(manifest)==24
    changed=[a for a in manifest if manifest[a]!=previous[a]]
    assert all('Billboard' in a or Path(a).name in {'Resident_TxtRes.uasset','8300-CORLE_TxtRes.uasset'} for a in changed)
    write('qa/chapter7/working-assets.json',manifest);write('qa/chapter7/review-records.json',reviews)
    write('qa/chapter7/relationship-context-review.json',context);write('qa/chapter7/number-review.json',number_review);write('qa/chapter7/choice-review.json',choices)
    audit=dict(chapter=7,chapter7_records=patch['dialogue_records'],new_shared_speech=sum(r['family']=='speech' and r['mode']!='existing' for r in sup),new_UI=sum(r['family']!='speech' and r['mode']!='existing' for r in sup),
      previous_records_preserved=sum(len(p['entries']) for p in old['assets'].values()),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),
      working_assets=24,glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],scope_source_records=len(rows),deferred_records=len(defer),supplement_inventory=len(sup),
      NPC_records=sum('_NPC_' in r['id'] for r in reviews),NPC_without_ACTOR=sum('_NPC_' in r['id'] and not c[Path(r['asset']).name][r['id']].get('MetaData',{}).get('ACTOR') for r in reviews),
      groups=dict(groups),choice_records=len(choices),context_candidates=len(context),number_candidates=len(number_review),
      corpus_scope_verified=True,old_text_and_ACTOR_preserved=True,append_only_glyph_map=True,changed_assets=changed,missing=[],japanese_remaining=[],tag_mismatches=[],
      source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False)
    write('qa/chapter7/translation-audit.json',audit)
    write('qa/active-working-set.json',dict(stage=cfg['stage'],manifest='qa/chapter7/working-assets.json',audit='qa/chapter7/translation-audit.json',asset_count=24,chapters=list(range(1,8)),combined_source=cfg['source'],cluster_map=cfg['cluster_map'],
      additional_parts=[['ThaiJP_Chapter3_4_5_P',['8200-JUNOE_TxtRes.uasset']],['ThaiJP_Chapter6_7_P',['8300-CORLE_TxtRes.uasset']]],superseded_parts=['ThaiJP_Chapter6_P'],shared_file_note='User chose Chapter6_7 name; CORLE shared by6–7. All5 ZIP parts required together.'))
    print(audit)
if __name__=='__main__':main()
