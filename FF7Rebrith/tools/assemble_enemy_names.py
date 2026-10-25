"""Use official same-ID US names for all enemy and reviewed target labels."""
import collections,hashlib,json,re,shutil,uuid
from pathlib import Path
from create_ui_completion_scope import W,R,read,write
from assemble_ui_completion import fingerprint
import txtres

PART_PREFIXES=('$Alexander_Boss_','$Foot_','$HG_','$JenovaBirth_','$LostNumber_',
    '$MateriaKeeper_','$MateriaKeeperBtmLeg_','$MidgarZolom_','$MythrilGolem_',
    '$PalmerMech_','$ScrMagArmorCustom_','$Titan_Boss_','$partsName_')
PART_IDS={
    '$Armor','$Battery_L','$Battery_R',
    '$bt_Aps_Tail','$bt_BizarroSephiroth_Core','$bt_BizarroSephiroth_Head',
    '$bt_BizarroSephiroth_LeftWing','$bt_BizarroSephiroth_RightWing',
    '$bt_BossSephiroth_PartsSword','$bt_BossSephiroth_PartsWing',
    '$bt_BottomSwell_TailEnd','$bt_BottomSwell_TailMark',
    '$bt_ChatchMech_LeftParts','$bt_ChatchMech_RightParts',
    '$bt_DeepGroundCommander_Core','$bt_DeepGroundCommander_Tentacle',
    '$bt_Jenova1_Hand_L','$bt_Jenova1_Hand_R','$bt_Jenova1_Tail',
    '$bt_Leviathan_Chest','$bt_Leviathan_Tail',
    '$bt_NeoBahamut_LeftWing','$bt_NeoBahamut_RightWing',
    '$bt_RedDragon_Chest','$bt_RedDragon_Head','$bt_RedDragon_LeftWing','$bt_RedDragon_RightWing',
    '$bt_SampleH05_LeftArm',
}

def family(k):
    if k.startswith('$en_'):return 'enemy_names'
    if re.fullmatch(r'\$GE_Enemy_\d+_Name',k):return 'gambit_minigame_enemy_names'
    if k.startswith(PART_PREFIXES) or k in PART_IDS:return 'target_part_names'

def main():
    qa=W/'qa/enemy-names';qa.mkdir(parents=True,exist_ok=True)
    if not (qa/'baseline.json').exists():
        run=qa/'revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
        for rel in ('translations/working-ui-completion-th.json','translations/ui-completion-th.json',
                    'qa/ui-completion/working-assets.json','qa/final-parts/latest.json',
                    'qa/ui-completion/active-revision.json'):
            dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
        protected=run/'protected-files-before.json';write(str(protected),fingerprint())
        baseline=dict(previous_combined_source=str(run/'translations/working-ui-completion-th.json'),
            previous_assets=str(run/'qa/ui-completion/working-assets.json'),
            protected_manifest=str(protected),backup=str(run))
        write('qa/enemy-names/baseline.json',baseline)
        write('qa/ui-completion/active-revision.json',dict(**baseline,
            reason='User now authorizes all enemy names in official English; previous deferral superseded.'))
    jp=txtres.parse(str(W/'source'/R));us_path=W/'source/End/Content/Text/US/Resident_TxtRes.uasset'
    us=txtres.parse(str(us_path));rows=[];entries={}
    corpus=read('reference/rebirth-jp-corpus.json')
    assert not [(a,k) for a,d in corpus.items() if a!='Resident_TxtRes.uasset' for k in d if k.startswith('$en_')]
    for k,v in jp.items():
        kind=family(k)
        if not kind or not v['Text']:continue
        en=us.get(k,{}).get('Text','')
        assert en.strip() and not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',en),(k,'Missing official English name')
        assert not v.get('MetaData',{}).get('ACTOR'),(k,'Dialogue selected')
        assert re.findall('<[^>]+>',en)==re.findall('<[^>]+>',v['Text']),k
        entries[k]=en;rows.append(dict(id=k,asset=R,category=kind,jp=v['Text'],en=en))
    assert PART_IDS<=entries.keys()
    assert len([r for r in rows if r['category']=='enemy_names'])==312
    write('reference/enemy-name-source.json',rows)
    write('reference/enemy-name-scope.json',dict(asset=R,selected_ids=list(entries),
        families=dict(collections.Counter(r['category'] for r in rows)),part_prefixes=PART_PREFIXES,
        explicit_part_ids=sorted(PART_IDS),jp_source_sha256=hashlib.sha256((W/'source'/R).read_bytes()).hexdigest(),
        us_source_sha256=hashlib.sha256(us_path.read_bytes()).hexdigest(),
        all_game_enemy_names_english=True,description_and_attack_names_not_added=True))
    write('translations/enemy-names-th.json',dict(scope='All-game official English enemy names and target-part labels; no spoken dialogue changes',
        assets={R:dict(entries=entries,actors={})}))
    write('qa/enemy-names/assembly.json',dict(records=len(entries),unique_official_names=len(set(entries.values())),
        categories=dict(collections.Counter(r['category'] for r in rows)),
        same_id_official_us_names=True,source_tags_preserved=True,runtime_tested=False,installed=False))
    print('Assembled',len(entries),'official English enemy/target names;',collections.Counter(r['category'] for r in rows))

if __name__=='__main__':main()
