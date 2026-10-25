"""Source/stage/corpus/choice/metadata/gender regression audit for Ch8."""
import hashlib,re,unicodedata
from pathlib import Path
from collections import Counter
from assemble_chapter8 import W,read,write,txtres,JP
from prepare_chapter8 import in_scope
from chapter8_scope import reason
from chapter8_supplement import family,speech as shared_speech
from assemble_ui_completion import fingerprint
import verify_chapter1 as verify

def main():
    cfg=read('reference/chapter8-build.json');stage=W/cfg['stage'];base=read('qa/chapter8/baseline.json')
    old=read(base['base_source']);now=read(cfg['source']);patch=read('translations/chapter8-th.json')
    c=read('reference/rebirth-jp-corpus.json');rows=read('reference/chapter8-source.json');sup=read('reference/chapter8-supplement-source.json')
    defer=read('reference/chapter8-deferred.json');dkeys={(r['asset'],r['id']) for r in defer}
    assert {(a,k) for a,d in c.items() for k,v in d.items() if v['Text'] and in_scope(a,k) and k not in old['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})}=={(Path(r['asset']).name,r['id']) for r in rows}
    assert {r['id'] for r in defer}=={r['id'] for r in rows if reason(r['id'])}
    cm=read(cfg['cluster_map']);seed=read(cfg['seed']);assert all(cm[k]==v for k,v in seed.items())
    rev=str.maketrans({v:k for k,v in cm.items()});staged={a:txtres.parse(str(stage/a)) for a in now['assets']}
    fixes=read('translations/aerith-name-corrections.json')['changes'] if (W/'translations/aerith-name-corrections.json').exists() else []
    exceptions={(r['asset'],r['id']):r for r in fixes}
    for a,p in old['assets'].items():
        for field in ('entries','actors'):
            for k,v in p[field].items():
                if field=='entries' and (a,k) in exceptions:
                    r=exceptions[(a,k)];assert v==r['before'] and now['assets'][a][field][k]==r['after']==v.replace('แอริธ','เอริธ'),k
                    assert staged[a][k]['Text'].translate(rev)==r['after'],k
                else:assert now['assets'][a][field][k]==v,k
    for a,p in now['assets'].items():
        for field in ('entries','actors'):assert set(p[field])-set(old['assets'].get(a,{}).get(field,{}))==set(patch['assets'].get(a,{}).get(field,{}))
    expected={(r['asset'],r['id']) for r in rows if (r['asset'],r['id']) not in dkeys}|{(r['asset'],r['id']) for r in sup if r['mode']!='existing'}
    assert expected=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    reviews=[];context=[];number_review=[];choices=[];groups=Counter()
    for a,k in sorted(expected):
        src=c[Path(a).name][k];actual=staged[a][k];t=now['assets'][a]['entries'][k];actor=now['assets'][a]['actors'].get(k,'')
        assert t==patch['assets'][a]['entries'][k]==actual['Text'].translate(rev),(k,'round trip')
        assert t.strip() and not JP.search(t),k
        assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),(k,'duplicated Thai combining mark')
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
    assert {r['id'] for r in sup if r['family']=='speech'}=={k for k,v in c['Resident_TxtRes.uasset'].items() if v['Text'] and shared_speech(k)}
    for r in sup:
        if r['mode']=='official_English_name':
            assert now['assets'][resident]['entries'][r['id']]==r['English']['Text'],r['id']
            assert not r['id'].endswith(('_help','_hint','_explain')),r['id']
    for k in inventoried:assert staged[resident][k]['Text'].translate(rev)==now['assets'][resident]['entries'][k],k
    assert fingerprint()==base['protected']
    for p,h in base['source_hashes'].items():assert hashlib.sha256((W/p).read_bytes()).hexdigest()==h
    vf=read('qa/chapter8/verification.json');assert vf['chapter']==list(range(1,9)) and len(vf['fonts'])==8
    manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))}
    previous=read(base['previous_assets']);assert set(manifest)==set(previous)|{str(Path('End/Content/Text/JP/8400-GOLDE_TxtRes.uasset'))} and len(manifest)==25
    changed=[a for a in manifest if manifest[a]!=previous.get(a)]
    allowed={'Resident_TxtRes.uasset','4000-MIDGR_TxtRes.uasset','8400-GOLDE_TxtRes.uasset'}|{Path(r['asset']).name for r in fixes}
    assert all('Billboard' in a or Path(a).name in allowed for a in changed)
    write('qa/chapter8/working-assets.json',manifest);write('qa/chapter8/review-records.json',reviews)
    write('qa/chapter8/relationship-context-review.json',context);write('qa/chapter8/number-review.json',number_review);write('qa/chapter8/choice-review.json',choices)
    audit=dict(chapter=8,chapter8_records=patch['dialogue_records'],new_shared_speech=sum(r['family']=='speech' and r['mode']!='existing' for r in sup),new_UI=sum(r['family']!='speech' and r['mode']!='existing' for r in sup),
      previous_records_preserved=sum(len(p['entries']) for p in old['assets'].values()),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),
      working_assets=25,glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],scope_source_records=len(rows),deferred_records=len(defer),supplement_inventory=len(sup),
      NPC_records=sum('_NPC_' in r['id'] for r in reviews),NPC_without_ACTOR=sum('_NPC_' in r['id'] and not c[Path(r['asset']).name][r['id']].get('MetaData',{}).get('ACTOR') for r in reviews),
      groups=dict(groups),choice_records=len(choices),context_candidates=len(context),number_candidates=len(number_review),
      corpus_scope_verified=True,old_text_and_ACTOR_preserved=True,append_only_glyph_map=True,changed_assets=changed,missing=[],japanese_remaining=[],tag_mismatches=[],
      source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False)
    if fixes:
        audit.update(old_text_and_ACTOR_preserved=False,prior_record_IDs_and_ACTOR_preserved=True,
          previous_records_preserved=audit['previous_records_preserved']-len(fixes),prior_record_name_spelling_corrections=fixes)
    write('qa/chapter8/translation-audit.json',audit)
    write('qa/active-working-set.json',dict(stage=cfg['stage'],manifest='qa/chapter8/working-assets.json',audit='qa/chapter8/translation-audit.json',asset_count=25,chapters=list(range(1,9)),combined_source=cfg['source'],cluster_map=cfg['cluster_map'],
      additional_parts=[['ThaiJP_Chapter3_4_5_P',['8200-JUNOE_TxtRes.uasset']],['ThaiJP_Chapter6_7_P',['8300-CORLE_TxtRes.uasset']],['ThaiJP_Chapter8_P',['8400-GOLDE_TxtRes.uasset']]],superseded_parts=[],shared_file_note='All6 latest ZIP parts required together. Chapter8 owns GOLDE; Chapter1 MIDGR includes Zack catch-up. Common shared fonts/UI.'))
    print(audit)
if __name__=='__main__':main()
