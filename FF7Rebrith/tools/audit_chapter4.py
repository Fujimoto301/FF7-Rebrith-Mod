"""Audit Junon scope, preservation, tags, numbers, speaker policy and font coverage."""
import hashlib,re,unicodedata
from collections import Counter
from pathlib import Path
from assemble_chapter4 import W,read,write,values,txtres,JP
from assemble_ui_completion import fingerprint
from prepare_chapter4 import in_scope
import verify_chapter1 as v

STAGE=W/'staging/ThaiJP_ThroughChapter4_Working'
COMMON=Path('End/Content/Menu/Billboard/Common')
MALE={'Cloud','Barret','Red XIII','Rufus','Tseng','Rude','Reno','Roche','Chadley','Sephiroth','Heidegger','Glenn','Darren','Devin'}
FEMALE={'Tifa','Aerith','Yuffie','Elena','Scarlet','Rhonda','Priscilla','Kyrie','MAI'}

def number_tokens(jp):
    s=re.sub('<[^>]+>','',unicodedata.normalize('NFKC',jp))
    for a,b in [('第七','第7'),('二等室','2等室'),('七番街','7番街'),('世界一','世界1'),
                ('男ふたり','男2'),('女ひとり','女1'),('セカンド','2'),('ゼロ','0')]:s=s.replace(a,b)
    s=re.sub(r'(\d+)万',lambda m:str(int(m[1])*10000),s)
    return re.findall(r'\d+',s)

