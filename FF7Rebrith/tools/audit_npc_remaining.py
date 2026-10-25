"""Independent inverse scan of all visited scene text, beyond NPC naming patterns."""
from collections import Counter
from prepare_chapter9 import W,read,write
from npc_recheck import REGIONS
from choice_completion import JP


def reason(k):
    if k.startswith('$mv_psbl0_0920_'):return 'Bonus Remake/INTERmission ending movie en route to Kalm, not Ch2 NPC scene; track separately from Rebirth story coverage'
    if k.startswith('$GRASE_QST_06_'):return 'Chapter12 Hustle and Grind: Beck return odd job'
    if k.startswith(('$JUNOE_QST_06_','$JUNOE_QST_07_')):return 'Chapter12 Junon return odd jobs: Tides of War and Worry / Beneath Still Waters'
    if k.startswith('$CORLE_QST_06_'):return 'Chapter12 Trouble in Paradise odd job; earlier Johnny renovation and bird-rescue quests now included in full'
    if k.startswith('$CHADL_QST_03_') and int(k.split('_')[3])>=3100:return 'Later Corel protorelic trials 3–4 and final Gilgamesh island; first two trials through stage3000 now included'
    if k.startswith(('$C3210_','$C3230_','$GOLDS_BOS_17_','$GOLDS_BOS_18_')):return 'Chapter12 Gold Saucer main story / LOVELESS return-performance dialogue'
    if k.startswith(('$GOLDE_QST_01_','$GOLDE_QST_02_','$GOLDE_QST_03_')):return 'Chapter12 Sand and Circuses / Gold Cup or Bust / Cannot Stop Wont Stop quests'
    if k.startswith('$UNDRS_ENM_00_'):return 'Enemy Test0 battle/debug messages, explicitly ACTOR テスト０; not ambient NPC'
    if k.startswith('$GONGE_QST_05_'):return 'Chapter12 Woodland Vigil odd job; ordinary village NPC and parents all return states included'
    if k.startswith('$GONGE_QST_06_'):return 'Chapter12 Escape from Endless Writers Block odd job'
    if k.startswith('$CARDG_QST_07_'):return 'Queens Blood finale after later-region opponents / Vincent and Regina progression'
    return None


def main():
    now=read('translations/working-npc-recheck-th.json');rows=[]
    for a,d in read('reference/rebirth-jp-corpus.json').items():
        if a not in REGIONS:continue
        e=now['assets']['End/Content/Text/JP/'+a]['entries']
        for k,v in d.items():
            if not v['Text'] or not JP.search(v['Text']) or k in e:continue
            r=reason(k);assert r,(a,k,v['Text'],'Unclassified visited-scene omission')
            rows.append(dict(asset=a,id=k,jp=v['Text'],reason=r))
    write('qa/npc-recheck/visited-scene-residual-dispositions.json',rows)
    print('Independent remaining visited-scene Japanese:',len(rows),dict(Counter(r['reason'] for r in rows)))


if __name__=='__main__':main()
