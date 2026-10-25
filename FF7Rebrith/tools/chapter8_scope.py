"""First-visit versus late-return Gold Saucer states, reviewed by source content."""
from prepare_chapter8 import W,read,write
def reason(k):
    s=k.split('_')
    if k.startswith('$C2630_MAIN_3320_') and int(s[3]) in (300,310):return 'later Wutai war reaction from Esther'
    if k.startswith('$C2630_MAIN_3320_') and int(s[3]) in (400,500):return 'Chapter12 Gold Cup victory reaction from Esther'
    if k.startswith('$UNDRS_QST_03_1100_') and int(s[4])>=800:return 'later Wutai broadcast seminar reaction'
    if k=='$UNDRS_QST_05_1000_0300_00_mma':return 'later Wutai broadcast card collector reaction'
    if k.startswith('$UNDRS_QST_06_0600_') and int(s[4])>=400:return 'later Wutai broadcast bartender reaction'
    if k.startswith('$UNDRS_NPC_10_0400_'):
        line=int(s[4])
        if 1500<=line<=2000 or 9000<=line<=11600:return 'Chapter12 Sand and Circuses / Gus party crowd and results'
    if k.startswith('$GOLDS_NPC_10_'):
        stage,line=int(s[3]),int(s[4])
        if stage==300 and 5900<=line<=6800:return 'later Wutai broadcast reaction'
        if stage==300 and (7500<=line<=8400 or 9600<=line<=9900):return 'Chapter12 Dio-Corneo naming-rights battle'
        if stage==400 and 3300<=line<=4700:return 'later Gold Cup regional odd job'
        if stage==600 and (3400<=line<=5300 or 6400<=line<=7400):return 'Chapter12 Dio-Corneo naming-rights battle'
        if stage==800 and line>=4000:return 'Chapter12 lyric contest'
        if stage==1000 and 3100<=line<=4800:return 'Chapter12 LOVELESS G-edition and lyric contest'
        if stage==1100 and 300<=line<=500:return 'Chapter12 colosseum victory reaction'
        if stage==1200:return 'endgame Ultimate Party Animal quest'
    if k.startswith('$UNDRS_NPC_10_0600_') and 2700<=int(s[4])<=2800:return 'later Wutai broadcast reaction'
    return None
if __name__=='__main__':
    rows=read('reference/chapter8-source.json');d=[dict(r,reason=reason(r['id'])) for r in rows if reason(r['id'])]
    write('reference/chapter8-deferred.json',d);print(len(rows)-len(d),'selected;',len(d),'deferred')
