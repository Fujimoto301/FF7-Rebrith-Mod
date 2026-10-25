"""Audit all source choice/UI families, plus independent question/short-option searches."""
import hashlib,re,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from choice_completion import family,JP,musical_notation


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    cfg=read('reference/choice-completion-build.json');baseline=read('qa/choice-completion/baseline.json')
    base=read(Path(baseline['snapshot'])/baseline['active']['combined_source']);now=read(cfg['source'])
    corpus=read('reference/rebirth-jp-corpus.json');rows=read('reference/choice-completion-source.json')
    stage=W/cfg['stage'];cmap=read(cfg['cluster_map']);reverse=str.maketrans({v:k for k,v in cmap.items()})
    assert cmap==read(Path(baseline['snapshot'])/baseline['active']['cluster_map'])
    # Verify the inventory against parsed original assets, not a previous selected-ID list.
    live_files={p.name for p in (W/'source/End/Content/Text/JP').glob('*_TxtRes.uasset') if p.stat().st_size>600}
    assert live_files==set(corpus)
    for asset,data in corpus.items():assert txtres.parse(str(W/'source/End/Content/Text/JP'/asset))==data,asset
    wanted={(f'End/Content/Text/JP/{a}',k) for a,d in corpus.items() for k,v in d.items() if v['Text'] and family(a,k)}
    assert wanted=={(r['asset'],r['id']) for r in rows}
    parsed={a:txtres.parse(str(stage/a)) for a in now['assets']}
    official={a:txtres.parse(str(W/'source'/a.replace('/JP/','/US/'))) for a in now['assets']}
    for a,p in base['assets'].items():
        for field in ('entries','actors'):assert all(now['assets'][a][field][k]==v for k,v in p[field].items())
    for a,p in now['assets'].items():
        for k,text in p['entries'].items():assert parsed[a][k]['Text'].translate(reverse)==text,k
    added=0;types=Counter();numeric=[]
    for r in rows:
        a,k=r['asset'],r['id'];jp=r['Japanese']['Text'];actual=parsed[a][k]
        assert r['English']==official[a].get(k,{}),k
        if r['mode']=='unchanged':
            assert not JP.search(jp) and actual==r['Japanese'],k
            continue
        t=now['assets'][a]['entries'][k]
        if jp.strip()=='<>':
            assert t==jp,k  # Original hidden-name / button-only sentinel, not missing text.
            continue
        assert (not JP.search(t) or musical_notation(k,t) and r['English']['Text']==t) and t.strip()!='<>',(k,t)
        assert re.findall('</?[^>]+>',jp)==re.findall('</?[^>]+>',t),k
        metadata=dict(r['Japanese'].get('MetaData',{}))
        if k in now['assets'][a]['actors']:metadata['ACTOR']=now['assets'][a]['actors'][k]
        assert actual.get('MetaData',{})==metadata,k
        types[r['family']]+=1
        if r['mode']=='existing':continue
        added+=1
        assert not re.search('ครับ|ค่ะ|นะค่ะ|แอริธ|เอเลน่า',t),(k,t)
        assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),(k,t)
        jn=re.findall(r'\d+',unicodedata.normalize('NFKC',re.sub('<[^>]+>','',jp)))
        tn=re.findall(r'\d+',re.sub('<[^>]+>','',t))
        if jn!=tn:
            if r['mode']=='official_English_name' or k.startswith(('$costume_change_','$menu_Colosseum_CourseTitle_')):reason='Official same-ID US title/name notation'
            elif not jn or jn==['3'] and tn==['3','2']:reason='Japanese kanji/kana number rendered as Arabic; roman rank/number-bearing official name preserved'
            elif k=='$Gambit_04_StageTips' and jn==['1'] and not tn:reason='1機ごと means per robot; Thai แต่ละตัว preserves per-unit condition'
            else:raise AssertionError((k,jp,t,jn,tn,'Unreviewed numeric difference'))
            numeric.append(dict(asset=a,id=k,jp=jp,thai=t,source_numbers=jn,target_numbers=tn,decision=reason))
    outside=[];question_count=0;short_count=0;key_candidates=[]
    short=r'はい|いいえ|休む|休まない|やめる|やめない|もう一度|引き受ける|引き受けない|挑戦する|挑戦しない|キャンセル|続ける|続けない|渡す|渡さない|使う|使わない|購入する|購入しない|始める|始めない|戻る|帰る|帰らない|降りる|乗る|乗らない|スキップする|リタイアする'
    for asset,data in corpus.items():
        entries=now['assets'].get('End/Content/Text/JP/'+asset,{}).get('entries',{})
        for k,v in data.items():
            t=v['Text']
            if not t or v.get('MetaData',{}).get('ACTOR'):continue
            if k not in entries and JP.search(t) and re.search(r'yes|(?:^|_)no(?:_|$)|confirm|comfirm|cancel|retry|(?:^|_)select(?:_|$)|retire|tutorial|(?:^|_)ask(?:_|$)',k,re.I):
                assert asset=='Resident_TxtRes.uasset' and k.startswith('$playdemo_'),(asset,k,'Untranslated choice-like key')
                key_candidates.append(dict(asset=asset,id=k,jp=t,reason='Demo-only UI, outside retail gameplay'))
            if re.fullmatch(short,re.sub('<[^>]+>','',t).strip()):
                short_count+=1;assert k in entries,(asset,k,'Missing short option')
            if not JP.search(t) or not re.search(r'[？?]|(?:ます|ない|する|よい)か[。\s]*$|選択|選ん|選べ|確認',t):continue
            question_count+=1
            if k in entries:continue
            if asset!='Resident_TxtRes.uasset':
                reviewed_voiced_questions={'$JUNOE_QST_06_0100_0100_00_mfk', '$CORLE_QST_05_0100_0400_00_mfk'}
                assert '_NPC_' in k or k.endswith(('_mma','_mfa','_crs','_rus')) or k in reviewed_voiced_questions,(asset,k,'Unclassified scene question')
                reason='Spoken ambient/later NPC or theatrical line; no system/choice ID'
            elif k.startswith('$playdemo_'):reason='Demo-only UI, outside retail gameplay'
            elif k.startswith(('$keyitem_','$menu_WorldReport_')):reason='Readable lore/reward letter/intel description, not a choice prompt or HUD objective'
            elif k.startswith(('$bt_','$menu_EnemyBook')):reason='Enemy ability label or test/assessment data, not a choice'
            else:raise AssertionError((asset,k,t,'Unclassified independent search hit'))
            outside.append(dict(asset=asset,id=k,jp=t,reason=reason))
    for k in ['$WorldSys_CampPoint_001','$WorldSys_CampPoint_002','$WorldSys_CampPoint_003','$WorldSys_CampPoint_Notify',
              '$ChocoboCapture_StoryMissionTitle_Hub1200','$ChocoboCapture_StoryText_Hub1200']:
        assert k in now['assets']['End/Content/Text/JP/Resident_TxtRes.uasset']['entries']
    # Independent namespace search: quest-like unselected hits must be individually classified.
    residual_quest=[]
    for k,v in corpus['Resident_TxtRes.uasset'].items():
        if (k in now['assets']['End/Content/Text/JP/Resident_TxtRes.uasset']['entries'] or
            not v['Text'] or not JP.search(v['Text']) or v.get('MetaData',{}).get('ACTOR') or
            not re.search('story|mission|quest',k,re.I)):continue
        assert k.startswith(('$bt_Flan_Emission','$menu_EnemyBookText_EN0008_04_','$menu_EnemyBookTipsText_EN0008_04_')),k
        residual_quest.append(dict(id=k,jp=v['Text'],reason='False namespace match inside enemy Quest or UniqueStandard IDs; combat data, not quest HUD'))
    from audit_gender_through_chapter8 import PARTICLES
    oldgender={r['id']:r for r in read('qa/chapter9/gender/records.json')['records']}
    particles=Counter();particle_rows=0
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            counts={name:len(pattern.findall(re.sub('<[^>]+>','',t))) for name,pattern in PARTICLES.items()}
            if not sum(counts.values()):continue
            if k=='$C1910_MAIN_7150_0500_00_mma' and t=='คะ…ครับ!':
                counts['คะ']=0  # Preserved reviewed stutter, not a feminine sentence ending.
            assert k in oldgender and oldgender[k]['thai']==t and oldgender[k]['counts']==counts,(k,'New/unreviewed gender ending')
            particles.update(counts);particle_rows+=1
    assert particle_rows==len(oldgender)==952 and sum(particles.values())==976
    # Inverse pass over every remaining non-voiced Resident entry, not a list of
    # keywords. Previously missed quest counters and Gambit namespaces are caught here.
    residual=[]
    for k,v in corpus['Resident_TxtRes.uasset'].items():
        if k in now['assets']['End/Content/Text/JP/Resident_TxtRes.uasset']['entries'] or not JP.search(v['Text']) or v.get('MetaData',{}).get('ACTOR'):continue
        if k.startswith(('$bt_','$EN9000_10_')):reason='Enemy combat action labels, outside current choice/quest/UI-category repair'
        elif k.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')):reason='Enemy biography/assessment prose; enemy names and index navigation are already covered separately'
        elif k.startswith(('$playdemo_','$demo_','$menu_TrialVersion_','$menu_load_trial_')):reason='Demo-only data'
        elif k.startswith(('$TEMPL_ITEM_','$TEMPL_MAGIC_')):reason='Development shop templates'
        elif k in {f'$MOGLE_QST_01_1800_0{i}00_00_lmg' for i in [4,5,6,7]}:reason='Moogle spoken reactions without ACTOR; not choice UI'
        else:raise AssertionError((k,v['Text'],'Unclassified remaining non-voiced Resident text'))
        residual.append(dict(id=k,jp=v['Text'],reason=reason))
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))}
    assert len(manifest)==27
    old_assets=read(Path(baseline['snapshot'])/baseline['active']['manifest'])
    assert all(manifest[p]==h for p,h in old_assets.items() if 'Billboard' in p)
    recheck_path=W/'qa/choice-completion/recheck/current.json'
    protection=read(recheck_path) if recheck_path.exists() else baseline
    assert fingerprint()==protection['protected']
    for p,h in baseline['source_hashes'].items():assert digest(W/p)==h,p
    total=sum(len(p['entries']) for p in now['assets'].values());source_hash=digest(W/cfg['source'])
    audit=dict(total_combined_text_records=total,added_UI_records=added,previous32859_text_and_ACTOR_preserved=True,
        inventory_records=len(rows),original_corpus_records=sum(len(d) for d in corpus.values()),original_text_assets=len(corpus),
        families=dict(types),independent_question_candidates=question_count,independent_short_option_records=short_count,
        independent_choice_key_dispositions=len(key_candidates),
        independent_nonchoice_dispositions=len(outside),working_assets=27,glyph_clusters=len(cmap),all16_font_assets_unchanged=True,
        numeric_differences_reviewed=len(numeric),source_sha256=source_hash,missing=[],tag_mismatches=[],japanese_remaining=[],
        prior_gender_particle_records_preserved=particle_rows,gender_particle_occurrences=dict(particles),new_gender_endings=0,
        remaining_nonvoiced_Resident_dispositions=len(residual),
        source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False)
    write('qa/choice-completion/translation-audit.json',audit);write('qa/choice-completion/working-assets.json',manifest)
    write('qa/choice-completion/independent-dispositions.json',outside)
    write('qa/choice-completion/independent-choice-key-dispositions.json',key_candidates)
    write('qa/choice-completion/quest-namespace-dispositions.json',residual_quest)
    write('qa/choice-completion/remaining-Resident-dispositions.json',residual)
    current=W/'qa/choice-completion/recheck/current.json'
    if current.exists():
        before=read(current);snap=Path(before['snapshot']);previous=read(snap/'translations/working-choice-completion-th.json')
        changes=[];newids=[]
        for a,p in now['assets'].items():
            for k,t in p['entries'].items():
                old=previous['assets'].get(a,{}).get('entries',{})
                if k not in old:newids.append(dict(asset=a,id=k,thai=t))
                elif old[k]!=t:changes.append(dict(asset=a,id=k,before=old[k],after=t))
        assert not changes,'Prior release text must be preserved in this additive recheck'
        assert all(p['actors']==now['assets'][a]['actors'] for a,p in previous['assets'].items())
        assert fingerprint()==before['protected']
        write('qa/choice-completion/recheck/review.json',dict(source_sha256=source_hash,
            previous_records=before['base_records'],previous33902_text_and_ACTOR_preserved=True,
            added_records=len(newids),corrected_records=0,added=newids,changes=changes,
            inventory_records=len(rows),new_manual_templates=len(read('reference/choice-completion-templates.json'))-before['base_templates'],
            all16_fonts_and711_assignments_unchanged=True,remaining_nonvoiced_Resident_dispositions=len(residual),
            new_gender_particles=0,in_game_tested=False))
    write('qa/choice-completion/numeric-review.json',dict(reviewed=True,source_sha256=source_hash,rows=numeric))
    ctx=dict(baseline['active']);ctx.update(stage=cfg['stage'],manifest='qa/choice-completion/working-assets.json',
        audit='qa/choice-completion/translation-audit.json',asset_count=27,combined_source=cfg['source'],cluster_map=cfg['cluster_map'],
        choice_completion=True,shared_file_note='All7 latest ZIPs required. Common also owns COSME choice-only UI until a later scene chapter assigns its whole asset; no later spoken dialogue translated.')
    write('qa/active-working-set.json',ctx)
    print(audit)


if __name__=='__main__':main()
