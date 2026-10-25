"""Final chapter: dream/interludes, both finale script versions and all boss voices."""
def scope(asset,key,text=''):
    if key.startswith('$C3410_'):return 'Ch14 Midgar dream/date and all Zack branching interludes'
    if key.startswith('$C3510_'):return 'Ch14 finale, all FOREE/CAPIT script variants and ending'
    if key.startswith('$CAPTL_BOS_'):return 'Ch14 final boss voices, all party variants'
    return None
