"""Content-reviewed Chapter7 state boundaries; retain every deferred source row."""
from prepare_chapter7 import W,read,write
# Young Nanaki voice only after Cosmo Canyon; paired against the mature wording.
YOUNG={100:[700,1020,1500,1800,3100,3300],300:[60,300,600,800,1100,1400],320:[300,400,700,800],400:[200,500,700],500:[300],700:[200,500,700,1000,1200],800:[200,500],900:[200,500,800],1000:[200,400,1600],1200:[400]}
EXTRA_YOUNG={r['id'] for r in read('reference/chapter7-source.json') if r['template'] in {943,945,950,953,956,959,963}}
EXTRA_LATE={r['id'] for r in read('reference/chapter7-source.json') if r['template'] in set(range(1101,1108))}
def reason(k):
    if k in EXTRA_LATE:return 'later Wutai broadcast reaction'
    s=k.split('_')
    if k in EXTRA_YOUNG:return 'post-Cosmo-Canyon young Nanaki alternate voice'
    if k.startswith('$CORLV_NPC_10_'):
        stage,line=int(s[3]),int(s[4])
        if stage==200 and line>=1100:return 'post-Barret reflection / post-Corel-Prison boss escape'
        if stage==500 and 700<=line<=1200:return 'later desert bird-rescue quest outcomes'
        if stage==900 and 9800<=line<=10300:return 'later Dio souvenir piecework unlock'
        if stage==1000 and line>=5400:return 'post-bird-rescue Barret village reconciliation'
    if k.startswith('$CORLE_QST_01_') and int(s[3])>=1500:return 'Johnny desert crown and renovated-inn phases require later access'
    if k.startswith('$CORLE_QST_03_2000_') and int(s[4])>=700:return 'later Wutai war broadcast reaction'
    if k.startswith('$CORLE_QST_04_'):
        if int(s[4]) in YOUNG.get(int(s[3]),[]):return 'post-Cosmo-Canyon young Nanaki alternate voice'
        if int(s[3])==1300 and int(s[4])>=400:return 'later Wutai broadcast reaction'
    return None
if __name__=='__main__':
    rows=read('reference/chapter7-source.json')
    deferred=[dict(r,reason=reason(r['id'])) for r in rows if reason(r['id'])]
    write('reference/chapter7-deferred.json',deferred)
    print(len(rows)-len(deferred),'selected;',len(deferred),'deferred')
