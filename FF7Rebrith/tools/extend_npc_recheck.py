"""Append discovered NPC families without resetting frozen translation indices."""
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from npc_recheck import selected

def main():
    b=read('qa/npc-recheck/baseline.json');base=read(Path(b['snapshot'])/b['active']['combined_source'])
    rows=read('reference/npc-recheck-source.json');ts=read('reference/npc-recheck-templates.json')
    have={(r['asset'],r['id']) for r in rows};ix={t['jp']:t['index'] for t in ts};old=len(ts)
    for a,d in read('reference/rebirth-jp-corpus.json').items():
        rel='End/Content/Text/JP/'+a;us=None
        for k,v in d.items():
            f=selected(a,k)
            if not f or not v['Text'] or (rel,k) in have:continue
            if us is None:us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
            r=dict(asset=rel,id=k,family=f,Japanese=v,English=us.get(k,{}),mode='existing' if k in base['assets'].get(rel,{}).get('entries',{}) else 'translate')
            if r['mode']=='translate':
                jp=v['Text']
                if jp not in ix:ix[jp]=len(ts);ts.append(dict(index=len(ts),jp=jp,us=us.get(k,{}).get('Text',''),examples=[],actors=[]))
                i=ix[jp];r['template']=i;ts[i]['examples'].append(k);act=us.get(k,{}).get('MetaData',{}).get('ACTOR','')
                if act not in ts[i]['actors']:ts[i]['actors'].append(act)
            rows.append(r)
    write('reference/npc-recheck-source.json',rows);write('reference/npc-recheck-templates.json',ts)
    print('inventory',len(rows),'new',sum(r['mode']=='translate' for r in rows),'templates',len(ts))
    for t in ts[old:]:print(t['index'],t['jp'].replace('\r\n',' / '))

if __name__=='__main__':main()
