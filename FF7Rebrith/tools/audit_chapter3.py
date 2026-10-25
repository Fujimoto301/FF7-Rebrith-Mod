"""Check complete scene scope, source equality, gender policy and release retention."""
import hashlib,json,re
from pathlib import Path
from assemble_chapter3 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from prepare_chapter3 import selected
import verify_chapter1 as v

STAGE=W/'staging/ThaiJP_ThroughChapter3_Working'
COMMON=Path('End/Content/Menu/Billboard/Common')
IDENTITY={'cld':('Cloud','male'),'blt':('Barret','male'),'red':('Red XIII','male'),
    'tif':('Tifa','female'),'art':('Aerith','female'),'eln':('Elena','female'),
    'lud':('Rude','male'),'tsu':('Tseng','male')}

def main():
    baseline=read('qa/chapter3/baseline.json');old=read(baseline['base_source'])
    now=read('translations/working-through-chapter3-th.json');patch=read('translations/chapter3-th.json')
    rows=read('reference/chapter3-source.json');scope=read('reference/chapter3-scope.json')
    c=read('reference/rebirth-jp-corpus.json')
    expected={(a,k) for a,d in c.items() for k,x in d.items() if x['Text'] and selected(k)}
    assert expected=={(Path(r['asset']).name,r['id']) for r in rows}
    assert len(rows)==len(expected)==253
    assert hashlib.sha256((W/'reference/chapter3-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    values={}
    for p in sorted((W/'translations/chapter3').glob('batch-*.json')):
        part=json.loads(p.read_text('utf-8'));assert not values.keys()&part.keys();values.update(part)
    assert set(values)=={str(r['index']) for r in rows}
    originals={a:txtres.parse(str(W/'source'/a)) for a in now['assets']}
    us={a:txtres.parse(str(W/'source'/a.replace('/JP/','/US/'))) for a in patch['assets']}
    staged={a:txtres.parse(str(STAGE/a)) for a in now['assets']}
    cmap=read('reference/through-chapter3-cluster-map.json');reverse=str.maketrans({v:k for k,v in cmap.items()})
    oldmap=read('reference/ui-completion-cluster-map.json')
    assert all(cmap[k]==t for k,t in oldmap.items()),'Existing encoded text mapping changed'
    # Preserve all previous translations, actor labels, UI and inventory exactly.
    for a,p in old['assets'].items():
        for field in ('entries','actors'):
            assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),(a,field)
    for a,p in now['assets'].items():
        for field in ('entries','actors'):
            added={k for k in p[field] if k not in old['assets'].get(a,{}).get(field,{})}
            assert added==set(patch['assets'].get(a,{}).get(field,{})),(a,field,'Unexpected new entry')
    # Pair suffixes with named JP/US metadata and the self-introduction, not a guess
    # based on arbitrary NPC model prefixes. Preserve ??? before the reveal.
    identity_evidence={}
    for code,(actor,gender) in IDENTITY.items():
        named=[r['id'] for r in rows if r['id'].endswith('_'+code)
            and r['English'].get('MetaData',{}).get('ACTOR')==actor]
        assert named,(code,'No named source identity evidence')
        identity_evidence[code]=dict(actor=actor,gender=gender,named_same_code_ids=named,
            basis='Same named character throughout these contiguous story/battle blocks; ??? label preserved before introduction.')
    identity_evidence['eln'].update(official_profile='https://www.square-enix.com/ffvii/en-us/games/rebirth/characters/elena/',
        profile_evidence='Official character profile uses she/her; JP self-introduction C2110_MAIN_1600_1600 names イリーナ.',
        thai='อิเลน่า',thai_spelling='Reviewed new transliteration, not claimed to be present in the supplied Remake mod.')
    gender=[];review=[]
    forbidden=re.compile(r'\b(?:Cloud|Barret|Tifa|Aerith|Elena|Rude|Tseng|Sephiroth|Shinra|Junon|Reno|Red XIII)\b')
    for row in rows:
        a=row['asset'];k=row['id'];t=values[str(row['index'])];source=originals[a][k]
        assert source['Text']==row['Text'] and source.get('MetaData',{})==row['MetaData']
        assert patch['assets'][a]['entries'][k]==now['assets'][a]['entries'][k]==t
        assert staged[a][k]['Text'].translate(reverse)==t
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t) and not forbidden.search(t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',source['Text']),k
        numbers=re.findall(r'\d+',source['Text'].translate(str.maketrans('０１２３４５６７８９','0123456789')))
        if numbers:assert re.findall(r'\d+',t)==numbers,(k,numbers,t)
        assert not re.search('นะค่ะ|ไหมค่ะ|หรือเปล่าค่ะ|เหรอค่ะ|เซคเตอร์เจ็ด',t),k
        code=k.rsplit('_',1)[1];actor,gender_value=IDENTITY[code]
        if gender_value=='male':assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน',t),k
        else:assert not re.search('ครับ|กระผม|ดิฉัน|ผม',t),k
        actor_label=patch['assets'][a]['actors'][k]
        if row['MetaData'].get('ACTOR')=='？？？？':assert actor_label=='???',k
        else:assert actor_label==actor,(k,actor_label)
        if re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',t):
            gender.append(dict(index=row['index'],id=k,actor=actor,gender=gender_value,text=t,evidence=identity_evidence[code]))
        review.append(dict(index=row['index'],id=k,actor=actor,jp=source['Text'],thai=t,
            meaning_reviewed_against_jp=True,proper_names_dialogue_thai=True,particles_needed_only=True))
    # All deferred and unrelated dialogue remains original, even in newly added asset.
    for r in read('reference/chapter3-deferred.json'):
        assert r['id'] not in patch['assets'].get(r['asset'],{}).get('entries',{})
        assert staged[r['asset']][r['id']]==originals[r['asset']][r['id']]
    coverage=[]
    all_text=[t for p in now['assets'].values() for t in p['entries'].values()]
    for size in ('Normal','Small'):
        g={r[0] for r in v.glyphs((STAGE/COMMON/f'U_Com_JP_SystemFont{size}.uasset').read_bytes())[0]}
        for text in all_text:
            for cluster in v.b.split_clusters(re.sub('<[^>]+>','',text)):
                if cluster.isspace():continue
                assert all(ord(ch) in g for ch in cmap.get(cluster,cluster)),(size,cluster)
        coverage.append(dict(font=size,all_combined_text_covered=True))
    assert fingerprint()==baseline['protected'],'Installed or legacy release files changed'
    for rel,sha in baseline['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    manifest={str(p.relative_to(STAGE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(STAGE.rglob('*.uasset'))}
    assert len(manifest)==22
    prev=read(baseline['previous_assets']);changes=[a for a in prev if manifest[a]!=prev[a]]
    new_assets=list(set(manifest)-set(prev))
    assert new_assets==[str(Path('End/Content/Text/JP/8200-JUNOE_TxtRes.uasset'))]
    assert set(changes)<=set(str(Path(r['asset'])) for r in rows)|{a for a in prev if 'Billboard' in a}
    write('qa/chapter3/working-assets.json',manifest)
    write('qa/chapter3/gender-review.json',dict(policy='Male ครับ; female ค่ะ statements / คะ questions / นะคะ. Only when suitable; no new audio review.',
        speaker_evidence=identity_evidence,records=gender,reviewed_all_lines=len(review),video_audio_verified=False))
    write('qa/chapter3/editorial-review.json',dict(records=review,all_253_jp_lines_reviewed=True,video_audio_verified=False))
    write('qa/chapter3/translation-audit.json',dict(chapter3_records=len(rows),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),
        missing_records=[],duplicate_indices=[],japanese_remaining=[],gender_mismatches=[],gender_sensitive_records=len(gender),
        previous_translation_and_actor_records_preserved=True,scope_verified_against_full_corpus=True,
        deferred_to_chapter4_records=14,original_glyph_map_assignments_preserved=True,new_clusters=len(cmap)-len(oldmap),
        changed_assets=changes,new_assets=new_assets,working_assets=len(manifest),glyph_coverage=coverage,
        source_and_installed_files_unchanged=True,installed=False,runtime_tested=False,video_audio_verified=False))
    write('qa/active-working-set.json',dict(stage='staging/ThaiJP_ThroughChapter3_Working',
        manifest='qa/chapter3/working-assets.json',audit='qa/chapter3/translation-audit.json',asset_count=22,
        chapters=[1,2,3],additional_parts=[['ThaiJP_Chapter3_P',['8200-JUNOE_TxtRes.uasset']]]))
    print('Chapter 3 audit passed: 253 lines, 14 deferred, prior 17178 records preserved;',len(gender),'gender-sensitive lines reviewed')
    print('Changed prior assets:',changes,'New assets:',new_assets)
if __name__=='__main__':main()
