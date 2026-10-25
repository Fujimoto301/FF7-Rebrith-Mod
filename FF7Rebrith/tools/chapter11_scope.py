"""Nibel first visit, both Ch11 odd jobs, four protorelic stages and shared NPCs."""
def primary(asset,key):
    return asset=='8700-NIBLE_TxtRes.uasset' and not key.startswith('$C3210_')

def shared(key):
    if key.startswith(('$WORLD_CDV_02_0700_','$WORLD_MGV_01_0700_','$PHOTO_QST_07_','$CARDG_QST_16_')):return True
    if key.startswith('$PHOTO_QST_00_0700_'):return True
    if key.startswith('$WORLD_CDV_01_0100_'):
        n=int(key.split('_')[4]);return 16800<=n<=18900 or 21500<=n<=21800 or 26800<=n<=27000
    if key.startswith('$WORLD_CDV_01_0300_'):return 1500<=int(key.split('_')[4])<=1700
    if key.startswith('$WORLD_CDV_01_0500_'):return 2900<=int(key.split('_')[4])<=3100
    return False

def defer(key):
    if key.startswith('$NIBLE_QST_03_'):return 'Lament of the Damned unlocks in Chapter12 after Full Speed Ahead; not a Chapter11 odd job.'
    return None
