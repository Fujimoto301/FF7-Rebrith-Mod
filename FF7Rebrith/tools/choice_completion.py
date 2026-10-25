"""Whole-corpus choice/UI inventory, including case-sensitive WorldSys IDs."""
import re

JP=re.compile('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19\uff66-\uff9f]')


def musical_notation(key,text):
    # These two original US note labels use a middle dot for octave notation.
    return (key,text) in {('$minigame_piano_C2','C・'),('$minigame_piano_C2_sharp','C・♯')}


def family(asset,key):
    if key.endswith('_sys'):return 'scene_choice_and_prompt'
    if asset!='Resident_TxtRes.uasset':return None
    if re.match(r'^\$[A-Z]+_(?i:MINIGAME)_',key):return 'field_activity_names'
    if key.startswith(('$menu_WorldReport_','$AreaReport_')):return 'world_intel_whole_UI'
    if re.match(r'^\$[A-Z]+_(?:ITEM|MAGIC|CLOSET|WEAPON|CARD|MOOGLESHOP)_',key):return 'all_region_shop_names'
    for prefixes,name in [
        (('$GC_','$GE_','$GF_','$GAN_','$GambitMaterialSkillText'),'gambit_conditions_targets_and_enemy_help'),
        (('$ChocoboGass_','$Qst14_Johnnymaterials_','$Qst16_EnemyKill'),'quest_progress_counters'),
        (('$4000_zack_','$2500_CSMOA_Gi_Village','$MAPICON_'),'map_and_activity_labels'),
        (('$3120_MenuLog_','$CSMOA_ResearchedLifeSpot'),'adjoining_HUD_objectives'),
        (('$card_challenge_','$card_normal_','$card_riddle_','$CHOFA_ChocoboTimeAttack'),'card_and_chocobo_activity_labels'),
        (('$Photograph_minigame_',),'photograph_activity_whole_UI'),
        (('$menu_Chadrey_','$Release_COL30'),'combat_course_requirements'),
        (('$menu_EnemyBookAreaText_','$menu_EnemyBook_BattleLog_','$menu_EnemyBook_EnemyNumber','$menu_EnemyBook_KeyGuide_'),'enemy_index_navigation_and_locations'),
        (('$name_','$npc_','$WeakPoint'),'character_and_NPC_UI_names'),
        (('$key_','$keyitem_','$it_key_','$it_secret_','$it_chocobo_'),'key_items_and_collectibles'),
        (('$alert_message_',),'equipment_restriction_notifications'),
        (('$level','$chapter_'),'quest_objectives_locations_and_chapter_labels'),
        (('$WorldSys_',),'world_system_and_camp'),
        (('$ChocoboCapture_',),'chocobo_capture_HUD_objectives'),
        (('$menu_BattleMission_',),'battle_and_quest_objectives'),
        (('$menu_secretquest_',),'party_quest_ranks'),
        (('$keyitem_quest','$it_key_grass_story'),'quest_item_descriptions'),
        (('$gambit_','$Gambit_'),'gears_and_gambits_whole_UI'),
        (('$costume_',),'costume_selection'),
        (('$minigame_',),'minigame_whole_UI'),
        (('$menu_Buggy_',),'buggy_pause_retry'),
        (('$CardChallenge_',),'card_challenge_whole_UI'),
        (('$card_Choices_',),'card_match_choices'),
        (('$menu_Colosseum_CourseTitle_','$menu_Colosseum_CourseFlavor_'),'combat_course_selection'),
        (('$menu_Ending_CancelButton_',),'ending_navigation')]:
        if key.startswith(prefixes):return name
    return None


def official_name(key):
    return (bool(re.match(r'^\$[A-Z]+_(?i:MINIGAME)_',key)) or
            bool(re.match(r'^\$[A-Z]+_(?:ITEM|MAGIC|CLOSET|WEAPON|CARD|MOOGLESHOP)_',key)) or
            key.startswith(('$name_','$npc_','$WeakPoint','$menu_EnemyBookAreaText_','$MAPICON_','$card_normal_','$card_riddle_','$CHOFA_ChocoboTimeAttack','$2500_CSMOA_Gi_Village','$4000_zack_')) or
            key.startswith('$AreaReport_') and key.endswith('_Title') or
            key.startswith(('$key_','$keyitem_','$it_key_')) and not key.endswith(('_help','_hint')) or
            key.startswith('$GF_') and ('Name_' in key or key.startswith('$GF_EN_UnitAct_') or key=='$GF_UnitAct_ATK_Collect') or
            key.startswith('$menu_WorldReport_') and bool(re.search(r'_Title(?:_NA)?$',key)) or
            key.startswith(('$keyitem_quest','$it_key_grass_story')) and not key.endswith('_help') or
            key.startswith('$menu_Colosseum_CourseTitle_') or
            key.startswith('$CardChallenge_') and key.endswith(('_Title','_Jenre')) or
            bool(re.fullmatch(r'\$costume_(?:cloth|character)_.*',key)) or
            bool(re.fullmatch(r'\$gambit_.*(?:PresetTitle\d+|DisplayName[A-Z])',key)))