def main():
    baseline=read('qa/chapter4/baseline.json');old=read(baseline['base_source'])
    now=read('translations/working-through-chapter4-th.json');patch=read('translations/chapter4-th.json')
    rows=read('reference/chapter4-source.json');templates=read('reference/chapter4-templates.json');translated=values()
    deferred=read('reference/chapter4-deferred.json');deferred_keys={(r['asset'],r['id']) for r in deferred}
    overrides=read('reference/chapter4-ui-overrides.json');corpus=read('reference/rebirth-jp-corpus.json')
    expected={(a,k) for a,d in corpus.items() for k,x in d.items() if x['Text'] and in_scope(a,k)}
    assert expected=={(Path(r['asset']).name,r['id']) for r in rows}
    assert len(rows)==3256 and len(templates)==len(translated)==3081 and len(deferred)==50
    scope=read('reference/chapter4-scope.json')
    assert hashlib.sha256((W/'reference/chapter4-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    assert deferred_keys<={(r['asset'],r['id']) for r in rows}
    selected=[r for r in rows if (r['asset'],r['id']) not in deferred_keys]
    assert len(selected)==3206
    staged={a:txtres.parse(str(STAGE/a)) for a in now['assets']}
    cmap=read('reference/through-chapter4-cluster-map.json');oldmap=read('reference/through-chapter3-cluster-map.json')
    assert all(cmap[k]==x for k,x in oldmap.items())
    reverse=str.maketrans({x:k for k,x in cmap.items()})
    for a,p in old['assets'].items():
        for field in ('entries','actors'):
            assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),(a,field)
    for a,p in now['assets'].items():
        for field in ('entries','actors'):
            added=set(p[field])-set(old['assets'].get(a,{}).get(field,{}))
            assert added==set(patch['assets'].get(a,{}).get(field,{})),(a,field)
    review=[];gender=[];numbers=[];groups=Counter()
    for r in rows:
        a=r['asset'];k=r['id'];source=corpus[Path(a).name][k]
        assert source['Text']==r['Text'] and source.get('MetaData',{})==r['MetaData'],k
        if (a,k) in deferred_keys:
            assert k not in patch['assets'].get(a,{}).get('entries',{})
            assert staged[a][k]==source,k
            continue
        t=overrides.get(k,translated[str(r['template'])]);system=k.endswith('_sys')
        assert patch['assets'][a]['entries'][k]==now['assets'][a]['entries'][k]==staged[a][k]['Text'].translate(reverse)==t,k
        assert not JP.search(t) and t.strip(),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Text']),k
        source_numbers=number_tokens(r['Text']);target_numbers=re.findall(r'\d+',re.sub('<[^>]+>','',t))
        # JP 1日 here means "this memorable day", not a one-day duration.
        if r['template']==1349:assert source_numbers==['1'] and not target_numbers
        elif r['template']==822:assert source_numbers==['7','2'] and target_numbers==['2','7']
        else:assert source_numbers==target_numbers,(r['template'],k,source_numbers,target_numbers)
        if source_numbers or target_numbers:numbers.append(dict(id=k,jp=r['Text'],thai=t,semantic_numbers_verified=True))
        assert not re.search('นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|เซคเตอร์เจ็ด',t),k
        label=patch['assets'][a]['actors'].get(k,'')
        actor=r['English'].get('MetaData',{}).get('ACTOR','') or label
        if r['MetaData'].get('ACTOR'):
            assert label and not JP.search(label),k
            if r['English'].get('MetaData',{}).get('ACTOR'):assert label==r['English']['MetaData']['ACTOR'],k
            if re.fullmatch('[？?]+',r['MetaData']['ACTOR']):assert re.fullmatch('[?]+',label),k
        else:assert k not in patch['assets'][a]['actors'],k
        if actor in MALE:assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน',t),(k,t)
        if actor in FEMALE:assert not re.search('ครับ|กระผม|ดิฉัน',t),(k,t)
        sensitive=bool(re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',t))
        if sensitive:
            # Unknown NPCs have neutral language; ผม in this record means hair.
            assert actor in MALE|FEMALE or r['template']==1635,(k,actor,t)
            gender.append(dict(id=k,actor=actor,text=t,basis='Named character / explicit brothers introduction' if actor in MALE|FEMALE else 'ผม means hair, not a male pronoun'))
        if not system:
            visible=re.sub('<[^>]+>','',t)
            # Zone letters and the in-world version identifier are retained.
            assert not re.search('[A-Za-z]{2,}',visible.replace('CH-2','')),(k,visible)
        else:
            assert not re.search('ยุฟฟี่|อวาแลนช์|ชินระ|นิเบิลไฮม์|เอมิลิโอ|ทีฟ่า|ฟอร์ทคอนดอร์',t),(k,t)
        group='system_choices' if system else 'ambient_without_actor' if not r['MetaData'].get('ACTOR') else 'named_or_labeled_dialogue'
        groups[group]+=1
        review.append(dict(id=k,template=r['template'],group=group,actor=actor,jp=r['Text'],thai=t))
    assert sum(len(p['entries']) for p in patch['assets'].values())==len(selected)
    coverage=[];all_text=[t for p in now['assets'].values() for t in p['entries'].values()]
    for size in ('Normal','Small'):
        glyphs={g[0] for g in v.glyphs((STAGE/COMMON/f'U_Com_JP_SystemFont{size}.uasset').read_bytes())[0]}
        for text in all_text:
            for cluster in v.b.split_clusters(re.sub('<[^>]+>','',text)):
                if not cluster.isspace():assert all(ord(ch) in glyphs for ch in cmap.get(cluster,cluster)),(size,cluster)
        coverage.append(dict(font=size,all_combined_text_covered=True))
    native_checks=[]
    for path in sorted((STAGE/COMMON).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        gs={g[0]:g for g in v.glyphs(path.read_bytes())[0]};pages={}
        def bottom(code):
            g=gs[code]
            if g[1] not in pages:
                p=path.with_name(path.stem+f'-{g[1]:02d}.uasset')
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            mask=pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
            return g[7]+mask.point(lambda p:255 if p>=64 else 0).getbbox()[3]
        h=bottom(ord('H'));assert h==bottom(ord(cmap['ก']))
        overshoot={c:bottom(ord(c))-h for c in '0123456789'}
        assert max(map(abs,overshoot.values()))<=2,(path.name,overshoot)
        assert all(bottom(ord(cmap[c]))==h for c in '0123456789')
        native_checks.append(dict(font=path.name,native_H_and_thai_baseline=h,native_digit_overshoot=overshoot,
            aliases_aligned=True,native_ASCII_preserved=True))
    assert len(native_checks)==8
    write('qa/chapter4/runtime-baseline-check.json',dict(fonts=native_checks,runtime_substitutions_after_encoding=True,in_game_tested=False))
    assert fingerprint()==baseline['protected'],'Installed/legacy files changed'
    for rel,sha in baseline['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    verified=read('qa/chapter4/verification.json');assert verified['chapter']==[1,2,3,4] and len(verified['fonts'])==8
    manifest={str(p.relative_to(STAGE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(STAGE.rglob('*.uasset'))}
    previous=read(baseline['previous_assets']);assert set(previous)==set(manifest) and len(manifest)==22
    changed=[a for a in manifest if manifest[a]!=previous[a]]
    assert set(changed)<={str(Path(r['asset'])) for r in selected}|{a for a in previous if 'Billboard' in a}
    write('qa/chapter4/working-assets.json',manifest)
    write('qa/chapter4/editorial-review.json',dict(records=review,number_reviews=numbers,system_overrides=overrides,video_audio_verified=False))
    write('qa/chapter4/gender-review.json',dict(policy='Male ครับ; female ค่ะ statements / คะ questions / นะคะ only as appropriate. Unknown NPCs neutral; no gender inference from NPC IDs.',
        named_male=sorted(MALE),named_female=sorted(FEMALE),records=gender,gender_mismatches=[],video_audio_verified=False))
    write('qa/chapter4/translation-audit.json',dict(chapter4_records=len(selected),prepared_source_records=len(rows),templates=len(templates),deferred_later_records=len(deferred),
        total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),groups=dict(groups),
        missing_records=[],duplicate_indices=[],japanese_remaining=[],gender_mismatches=[],previous_translation_and_actor_records_preserved=True,
        scope_verified_against_full_corpus=True,old_glyph_assignments_preserved=True,new_clusters=len(cmap)-len(oldmap),
        changed_assets=changed,working_assets=len(manifest),glyph_coverage=coverage,source_and_installed_files_unchanged=True,
        installed=False,runtime_tested=False,video_audio_verified=False))
    write('qa/active-working-set.json',dict(stage='staging/ThaiJP_ThroughChapter4_Working',manifest='qa/chapter4/working-assets.json',
        audit='qa/chapter4/translation-audit.json',asset_count=22,chapters=[1,2,3,4],
        additional_parts=[['ThaiJP_Chapter3_4_P',['8200-JUNOE_TxtRes.uasset']]],superseded_parts=['ThaiJP_Chapter3_P']))
    print('Chapter 4 audit passed:',len(selected),'new records;',len(deferred),'later records deferred;',dict(groups))
if __name__=='__main__':main()
