"""All Chapter12 branches,11 odd jobs,final protorelic and common catch-up."""
import re
JP=re.compile('[\u3040-\u30ff\u3400-\u9fff]')
def scope(asset,key,text=''):
    if key.startswith(('$C3210_','$C3220_','$C3230_')):return 'Ch12 main story,interlude,date/LOVELESS and ship variants'
    if asset=='4000-MIDGR_TxtRes.uasset':return None
    if asset=='8100-GRASE_TxtRes.uasset':
        if key.startswith('$GRASE_QST_06_'):return 'Hustle and Grind'
        if key.startswith('$mv_psbl0_'):return 'Earlier Japanese-only walking banter catch-up; English take absent,do not invent actor metadata'
    if asset=='8200-JUNOE_TxtRes.uasset' and key.startswith(('$JUNOE_QST_06_','$JUNOE_QST_07_')):return 'Tides of War and Worry / Beneath Still Waters'
    if asset=='8300-CORLE_TxtRes.uasset' and key.startswith(('$CORLE_QST_06_','$CHADL_QST_03_')):return 'Trouble in Paradise / final Corel protorelic'
    if asset=='8400-GOLDE_TxtRes.uasset' and key.startswith(('$GOLDE_QST_01_','$GOLDE_QST_02_','$GOLDE_QST_03_','$GOLDS_BOS_17_','$GOLDS_BOS_18_','$UNDRS_ENM_00_')):return 'Sand and Circuses / Gold Cup or Bust / Can’t Stop Won’t Stop / all Ch12 boss voices'
    if asset=='8500-GONGE_TxtRes.uasset' and key.startswith(('$CARDG_QST_07_','$GONGE_QST_05_','$GONGE_QST_06_')):return 'Woodland Vigil / Escape from Endless Writer’s Block / final Queen’s Blood'
    if asset=='8600-COSME_TxtRes.uasset' and key.startswith('$COSME_QST_05_'):return 'Victim of Circumstance'
    if asset=='8700-NIBLE_TxtRes.uasset' and key.startswith('$NIBLE_QST_03_'):return 'Lament of the Damned'
    if asset=='8800-FOREE_TxtRes.uasset' and key.startswith(('$CHADL_QST_03_','$CHADL_QST_06_','$CHADL_QST_07_')):return 'Final protorelic / Gilgamesh Island,available during Ch12; not Temple main story'
    if asset=='Resident_TxtRes.uasset':
        if key.startswith(('$CARDG_QST_05_','$CARDG_QST_06_','$CARDG_QST_07_','$PHOTO_QST_00_0800_','$WORLD_CDV_','$WORLD_QST_01_','$CHADL_QST_03_','$CHADL_QST_06_','$COMMN_BOS_50_','$PIANO_QST_01_')):return 'Shared return-region,QB finale,pirate treasure,photo/piano completion and protorelic dialogue'
        if key.startswith('$NIBLT_NPC_20_'):return 'Earlier Nibel shared NPC variants catch-up,including robed villagers'
        if key.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')) and JP.search(text):return 'Whole remaining Enemy Intel text/tips UI; user authorized all-game UI,not future spoken story'
    return None
