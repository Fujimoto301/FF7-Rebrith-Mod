"""Audit Costa's first-visit scope, prior layers, tags, numbers and native fonts."""
import hashlib,re,unicodedata
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write,values,txtres,JP
from assemble_ui_completion import fingerprint
from prepare_chapter6 import in_scope
import verify_chapter1 as v

STAGE=W/'staging/ThaiJP_ThroughChapter6_Working'
COMMON=Path('End/Content/Menu/Billboard/Common')
MALE={'Cloud','Barret','Red XIII','Rufus','Tseng','Rude','Reno','Roche','Chadley','Sephiroth','Heidegger','Glenn','Darren','Devin','Captain Titov','Hojo','Andrea','Johnny'}
FEMALE={'Tifa','Aerith','Yuffie','Elena','Scarlet','Rhonda','Priscilla','Kyrie','MAI','Regina','Madam M'}

def number_tokens(jp):
    s=re.sub('<[^>]+>','',unicodedata.normalize('NFKC',jp))
    # JP denominators precede numerators; Thai puts the numerator first.
    s=re.sub(r'(\d+)分の(\d+)',lambda m:m[2]+'/'+m[1],s)
    s=s.replace('セカンドハウス','別荘').replace('二輪車','2輪車').replace('コスタいちばん','コスタ1').replace('いち にー','1 2')
    for a,b in [('第七','第7'),('二等室','2等室'),('七番街','7番街'),('世界一','世界1'),
                ('男ふたり','男2'),('女ひとり','女1'),('セカンド','2'),('ゼロ','0'),
                ('二等船室','2等船室'),('第八神羅丸','第8神羅丸'),('ふたり','2人'),
                ('Type III','Type 3'),('二本足','2本足'),('一等客室','1等客室'),('一等の','1等の'),
                ('ナンバーワン','ナンバー1'),('七番プレート','7番プレート'),('五感','5感')]:s=s.replace(a,b)
    s=re.sub(r'(\d+)万',lambda m:str(int(m[1])*10000),s)
    return re.findall(r'\d+',s)

