"""Chapter10 Cosmo Canyon and its complete NPC/quest/shared families."""
def primary(asset,key):
    return asset=='8600-COSME_TxtRes.uasset' or asset=='4000-MIDGR_TxtRes.uasset' and key.startswith(('$C3010_','$MIDGR_NPC_10_'))


def shared(key):
    if key.startswith(('$WORLD_CDV_02_0600_','$WORLD_MGV_01_0600_','$PHOTO_QST_06_','$CARDG_QST_15_')):return True
    if key.startswith('$PHOTO_QST_00_') and int(key.split('_')[3])==600:return True
    if key.startswith('$PHOTO_QST_03_'):return True # renovated Johnny inn unlocked before Ch10; recover any remaining ranks
    if key.startswith('$WORLD_CDV_01_0100_') and 14700<=int(key.split('_')[4])<=16700:return True
    if key.startswith('$WORLD_CDV_01_0300_') and 1100<=int(key.split('_')[4])<=1400:return True
    if key.startswith('$WORLD_CDV_01_0500_') and 2500<=int(key.split('_')[4])<=2800:return True
    return False


def defer(key):
    if key.startswith('$COSME_QST_05_'):return 'Victim of Circumstance is a new Chapter12 odd job; ordinary Cosmo NPC all return states are included'
    return None
