"""Append newly discovered HUD/quest families without resetting existing indices."""
from collections import defaultdict,Counter
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from choice_completion import family,official_name,JP


def main():
    rows=read('reference/choice-completion-source.json');ts=read('reference/choice-completion-templates.json')
    previous_templates=len(ts)
    for r in rows:r['family']=family(Path(r['asset']).name,r['id'])
    have={(r['asset'],r['id']) for r in rows};ix={t['jp']:t['index'] for t in ts}
    auto=read('translations/choice-completion-automatic.json');baseline=read('qa/choice-completion/baseline.json')
    base=read(Path(baseline['snapshot'])/baseline['active']['combined_source'])
    c=read('reference/rebirth-jp-corpus.json');same=defaultdict(set)
    for a,p in base['assets'].items():
        for k,t in p['entries'].items():
            if family(Path(a).name,k):same[c[Path(a).name][k]['Text']].add(t)
    added=[]
    for asset,data in c.items():
        rel='End/Content/Text/JP/'+asset;us=None
        for k,v in data.items():
            f=family(asset,k)
            if not f or not v['Text'] or (rel,k) in have:continue
            if us is None:us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
            mode='existing' if k in base['assets'].get(rel,{}).get('entries',{}) else 'unchanged' if not JP.search(v['Text']) else 'translate'
            r=dict(asset=rel,id=k,family=f,Japanese=v,English=us.get(k,{}),mode=mode)
            if mode=='translate':
                if official_name(k):auto.setdefault(rel,{})[k]=us[k]['Text'];r['mode']='official_English_name'
                elif len(same[v['Text']])==1:auto.setdefault(rel,{})[k]=next(iter(same[v['Text']]));r['mode']='review_existing_UI_reuse'
                else:
                    if v['Text'] not in ix:
                        i=len(ts);ix[v['Text']]=i;ts.append(dict(index=i,jp=v['Text'],us=us.get(k,{}).get('Text',''),examples=[],family=f))
                    r['template']=ix[v['Text']];ts[r['template']]['examples'].append(k)
            rows.append(r);added.append(k)
    write('reference/choice-completion-source.json',rows);write('reference/choice-completion-templates.json',ts)
    write('translations/choice-completion-automatic.json',auto);write('qa/choice-completion/HUD-adjacent-additions.json',added)
    print('Added',len(added),'inventory rows; total',len(rows),Counter(r['mode'] for r in rows),';templates',len(ts))
    for t in ts[previous_templates:]:print(t['index'],t['examples'][0],t['jp'].replace('\r\n',' / '),'US:',t['us'].replace('\r\n',' / '))


if __name__=='__main__':main()
