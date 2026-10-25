"""Permanent full NPC-family inventory for visited Ch2–9 regions."""
import re

REGIONS={'8100-GRASE_TxtRes.uasset','8200-JUNOE_TxtRes.uasset','8300-CORLE_TxtRes.uasset','8400-GOLDE_TxtRes.uasset','8500-GONGE_TxtRes.uasset'}


def selected(asset,key):
    if asset=='8300-CORLE_TxtRes.uasset' and key.startswith(('$CORLE_QST_01_','$CORLE_QST_02_','$CORLE_QST_03_','$CORLE_QST_04_','$CORLE_QST_05_','$COSTT_QST_04_')):return 'Corel_earlier_quest_NPC_all_return_states'
    if asset=='8300-CORLE_TxtRes.uasset' and key.startswith('$CHADL_QST_03_') and int(key.split('_')[3])<=3000:return 'Corel_desert_first_two_protorelic_trials_Ch9'
    if asset=='8400-GOLDE_TxtRes.uasset' and key.startswith(('$C2630_MAIN_3320_','$UNDRS_QST_03_','$UNDRS_QST_05_','$UNDRS_QST_06_')):return 'Corel_Prison_earlier_NPC_all_return_states'
    if asset=='8500-GONGE_TxtRes.uasset' and key.startswith(('$C2710_MAIN_3500_','$C2710_MAIN_3600_')):return 'Zack_parents_all_return_states'
    if asset=='8100-GRASE_TxtRes.uasset' and re.match(r'^\$GRASE_QST_0[1-5]_',key):return 'Grasslands_quest_NPC_all_return_states'
    if asset=='8200-JUNOE_TxtRes.uasset' and key.startswith(('$JUNOE_QST_02_','$JUNOE_QST_03_')):return 'Junon_quest_NPC_all_return_states'
    # Include *all* states of each visited region's NPC family, including returns.
    if asset in REGIONS and '_NPC_' in key:return 'visited_region_NPC_all_states'
    if asset!='Resident_TxtRes.uasset':return None
    if key.startswith(('$WORLD_CDV_02_0500_','$WORLD_MGV_01_0500_')):return 'Gongaga_shared_intel_NPC_all_return_states'
    if key.startswith('$MOGLE_QST_01_'):return 'moogle_merchant_and_children_all_states'
    if key.startswith(('$CARDG_QST_01_','$CARDG_QST_04_')):return 'visited_region_Queens_Blood_NPC'
    if key.startswith('$WORLD_CDV_01_0100_'):
        line=int(key.split('_')[4])
        if line<=14600 or 19000<=line<=21000 or 21900<=line<=26400:return 'visited_region_Chadley_ambient_and_reports'
    if key.startswith('$WORLD_CDV_01_0300_') and int(key.split('_')[4])<=1000:return 'visited_region_summon_victory_NPC'
    if key.startswith('$WORLD_PCV_01_') and not key.startswith('$WORLD_PCV_01_1000_'):return 'visited_region_party_field_reactions'
    if key.startswith(('$WORLD_CDV_02_0400_','$WORLD_MGV_01_0400_')):return 'Corel_shared_intel_NPC'
    if key.startswith('$WORLD_CDV_02_0100_') and int(key.split('_')[4])<=5500:return 'visited_region_chocobo_NPC_help'
    if key.startswith('$PHOTO_QST_00_') and int(key.split('_')[3])<=500:return 'photographer_ranks_through_Gongaga'
    return None
