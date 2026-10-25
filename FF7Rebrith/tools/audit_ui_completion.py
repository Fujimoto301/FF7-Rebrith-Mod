"""Independently audit category coverage, policy, source integrity and glyphs."""
import collections, hashlib, json, re, string
from create_ui_completion_scope import W,R,read,write,category
from assemble_ui_completion import fingerprint,protected_snapshot
import verify_chapter1 as v
import txtres

def main():
    original=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    base=read('translations/working-inventory-th.json')
    combined=read('translations/working-ui-completion-th.json')
    entries=combined['assets'][R]['entries']
    rows=read('reference/ui-completion-source.json');scope=read('reference/ui-completion-scope.json')
    new=read('translations/ui-completion-th.json')['assets'][R]['entries']
    prefixes=('$mainmenu_','$menu_Libra_','$menu_field_','$menu_FastTravel_','$menu_WM_',
        '$menu_WeaponUpgrade_','$menu_questboard_','$menu_itemcraft_','$menu_pcrein_',
        '$menu_chadleyshop_','$menu_shop_','$menu_partyname_','$menu_navimap_','$menu_mapicon_','$menu_map_',
        '$Piano_','$minigame_piano_','$menu_commandmenu_','$sys_')
    wanted={k for k,item in original.items() if item['Text'] and not item.get('MetaData',{}).get('ACTOR')
            and (category(k) or k.startswith(prefixes) or k=='$map_midgr')}
    assert not wanted-entries.keys(),('Untranslated category members',sorted(wanted-entries.keys()))
    assert set(new)==set(scope['selected_ids'])=={r['id'] for r in rows}
    assert hashlib.sha256((W/'source'/R).read_bytes()).hexdigest()==scope['source_sha256']
    for a,patch in base['assets'].items():
        assert combined['assets'][a]['actors']==patch['actors']
        assert all(combined['assets'][a]['entries'][k]==t for k,t in patch['entries'].items())
    assert set(combined['assets'])==set(base['assets'])
    assert not set(new)&set(base['assets'][R]['entries'])
    us=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    names=[];chapters=[];temporal=[]
    for row in rows:
        k=row['id'];t=new[k]
        assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]|\{n\d+\}',t.replace('・','')),k
        assert sorted(re.findall('<[^>]+>',t))==sorted(re.findall('<[^>]+>',row['jp'])),k
        if row['mode']=='english':
            expected=us[k]['Text'].replace('<i>','').replace('</i>','')
            assert t==expected,(k,'Official English name changed')
            names.append(k)
        if row['category']=='chapter_labels':
            if k.startswith('$chapter_number_'):
                assert t.lower()==us[k]['Text'].lower(),(k,'Chapter number')
            else:
                assert t==us[k]['Text'],(k,'Chapter title')
            chapters.append(dict(id=k,text=t))
        if re.fullmatch(r'[0-9０-９]+年前|現在|翌日|翌朝|[0-9０-９]+時間後',row['jp']):
            assert re.search(r'[\u0e01-\u0e5b]',t),(k,'Temporal caption not Thai')
            temporal.append(dict(id=k,text=t))
    assert new['$chapter_title_0001']=='Fall of a Hero'
    assert new['$chapter_title_0002']=='A New Journey Begins'
    assert new['$lvl_time_5yearsago']=='5 ปีก่อน' and new['$lvl_time_now']=='ปัจจุบัน'
    assert new['$area2360_4yearsago']=='4 ปีก่อน'
    for k,t in scope.get('english_hud_actions',{}).items():assert new[k]==t,(k,'English HUD action')
    assert entries['$menu_commandmenu_0000_0000']=='COMMAND'
    assert not any(k.startswith(('$en_','$enemy_','$menu_EnemyBookText_')) for k in new)
    cmap=read('reference/ui-completion-cluster-map.json');coverage=[]
    for name in ('Normal','Small'):
        p=W/f'staging/ThaiJP_UICompletion_Working/End/Content/Menu/Billboard/Common/U_Com_JP_SystemFont{name}.uasset'
        glyphs={g[0] for g in v.glyphs(p.read_bytes())[0]}
        missing=collections.defaultdict(list)
        for k,t in entries.items():
            for cluster in v.b.split_clusters(re.sub('<[^>]+>','',t)):
                if cluster.isspace():continue
                code=cmap.get(cluster,cluster)
                for c in code:
                    if ord(c) not in glyphs:missing[c].append(k)
        assert not missing,(name,dict(missing))
        coverage.append(dict(font=name,all_combined_translation_characters_covered=True))
    assert fingerprint()==protected_snapshot()
    stage=W/'staging/ThaiJP_UICompletion_Working'
    assets={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))}
    assert len(assets)==21
    write('qa/ui-completion/working-assets.json',assets)
    write('qa/ui-completion/final-audit.json',dict(new_ui_records=len(new),
        total_combined_text_records=sum(len(a['entries']) for a in combined['assets'].values()),
        required_category_records=len(wanted),untranslated_required_records=[],
        official_english_name_records=len(names),chapter_titles=chapters,temporal_captions=temporal,
        source_resident_hash_unchanged=True,prior_dialogue_and_inventory_preserved=True,
        enemy_name_records=combined.get('enemy_name_records',0),
        enemy_labels_report='qa/enemy-names/audit.json' if combined.get('enemy_name_records') else None,
        spoken_dialogue_added=0,glyph_coverage=coverage,
        working_assets=len(assets),dist_and_installed_hashes_unchanged=True,
        runtime_tested=False,installed=False))
    print('Audit passed:',len(new),'new UI records;',len(wanted),'category members covered; 21 working assets; release unchanged')

if __name__=='__main__':main()
