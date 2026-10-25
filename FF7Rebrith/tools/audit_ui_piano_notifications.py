"""Verify the user's seven screenshots against the current serialized assets."""
import hashlib,json,re
from create_ui_completion_scope import W,R,read,write
import txtres
from preview_ui_completion import main as preview

def main():
    extension=read('qa/ui-completion/piano-notification-scope.json')
    snapshot=__import__('pathlib').Path(extension['revision_backup'])
    previous=read(str(snapshot/'translations/working-ui-completion-th.json'));now=read('translations/working-ui-completion-th.json')
    old=previous['assets'][R]['entries'];current=now['assets'][R]['entries']
    added=set(current)-set(old);changed={k for k in old if old[k]!=current[k]}
    enemy_path=W/'translations/enemy-names-th.json'
    enemy=read(str(enemy_path))['assets'][R]['entries'] if enemy_path.exists() else {}
    assert added==set(extension['added_ids'])|(set(enemy)-set(old))
    added_piano=set(extension['added_ids']);assert len(added_piano)==421
    assert changed=={'$level_sys_show_parkour_input'}
    for a,patch in previous['assets'].items():
        assert now['assets'][a]['actors']==patch['actors']
        if a!=R:assert now['assets'][a]==patch
    assert current['$level_sys_show_parkour_input']=='Terrain Action'
    assert current['$menu_commandmenu_0000_0000']=='COMMAND'
    wanted={'$menu_commandmenu_0002_0002':'ใช้ไอเทม',
        '$sys_item_drop':'ได้รับ <object=0>','$sys_item_drop_multiple':'ได้รับ <object=0> ×<count>',
        '$sys_get_exp_ap':'ได้รับ <count=0> EXP และ <count=1> AP',
        '$sys_get_gil':'ได้รับ <count=0> กิล','$sys_enemy_down':'กำจัด <object=0> แล้ว',
        '$minigame_piano_pause_message':'ต้องการหยุดเล่นเปียโนหรือไม่?',
        '$minigame_piano_pause_yes':'หยุดเล่น',
        '$Piano_ModeChange_To_Monotone_Text':'โหมดโน้ตเดี่ยว'}
    for k,t in wanted.items():assert current[k]==t,(k,current[k])
    src=txtres.parse(str(W/'source'/R));staged=txtres.parse(str(W/'staging/ThaiJP_UICompletion_Working'/R))
    cmap=read('reference/ui-completion-cluster-map.json');reverse=str.maketrans({v:k for k,v in cmap.items()})
    for k in added|changed:
        t=staged[k]['Text'].translate(reverse);assert t==current[k]
        assert sorted(re.findall('<[^>]+>',staged[k]['Text']))==sorted(re.findall('<[^>]+>',src[k]['Text']))
    enemy_keys=[k for k in src if k.startswith(('$en_','$enemy_','$menu_EnemyBookText_'))]
    for k in enemy_keys:
        assert staged[k]['Text'].translate(reverse)==enemy.get(k,old.get(k,src[k]['Text'])),(k,'Enemy name regression')
        assert staged[k].get('MetaData',{})==src[k].get('MetaData',{}),k
    former=read(str(snapshot/'qa/ui-completion/working-assets.json'))
    # Later native-baseline correction may alter font origins only; scene and
    # texture assets must still match the original piano revision snapshot.
    latest=read('qa/ui-completion/working-assets.json')
    changed_assets=[a for a in latest if latest[a]!=former[a]]
    aligned_fonts={a for a in latest if 'Menu\\Billboard\\Common\\U_Com_JP_SystemFont' in a and '-' not in __import__('pathlib').Path(a).name} if (W/'reference/native-baseline-policy.json').exists() else set()
    assert set(changed_assets)=={R.replace('/','\\')}|aligned_fonts,changed_assets
    write('qa/ui-completion/piano-notification-review.json',dict(added_ui_records=len(added_piano),
        changed_existing_records=sorted(changed),affected_assets=changed_assets,
        screenshot_messages=wanted,english_hud_actions=extension['english_hud_actions'],
        enemy_names_checked_against_current_policy=len(enemy_keys),previous_dialogue_and_inventory_preserved=True,
        scene_and_texture_assets_unchanged=True,font_origins_aligned_to_native_ascii=bool(aligned_fonts),
        raw_source_tags_preserved=True,runtime_tested=False))
    preview([
        ('Field HUD (English)',['$level_sys_show_parkour_input','$menu_commandmenu_0000_0000']),
        ('Command help (Thai)',['$menu_commandmenu_0002_0001','$menu_commandmenu_0002_0002']),
        ('Piano control modes',['$Piano_ModeChange_To_Monotone_Text','$Piano_ModeChange_To_Minor_Text','$minigame_piano_sharp']),
        ('Piano key / octave',['$Piano_Chord_PageTitle_Text','$Piano_Monotone_PageTitle_Text','$Piano_Chord_PageReset_Text']),
        ('Piano pause dialog',['$minigame_piano_pause_message','$minigame_piano_pause_yes','$minigame_piano_pause_no']),
        ('Piano camera / sheet',['$minigame_piano_CameraChange','$minigame_piano_music_select_title','$minigame_piano_end']),
        ('Piano note notation',['$minigame_piano_C','$minigame_piano_F_sharp','$minigame_piano_A_flat']),
        ('Pickup / battle static text (parameters omitted)',['$sys_item_drop','$sys_get_exp_ap','$sys_get_gil'])
    ],'piano-notification-proof')
    print('Verified screenshot fixes: 421 added records, one English HUD correction; prior translations preserved')

if __name__=='__main__':main()
