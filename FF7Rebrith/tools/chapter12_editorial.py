"""Exact reviewed revisions; preserve draft history and the frozen Ch11 base."""
from assemble_chapter12 import values
from prepare_chapter9 import W,read,write

def main():
    vals=values();fix={
      1528:('จงซะ','เฉิงซะ'),2029:('ที่นายถูกกระทำ','ที่เจ้านายถูกกระทำ'),
      2398:('นอกจากนาย','นอกจากเจ้านาย'),3414:('รูด้วยเหรอ','รู้ด้วยเหรอ'),
      3728:('Neck Bite','Throat Clamp'),3734:('Spin Rush','Barbed Boomerang'),
      3690:('ขัดการเชื่อมต่อกับรูฟัส','ขัดการเชื่อมต่อกับรูฟัสจากท่า『Heel』'),
      3719:('ระหว่างวางกับดัก','ระหว่างใช้『Set Up』วางกับดัก'),
      3723:('หลังป้องกันสมบูรณ์แบบ','หลังท่า『Don\'t Think So』'),
      3737:('การโจมตีไฟฟ้าจากก้าม','ท่า『High Voltage』'),
      3750:('การจู่โจมรุนแรง','ท่า『Death from Above』'),
      3752:('ก่อนพุ่งชน','ก่อนท่า『Charge』พุ่งชน'),
      3756:('ภาวะพัก','ภาวะพัก『Quick Nap』'),3757:('ภาวะงีบ','ภาวะงีบ『Quick Nap』'),
      3760:('จะพัก','จะพักด้วย『Breather』'),
      3762:('โหมดปกติ','Low Voltage'),
      3777:('ระเบิดตัวเอง','ใช้『Self-Destruct』ระเบิดตัวเอง'),
      3785:('เสนอให้เสี่ยงดวง','ใช้『Take a Gamble』'),
      3798:('ขณะซุ่มโจมตี','ขณะใช้『Ambush』ซุ่มโจมตี'),3799:('ขณะซุ่มโจมตี','ขณะใช้『Ambush』ซุ่มโจมตี'),
      3815:('การเวียนว่าย','『Resurrection』'),3816:('การเวียนว่าย','『Resurrection』'),3817:('การเวียนว่าย','『Resurrection』'),
      3834:('จะตื่นพลังเป็นระยะ','จะใช้『Galvanize』ตื่นพลังเป็นระยะ'),
    }
    changes=[]
    for n,(a,z) in fix.items():
        t=vals[str(n)];assert a in t,(n,a);after=t.replace(a,z)
        changes.append(dict(template=n,before=t,after=after,reason='Context or official action name reviewed against Japanese and exact same-ID US; action names disambiguated by enemy.'));vals[str(n)]=after
    for n,a,z in [(3762,'โหมดสะสมประจุ','Supercharged'),(3785,'เพื่อเริ่มรูเล็ต','เพื่อเริ่ม『Roulette』'),(3818,'พยายามคืนชีพพวกพ้องที่ตาย','พยายามใช้『Resurrection』คืนชีพพวกพ้องที่ตาย'),(3818,'คำร่ายคืนชีพ','『Arise』')]:
        t=vals[str(n)];assert a in t;after=t.replace(a,z);changes.append(dict(template=n,before=t,after=after,reason='Retain exact official English action labels in Enemy Intel UI.'));vals[str(n)]=after
    for p in sorted((W/'translations/chapter12').glob('batch-*.json')):
        d=read(p);write(p,{k:vals[k] for k in d})
    write('qa/chapter12/editorial-action-revisions.json',dict(records=changes))
    now=read('translations/working-through-chapter12-th.json');corpus=read('reference/rebirth-jp-corpus.json');over=[]
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            after=t
            if k.startswith('$GOLDE_QST_03_') and k.endswith('_sys'):after=after.replace('ท้าทายผู้จัดการ Shinra','ท้าทายหัวหน้าแผนก Shinra')
            if k=='$GONGE_QST_05_1200_1400_00_sys':after='ท่าทีที่ชวนให้สงสัย'
            if after!=t:over.append(dict(asset=a,id=k,before=t,after=after,jp=corpus[a.split('/')[-1]][k]['Text'],reason='Question occupation aligned with dialogue; Cissnei option asks about suggestive/evasive behavior, avoiding vague wording.'))
    assert len(over)==7
    write('reference/chapter12-context-overrides.json',dict(records=over))
    print('Revised',len(changes),'draft entries and',len(over),'existing choice questions/options')
if __name__=='__main__':main()
