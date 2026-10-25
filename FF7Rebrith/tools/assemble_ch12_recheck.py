"""Apply reviewed shared UI to the preserved Chapters 1–6 release."""
import copy
from assemble_chapter6 import read,write
from prepare_ch12_recheck import ROOT,R

def main():
    base=read(ROOT+'/baseline.json');old=read(base['snapshot']+'/translations/working-through-chapter6-th.json')
    assert old==read('translations/working-through-chapter6-th.json'),'Stable Ch.6 baseline changed'
    now=copy.deepcopy(old);patch=read('translations/ch12-recheck-ui-th.json')
    assert not patch.keys()&now['assets'][R]['entries'].keys()
    now['assets'][R]['entries'].update(patch)
    recap=read('translations/ch1-opening-recap-th.json')
    now['assets']['End/Content/Text/JP/0005-TITLB_TxtRes.uasset']=dict(entries=recap,actors={})
    now.update(ch12_recheck_UI_records=len(patch),ch1_opening_recap_records=len(recap),source_only=True,
      scope='Chapters1–6 preserved, Ch.1–2 completeness recheck/shared activity UI and low dialogue ellipsis')
    write('translations/working-ch12-recheck-th.json',now)
    print('Assembled',sum(len(p['entries']) for p in now['assets'].values()),'records; preserved',sum(len(p['entries']) for p in old['assets'].values()))

if __name__=='__main__':main()
