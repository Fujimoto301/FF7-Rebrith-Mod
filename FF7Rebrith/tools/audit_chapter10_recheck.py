"""Independent cross-file completeness and explicit residual dispositions."""
import re
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write
from audit_chapter10 import digest
from assemble_ui_completion import fingerprint
from chapter10_recheck_scope import extra
from chapter4_door_fix import matches as door_matches,verify_protected
Q='qa/chapter10/recheck/'

def disposition(k):
    if k.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')):return 'Enemy index biographies/tactics remain a separate untranslated category; enemy/action NAME labels already verified. Not Chapter10 dialogue or choices.'
    if k.startswith(('$menu_TrialVersion_','$menu_load_trial_','$playdemo_','$demo_')):return 'Inactive trial/demo storefront/interface; outside retail Chapter10 gameplay.'
    if k.startswith('$NIBLT_NPC_20_'):return 'Chapter11 Nibel village NPC family; not yet visited.'
    if k.startswith(('$CARDG_QST_05_','$CARDG_QST_06_','$CARDG_QST_07_','$CARDG_QST_16_')):return 'Later Queens Blood: Lidrehl requires Gold Saucer return, Vincent/Nibel rank, or Shadowblood finale. Current rank notifications through Marquis included.'
    if k.startswith(('$CHADL_QST_03_','$COMMN_BOS_50_')):return 'Corel protorelic trials3/4 or final Gilgamesh island after Chapter12; earlier-region dimension closure scenes now included.'
    if k.startswith('$CHADL_QST_06_'):return 'Nibel protorelic new Chapter11 content.'
    if k.startswith(('$PHOTO_QST_07_','$PHOTO_QST_00_')):return 'Nibel photography or ranks requiring Nibel/all later photography locations; Cosmo rank600 and current-region returns included.'
    if k.startswith('$PIANO_QST_01_'):return 'Final six-sheet piano completion and Dorian backstory; sixth sheet only obtained after Nibel progression.'
    if k.startswith('$C3210_'):return 'Tiny Bronco sailing services Chapter12 after the Chapter11 aircraft sequence.'
    if k.startswith('$C3310_'):return 'Chapter13 Tiny Bronco/temple-bound main story.'
    if k.startswith('$WORLD_QST_01_'):return 'Pirate King treasure and open-ocean sailing after Chapter12 Tiny Bronco conversion.'
    if k.startswith('$WORLD_MGV_01_0700_'):return 'Nibel fiend intel; Cosmo0600 complete.'
    if k.startswith('$WORLD_CDV_02_0700_'):return 'Nibel world/divine/fiend/protorelic intel.'
    if k.startswith('$WORLD_CDV_02_0100_'):
        n=int(k.split('_')[4]);assert n in [5800,5900] or 6200<=n<=7400,k
        return 'Nibel sea-chocobo movement help' if n<6200 else 'Gilgamesh island guidance unlocked after later protorelics Chapter12.'
    if k.startswith('$WORLD_CDV_01_0100_'):
        n=int(k.split('_')[4]);assert 16800<=n<=18900 or 21500<=n<=21800 or 26800<=n<=27300,k
        return 'Chapter12 Gold Cup victory report' if n>=27100 else 'Nibel village/chocobo/completion or Odin simulator content Chapter11.'
    if k.startswith('$WORLD_CDV_01_0300_'):return 'Odin victory or all combat simulator courses completed; requires Nibel/later progression.'
    if k.startswith('$WORLD_CDV_01_0400_'):return 'Ark Library final all-world-intel completion scene; requires Nibel and later protorelics.'
    if k.startswith('$WORLD_CDV_01_0500_'):
        assert 2900<=int(k.split('_')[4])<=3100,k
        return 'Nibel-specific ordinary Chadley return lines; all other visited-region return states included.'
    if k.startswith('$WORLD_CDV_03_0100_'):return 'Queens Blood Sovereign/Vincent/Shadowblood ranks after Nibel/later Gold Saucer return; through-Marquis messages included.'
    return None

