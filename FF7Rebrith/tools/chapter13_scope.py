"""Temple chapter, all party trials and boss voices; exclude Ch14 dreams/finale."""
def scope(asset,key,text=''):
    if key.startswith(('$C3310_','$C3320_','$C3330_','$C3340_')):
        return 'Ch13 voyage, Temple of the Ancients, both parties and all trials'
    if asset=='8800-FOREE_TxtRes.uasset' and key.startswith('$TEMPL_BOS_'):
        return 'Ch13 Temple boss voices, all party variants'
    if asset=='Resident_TxtRes.uasset' and key.startswith('$PHOTO_QST_00_0900_'):
        return 'Shared photography completion catch-up available before point of no return'
    return None
