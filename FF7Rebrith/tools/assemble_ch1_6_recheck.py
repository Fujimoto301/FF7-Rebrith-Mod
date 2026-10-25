"""Preserve the latest1–6 release and apply reviewed missing shared UI/NPCs."""
import copy
from assemble_chapter6 import read,write
from prepare_ch1_6_recheck import ROOT,R

def main():
    base=read(ROOT+'/baseline.json');ctx=base['active']
    old=read(base['snapshot']+'/'+ctx['combined_source']);assert old==read(ctx['combined_source'])
    now=copy.deepcopy(old);ui=read('translations/ch1-6-recheck-ui-th.json');speech=read('translations/ch1-6-recheck-speech-th.json')
    assert not ui.keys()&speech['entries'].keys()
    extra=read('translations/ch1-6-recheck-extra-th.json')
    assert not ui.keys()&extra.keys() and not speech['entries'].keys()&extra.keys()
    ui.update(extra)
    p=now['assets'][R]
    for field,values in [('entries',ui),('entries',speech['entries']),('actors',speech['actors'])]:
        assert not p[field].keys()&values.keys(),field;p[field].update(values)
    now.update(completed_chapter_recheck_UI_records=len(ui),completed_chapter_recheck_shared_dialogue_records=len(speech['entries']),
      scope='Chapters1–6 plus reviewed shared activity/NPC/report UI; preserves previous low-ellipsis correction',source_only=True)
    write('translations/working-ch1-6-recheck-th.json',now)
    print('Assembled',sum(len(p['entries']) for p in now['assets'].values()),'records; +',len(ui),'UI /',len(speech['entries']),'shared dialogue')

if __name__=='__main__':main()
