"""Whole Ch8 activity UI families and shared Queen's Blood NPCs, frozen separately."""
import re
from collections import defaultdict
from prepare_chapter8 import W,read,write,txtres
R='End/Content/Text/JP/Resident_TxtRes.uasset'
def family(k):
    if k.startswith('$costume_change_0006_'):return 'Cait_costume_UI'
    if k.startswith('$4000_MenuLog_'):return 'Midgar_shared_objective_UI'
    if k.startswith('$minigame_2650_ChocoboRace_'):return 'Chocobo_race_whole_UI'
    if k.startswith(('$CardChallenge_GS_','$card_riddle_GS_')):return 'Saucer_card_challenge_whole_UI'
    if k.startswith(('$level_GOLDS_','$level_UNDRS_','$level2350_pointwarp_')):return 'Gold_Saucer_Prison_field_and_choices'
    if k.startswith(('$minigame_3Dbattler_','$minigame_bike_','$menu_bike_','$minigame_ShootingCoaster_','$minigame_desertsmash_')):return 'Saucer_arcade_whole_UI'
    if k.startswith(('$minigame_chocoborace_','$minigame_ChocoboRace_','$chocobo_customize_')):return 'Chocobo_race_whole_UI'
    if k.startswith(('$menu_Colosseum_CourseFlavor_','$menu_Colosseum_CourseTitle_')):
        return 'Colosseum_whole_UI' if re.search('_(?:GOLDA|UNDRS)_',k) else None
    if k.startswith('$menu_Colosseum_') or re.match(r'\$Release_COL\d+_(?:GOLDA|UNDRS)_',k):return 'Colosseum_whole_UI'
    if re.match(r'\$(?:GOLDS|UNDRS)_(?:ITEM|MAGIC|WEAPON|CARD)_',k) or k.startswith('$GS_SHOP_SQUARE'):return 'Saucer_Prison_shop_names'
    if k.startswith(('$keyitem_CaveKey','$keyitem_ChocoboFood','$keyitem_SylkisGreens','$keyitem_GoldTicket','$keyitem_CoupleTicket')):return 'Prison_quest_items'
    if re.match(r'\$(?:key_collection_(?:04|06|2[4-8])|keyitem_collection_(?:0(?:19|2\d|3\d|4[0-5]|48|59|65|7\d|8[0-8])))_',k):return 'Saucer_collectible_lore_and_hints'
    return None
def speech(k):
    if k.startswith(('$CARDG_QST_03_','$CARDG_QST_12_','$CARDG_QST_13_','$PHOTO_QST_04_')):return True
    if k.startswith('$WORLD_CDV_01_0100_'):return 9000<=int(k.split('_')[4])<=13600
    if k.startswith('$WORLD_CDV_01_0500_'):return 1900<=int(k.split('_')[4])<=2300
    return False
def name(k,f):
    if k.endswith(('_hint','_help','_explain')):return False
    if f=='Cait_costume_UI':return True
    if k.startswith('$card_riddle_GS_') or k.startswith('$CardChallenge_GS_') and k.endswith('_Title') or k=='$minigame_2650_ChocoboRace_Name':return True
    return f=='Saucer_Prison_shop_names' or f=='Prison_quest_items' and not k.endswith('_help') or bool(re.search(r'\$(?:minigame_3Dbattler_challenger|minigame_chocoborace_(?:coursename|chocoboname|chocobo0\d)|minigame_ChocoboRace_PartsSkill_(?:Name|name)|menu_Colosseum_CourseTitle)_',k))
def main():
    assert not (W/'reference/chapter8-supplement-source.json').exists()
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-through-chapter7-th.json');byjp=defaultdict(set)
    for k,t in base['assets'][R]['entries'].items():
        v=c['Resident_TxtRes.uasset'][k]
        if not v.get('MetaData',{}).get('ACTOR'):byjp[v['Text']].add(t)
    us=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    rows=[];ts=[];ix={};automatic={}
    for k,v in c['Resident_TxtRes.uasset'].items():
        f='speech' if speech(k) else family(k)
        if not f or not v['Text']:continue
        mode='existing' if k in base['assets'][R]['entries'] else 'translate'
        row=dict(asset=R,id=k,Japanese=v,English=us.get(k,{}),family=f,mode=mode)
        if mode!='existing':
            t=None
            if f!='speech':
                if name(k,f):t=us[k]['Text'];row['mode']='official_English_name'
                elif not re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']):t=v['Text'];row['mode']='original_symbol_or_English'
                elif len(byjp[v['Text']])==1:t=next(iter(byjp[v['Text']]));row['mode']='exact_UI_reuse'
            if t is not None:automatic[k]=t
            else:
                key=(f=='speech',v['Text'])
                if key not in ix:ix[key]=len(ts);ts.append(dict(index=len(ts),jp=v['Text'],family=f,examples=[],us=us.get(k,{}).get('Text',''),actors=[]))
                row['template']=ix[key];tr=ts[row['template']];tr['examples'].append(k)
                ac=us.get(k,{}).get('MetaData',{}).get('ACTOR','')
                if ac not in tr['actors']:tr['actors'].append(ac)
        rows.append(row)
    write('reference/chapter8-supplement-source.json',rows);write('reference/chapter8-supplement-templates.json',ts);write('translations/chapter8-supplement-automatic.json',automatic)
    print(len(rows),'inventory;',len(ts),'manual;',len(automatic),'auto;',sum(r['mode']=='existing' for r in rows),'existing')
if __name__=='__main__':main()
