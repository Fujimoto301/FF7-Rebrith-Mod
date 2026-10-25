"""Audit complete name coverage, official names and unchanged previous content."""
import collections,hashlib,re
from create_ui_completion_scope import W,R,read,write
from assemble_ui_completion import fingerprint,protected_snapshot
from assemble_enemy_names import family
import txtres

def main():
    jp=txtres.parse(str(W/'source'/R));us_path=W/'source/End/Content/Text/US/Resident_TxtRes.uasset'
    us=txtres.parse(str(us_path));scope=read('reference/enemy-name-scope.json')
    expected={k:us[k]['Text'] for k,v in jp.items() if v['Text'] and family(k)}
    names=read('translations/enemy-names-th.json')['assets'][R]['entries']
    assert expected==names and set(names)==set(scope['selected_ids'])
    assert hashlib.sha256((W/'source'/R).read_bytes()).hexdigest()==scope['jp_source_sha256']
    assert hashlib.sha256(us_path.read_bytes()).hexdigest()==scope['us_source_sha256']
    baseline=read('qa/enemy-names/baseline.json');old=read(baseline['previous_combined_source'])
    now=read('translations/working-ui-completion-th.json')
    assert set(now['assets'])==set(old['assets'])
    new_entries=now['assets'][R]['entries'];old_entries=old['assets'][R]['entries']
    for asset,p in old['assets'].items():
        assert now['assets'][asset]['actors']==p['actors'],(asset,'Actor labels changed')
        for k,t in p['entries'].items():assert now['assets'][asset]['entries'][k]==t,(asset,k,'Prior translation changed')
        if asset!=R:assert now['assets'][asset]==p,asset
    added=set(new_entries)-set(old_entries)
    assert added==set(names)-set(old_entries)
    assert not {k for k in names if k.startswith('$menu_EnemyBookText_')}
    staged=txtres.parse(str(W/'staging/ThaiJP_UICompletion_Working'/R))
    cmap=read('reference/ui-completion-cluster-map.json');reverse=str.maketrans({v:k for k,v in cmap.items()})
    for k,en in names.items():
        assert staged[k]['Text'].translate(reverse)==en,k
        assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',en),k
        assert staged[k].get('MetaData',{})==jp[k].get('MetaData',{}),k
        assert re.findall('<[^>]+>',staged[k]['Text'])==re.findall('<[^>]+>',jp[k]['Text']),k
    assert all(staged[k]==jp[k] for k in jp if k.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_'))),'Enemy lore/tips changed'
    sample={'$en_Formula_SonicSpeedEnd2':'Velociwing',
        '$en_MateriaKeeper_Standard':'Materia Guardian','$en_MidgarZolom_Standard':'Midgardsormr',
        '$en_HellRiderVR2_StandardEnd2':'Hell Rider II','$en_Sephiroth_VRHard':'Virtual Sephiroth',
        '$en_SecuritySoldier_Standard':'Security Officer','$en_ShieldSoldier_Flame':'Flametrooper',
        '$en_Cactuar_Standard_Gold_MiniGame':'Gold Cactuar: 100 pt.',
        '$GE_Enemy_01_Name':'Flan General','$MateriaKeeper_FrontLeg_L':'Left Foreleg'}
    assert all(names[k]==t for k,t in sample.items())
    # Names feed the source object reference; preserve its case/format and all
    # original battle quantities in the already translated notification template.
    assert new_entries['$sys_enemy_down']=='กำจัด <object=0> แล้ว'
    example=new_entries['$sys_enemy_down'].replace('<object=0>',names['$en_Formula_SonicSpeedEnd2'])
    assert example=='กำจัด Velociwing แล้ว'
    former=read(baseline['previous_assets']);current=read('qa/ui-completion/working-assets.json')
    assert set(former)==set(current)
    changed=[a for a in current if current[a]!=former[a]]
    aligned_fonts={a for a in current if 'Menu\\Billboard\\Common\\U_Com_JP_SystemFont' in a and '-' not in __import__('pathlib').Path(a).name} if (W/'reference/native-baseline-policy.json').exists() else set()
    assert set(changed)=={R.replace('/','\\')}|aligned_fonts,changed
    assert fingerprint()==protected_snapshot()
    report=dict(total_name_records=len(names),categories=dict(collections.Counter(family(k) for k in names)),
        unique_official_names=len(set(names.values())),new_records=len(added),
        previously_english_records=len(names)-len(added),all_selected_ids_match_official_us=True,
        missing_enemy_name_ids=[],japanese_remaining_in_selected_names=[],
        prior_translations_and_dialogue_preserved=True,enemy_lore_and_tips_unchanged=True,
        actor_metadata_unchanged=True,scene_and_texture_assets_unchanged=True,
        font_origins_aligned_to_native_ascii=bool(aligned_fonts),
        changed_assets=changed,notification_example=example,source_and_installed_files_unchanged=True,
        sample_names=sample,runtime_tested=False,installed=False)
    write('qa/enemy-names/audit.json',report)
    print('Enemy name audit passed:',len(names),'official names;',len(added),'new records; earlier content preserved')

if __name__=='__main__':main()