def main():
    continued=(W/'qa/chapter10/continue-review/current.json').exists()
    if continued:
        from chapter10_continue_review import audit as audit_continuation
        audit_continuation()
    before=read(Q+'current.json');snap=Path(before['snapshot']);ctx=read('qa/active-working-set.json');old=read(snap/before['active']['combined_source']);now=read(ctx['combined_source']);c=read('reference/rebirth-jp-corpus.json');added=[];changed=[]
    for a,p in old['assets'].items():
        assert now['assets'][a]['actors'].items()>=p['actors'].items(),(a,'existing ACTOR changed')
        for k,t in p['entries'].items():
            assert k in now['assets'][a]['entries'],(a,k,'dropped');n=now['assets'][a]['entries'][k]
            if n!=t:changed.append(dict(asset=a,id=k,before=t,after=n,jp=c[Path(a).name][k]['Text']))
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            if k not in old['assets'].get(a,{}).get('entries',{}):added.append((a,k))
    ext=read('reference/chapter10-recheck-source.json');assert set(added)=={(r['asset'],r['id']) for r in ext}
    expected={(f'End/Content/Text/JP/{a}',k) for a,d in c.items() for k,v in d.items() if v['Text'] and extra(a,k) and k not in old['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})}
    assert expected==set(added) and len(added)==144
    original=read('reference/chapter10-source.json');original_keys={(r['asset'],r['id']) for r in original}
    assert all((r['asset'],r['id']) in original_keys or door_matches(r['asset'],r['id'],r['before'],r['after']) for r in changed),'Unapproved pre-Ch10 translation changed'
    fixes={174,304,634,818,900,916,1241,1268};lookup={(r['asset'],r['id']):r['template'] for r in original}
    if continued:
        from chapter10_continue_review import FIXES
        fixes |= {int(k) for k in FIXES if k.isdigit()}
    for r in changed:
        if door_matches(r['asset'],r['id'],r['before'],r['after']):
            r['decision']='Reviewed per-ID context correction; exact old/new/source/context recorded in reference/context-recheck-overrides.json or earlier Ch4 door/choice review.'
            continue
        template=lookup[r['asset'],r['id']]
        if template in fixes:
            r['decision']=FIXES[str(template)][1] if continued and str(template) in FIXES else 'Explicit contextual correction: Marche ingredient, emotional/landscape wording, interrupted sentence or resolve nuance.'
        else:
            normalized=r['before'].replace('ศาสตร์แห่งชีวิตดวงดาว','ศาสตร์ชีวิตดวงดาว').replace('พิธีส่งคืนสู่ดวงดาว','พิธีส่งวิญญาณสู่ดวงดาว').replace('วันส่งคืนสู่ดวงดาว','วันส่งวิญญาณสู่ดวงดาว').replace('คืนส่งคืนสู่ดวงดาว','คืนส่งวิญญาณสู่ดวงดาว')
            assert normalized==r['after'],r['id'];r['decision']='Consistent planetology/ceremony wording within Chapter10.'
    # Content-driven, corpus-wide chapter IDs also catch a scene in another asset.
    broad=[]
    for a,d in c.items():
        for k,v in d.items():
            if v['Text'] and k.startswith(('$C2910_','$C3010_')):
                assert k in now['assets']['End/Content/Text/JP/'+a]['entries'],(a,k,'cross-file chapter omission')
                broad.append(dict(asset=a,id=k))
    resident=[];d=c['Resident_TxtRes.uasset'];e=now['assets']['End/Content/Text/JP/Resident_TxtRes.uasset']['entries']
    for k,v in d.items():
        if v['Text'] and re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']) and k not in e:
            why=disposition(k);assert why,(k,v['Text'],'Unclassified shared residual');resident.append(dict(id=k,jp=v['Text'],reason=why))
    cm=read(ctx['cluster_map']);prior=read(snap/before['active']['cluster_map']);assert all(cm[k]==v for k,v in prior.items())
    verify_protected(before['protected'])
    shortened=read(Q+'terminology-candidates.json');assert len(shortened)==4 and all(r['term']=='魔晄' and 'เตาปฏิกรณ์' in r['thai'] for r in shortened)
    for r in shortened:r['decision']='魔晄炉 shortened naturally to reactor in an established mako-reactor context; no alternate Mako spelling.'
    write(Q+'terminology-decisions.json',shortened);write(Q+'Resident-residual-dispositions.json',resident)
    report=dict(source_sha256=digest(W/ctx['combined_source']),source_records_scanned=sum(len(p['entries']) for p in now['assets'].values()),previous40547_records_retained=True,previous_ACTOR_preserved=True,added_records=len(added),changed_records=len(changed),changes=changed,new_shared_families=dict(Counter(r['family'] for r in ext)),cross_file_main_chapter_records=len(broad),registered_choices=read('qa/chapter10/translation-audit.json')['registered_choice_records'],remaining_Resident_records=len(resident),remaining_Resident_dispositions=dict(Counter(r['reason'] for r in resident)),new_clusters=[k for k in cm if k not in prior],all716_assignments_preserved=True,all_original_indices_preserved=True,source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False,scope='Chapter10 and adjacent earlier/shared closures/ordinary NPC returns; no new Chapter11 main story')
    write(Q+'review.json',report);print('Recheck:',len(added),'added;',len(changed),'corrected;',len(broad),'cross-file Ch10 main records;',len(resident),'remaining Resident records individually classified')
if __name__=='__main__':main()
