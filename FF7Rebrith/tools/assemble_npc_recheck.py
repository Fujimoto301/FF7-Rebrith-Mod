"""Merge reviewed NPC dialogue over the frozen corrected UI release."""
import copy,re
from pathlib import Path
from prepare_chapter9 import W,read,write
from choice_completion import JP


def main():
    baseline=read('qa/npc-recheck/baseline.json');base=read(Path(baseline['snapshot'])/baseline['active']['combined_source'])
    rows=read('reference/npc-recheck-source.json');values={}
    for p in sorted((W/'translations/npc-recheck').glob('*.json')):
        for k,t in read(p).items():assert k not in values;values[k]=t
    now=copy.deepcopy(base);patch={};review=[]
    for r in rows:
        if r['mode']=='existing':continue
        a,k=r['asset'],r['id'];t=values[str(r['template'])];jp=r['Japanese']['Text']
        assert t.strip() and not JP.search(t),(k,t)
        assert re.findall('</?[^>]+>',jp)==re.findall('</?[^>]+>',t),k
        dst=patch.setdefault(a,dict(entries={},actors={}))
        dst['entries'][k]=t;label=r['English'].get('MetaData',{}).get('ACTOR','')
        if r['Japanese'].get('MetaData',{}).get('ACTOR'):
            if not label and r['Japanese']['MetaData']['ACTOR']=='コモーグリ':
                label='Mooglets'  # Same JP actor has this US label on adjacent voiced records.
            assert label and not JP.search(label),(k,label);dst['actors'][k]=label
        review.append(dict(asset=a,id=k,jp=jp,thai=t,actor=label,template=r['template'],family=r['family']))
    for a,p in patch.items():
        for field in ['entries','actors']:now['assets'][a][field].update(p[field])
    now.update(scope='Ch1–9 plus recovered visited-region NPCs in all return states and shared field dialogue',npc_recheck=True)
    write('translations/npc-recheck-th.json',dict(assets=patch));write('translations/working-npc-recheck-th.json',now)
    write('qa/npc-recheck/review-records.json',review)
    import build_prototype as b
    clusters={c for p in now['assets'].values() for t in p['entries'].values() for c in b.split_clusters(re.sub('<[^>]+>','',t)) if any('\u0e00'<=ch<='\u0e7f' for ch in c)}
    cm=read('reference/npc-recheck-cluster-map.json')
    print('Added',len(review),'total',sum(len(p['entries']) for p in now['assets'].values()),'missing clusters',sorted(clusters-set(cm)))


if __name__=='__main__':main()