def main():
    baseline=read('qa/chapter6/baseline.json');old=read(baseline['base_source'])
    now=read('translations/working-through-chapter6-th.json');patch=read('translations/chapter6-th.json')
    rows=read('reference/chapter6-source.json');templates=read('reference/chapter6-templates.json');translated=values()
    deferred=read('reference/chapter6-deferred.json');deferred_keys={(r['asset'],r['id']) for r in deferred}
    ui_rows=read('reference/chapter6-ui-source.json');ui_patch=read('translations/chapter6-ui-th.json')
    activity_rows=[r for r in read('reference/chapter6-activity-ui-source.json') if r['action']=='translate']
    activity_patch=read('translations/chapter6-activity-ui-th.json')
    assert len(ui_rows)==22 and len(activity_rows)==131
    assert {r['id'] for r in activity_rows}==set(activity_patch)
    assert not ui_patch.keys()&activity_patch.keys()
    ui_rows+=activity_rows;ui_patch.update(activity_patch)
    overrides=read('reference/chapter6-ui-overrides.json');corpus=read('reference/rebirth-jp-corpus.json')
    expected={(a,k) for a,d in corpus.items() for k,x in d.items() if x['Text'] and in_scope(a,k)}
    assert expected=={(Path(r['asset']).name,r['id']) for r in rows}
    assert len(rows)==1805 and len(templates)==len(translated)==1737 and len(deferred)==107
    scope=read('reference/chapter6-scope.json')
    assert hashlib.sha256((W/'reference/chapter6-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    assert deferred_keys<={(r['asset'],r['id']) for r in rows}
    selected=[r for r in rows if (r['asset'],r['id']) not in deferred_keys]
    assert len(selected)==1698
    staged={a:txtres.parse(str(STAGE/a)) for a in now['assets']}
    cmap=read('reference/through-chapter6-cluster-map.json');oldmap=read('reference/through-chapter5-cluster-map.json')
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
        if r['template']==1337:
            # A pleasant day: indefinite greeting, not a measured one-day duration.
            assert source_numbers==['1'] and not target_numbers
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
        # Johnny explicitly calls himself 男ジョニー in template43.
        if actor in MALE:assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน',t),(k,t)
        if actor in FEMALE:assert not re.search('ครับ|กระผม',t),(k,t)
        sensitive=bool(re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',t))
        if sensitive:
            # Unidentified NPC speakers must not acquire gender-specific forms.
            assert actor in MALE|FEMALE,(k,actor,t)
            gender.append(dict(id=k,actor=actor,text=t,basis='Named character / explicit JP gender evidence'))
        if not system:
            visible=re.sub('<[^>]+>','',t)
            assert not re.search('[A-Za-z]{2,}',visible),(k,visible)
        else:
            assert not re.search('ยุฟฟี่|อวาแลนช์|ชินระ|นิเบิลไฮม์|เอมิลิโอ|ทีฟ่า|ฟอร์ทคอนดอร์',t),(k,t)
        group='system_choices' if system else 'ambient_without_actor' if not r['MetaData'].get('ACTOR') else 'named_or_labeled_dialogue'
        groups[group]+=1
        review.append(dict(id=k,template=r['template'],group=group,actor=actor,jp=r['Text'],thai=t))
    assert {r['id'] for r in ui_rows}==set(ui_patch) and len(ui_rows)==153
    for r in ui_rows:
        a=r['asset'];k=r['id'];t=ui_patch[k]
        assert corpus[Path(a).name][k]==r['Japanese']
        assert k not in old['assets'][a]['entries']
        assert staged[a][k]['Text'].translate(reverse)==now['assets'][a]['entries'][k]==patch['assets'][a]['entries'][k]==t
        assert not JP.search(t) and t.strip()
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),k
        assert staged[a][k].get('MetaData',{})==r['Japanese'].get('MetaData',{})
    assert sum(len(p['entries']) for p in patch['assets'].values())==len(selected)+len(ui_rows)
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
    write('qa/chapter6/runtime-baseline-check.json',dict(fonts=native_checks,runtime_substitutions_after_encoding=True,in_game_tested=False))
    assert fingerprint()==baseline['protected'],'Installed/legacy files changed'
    for rel,sha in baseline['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    verified=read('qa/chapter6/verification.json');assert verified['chapter']==[1,2,3,4,5,6] and len(verified['fonts'])==8
    manifest={str(p.relative_to(STAGE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(STAGE.rglob('*.uasset'))}
    previous=read(baseline['previous_assets']);assert set(manifest)==set(previous)|{str(Path("End/Content/Text/JP/8300-CORLE_TxtRes.uasset"))} and len(manifest)==23
    changed=[a for a in manifest if manifest[a]!=previous.get(a)]
    assert set(changed)<={str(Path(r['asset'])) for r in selected+ui_rows}|{a for a in previous if 'Billboard' in a}
    write('qa/chapter6/working-assets.json',manifest)
    write('qa/chapter6/editorial-review.json',dict(records=review,number_reviews=numbers,system_overrides=overrides,video_audio_verified=False))
    write('qa/chapter6/gender-review.json',dict(policy='Male ครับ; female ค่ะ statements / คะ questions / นะคะ only as appropriate. Unknown NPCs neutral; no gender inference from NPC IDs.',
        named_male=sorted(MALE),named_female=sorted(FEMALE),records=gender,gender_mismatches=[],video_audio_verified=False))
    write('qa/chapter6/translation-audit.json',dict(chapter6_records=len(selected),additional_Costa_UI_records=len(ui_rows),prepared_source_records=len(rows),templates=len(templates),deferred_later_records=len(deferred),
        total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),groups=dict(groups),
        missing_records=[],duplicate_indices=[],japanese_remaining=[],gender_mismatches=[],previous_translation_and_actor_records_preserved=True,
        scope_verified_against_full_corpus=True,old_glyph_assignments_preserved=True,new_clusters=len(cmap)-len(oldmap),
        changed_assets=changed,working_assets=len(manifest),glyph_coverage=coverage,source_and_installed_files_unchanged=True,
        installed=False,runtime_tested=False,video_audio_verified=False))
    write('qa/active-working-set.json',dict(stage='staging/ThaiJP_ThroughChapter6_Working',manifest='qa/chapter6/working-assets.json',
        audit='qa/chapter6/translation-audit.json',asset_count=23,chapters=[1,2,3,4,5,6],
        additional_parts=[['ThaiJP_Chapter3_4_5_P',['8200-JUNOE_TxtRes.uasset']],['ThaiJP_Chapter6_P',['8300-CORLE_TxtRes.uasset']]],superseded_parts=[],
        shared_file_note='GRASE in Chapter2 contains Ch.1–3; JUNOE in Chapter3_4_5 contains Ch.3–5; CORLE in Chapter6 contains Costa dialogue. Resident/fonts are shared. All five ZIPs required.'))
    print('Chapter 6 audit passed:',len(selected),'new records;',len(deferred),'later records deferred;',dict(groups))
if __name__=='__main__':main()
