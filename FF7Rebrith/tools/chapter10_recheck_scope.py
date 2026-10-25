"""Content and cross-file adjacency families missed by the first Ch10 pass."""
def extra(a,k):
    if a=='8800-FOREE_TxtRes.uasset' and k.startswith(('$CHADL_QST_02_2200_','$CHADL_QST_04_2900_','$CHADL_QST_04_3000_','$CHADL_QST_05_5000_')):return 'regional_protorelic_closure_in_shared_dimension_asset'
    if a!='Resident_TxtRes.uasset':return None
    if k.startswith('$C3010_'):return 'Cid_flight_service_reactions_Ch10'
    if k.startswith('$CHADL_QST_04_3100_'):return 'Gongaga_protorelic_post_scene_report_catchup'
    if k.startswith('$CHADL_QST_05_5100_'):return 'Cosmo_protorelic_post_scene_report'
    if k.startswith('$WORLD_PCV_01_1000_'):return 'Tifa_Gongaga_reactor_field_reactions_catchup'
    if k.startswith('$WORLD_CDV_03_0100_') and int(k.split('_')[4])<=2400:return 'Queens_Blood_rank_and_return_notifications_through_Cosmo'
    if k.startswith('$WORLD_CDV_01_0100_'):
        n=int(k.split('_')[4])
        if 21100<=n<=21400:return 'Cosmo_region_completion_report'
        if 26500<=n<=26700:return 'Bahamut_Arisen_simulator_unlock'
    if k.startswith('$WORLD_CDV_01_0500_'):
        n=int(k.split('_')[4])
        if n<2900 or n>3100:return 'visited_region_Chadley_all_ordinary_return_states_except_Nibel_specific'
    if k.startswith('$WORLD_CDV_02_0100_'):
        n=int(k.split('_')[4])
        if 5600<=n<=5700:return 'Cosmo_sky_chocobo_field_help'
        if 6000<=n<=6100:return 'Corel_buggy_quicksand_field_help_catchup'
    return None
