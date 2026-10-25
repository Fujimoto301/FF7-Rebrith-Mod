"""Merge all-game choice UI over the frozen Ch1–9 release; no spoken text edits."""
import copy,re,hashlib
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write
from choice_completion import JP


def main():
    baseline=read('qa/choice-completion/baseline.json');ctx=baseline['active']
    base=read(Path(baseline['snapshot'])/ctx['combined_source']);now=copy.deepcopy(base)
    automatic=read('translations/choice-completion-automatic.json');values={}
    for path in sorted((W/'translations/choice-completion').glob('*.json')):
        for key,text in read(path).items():assert key not in values,(path,key);values[key]=text
    rows=read('reference/choice-completion-source.json');patch={};review=[]
    for row in rows:
        if row['mode'] in ('existing','unchanged'):continue
        a,k=row['asset'],row['id'];jp=row['Japanese']['Text']
        text=values[str(row['template'])] if 'template' in row else automatic[a][k]
        assert text.strip() and text.strip()!='<>' and not JP.search(text),(k,text)
        assert re.findall('</?[^>]+>',jp)==re.findall('</?[^>]+>',text),(k,'tags')
        p=patch.setdefault(a,dict(entries={},actors={}))
        assert k not in base['assets'].get(a,{}).get('entries',{}),(k,'Changed prior release')
        p['entries'][k]=text
        if row['Japanese'].get('MetaData',{}).get('ACTOR'):
            label=row['English'].get('MetaData',{}).get('ACTOR')
            assert label and not JP.search(label),(k,'actor label')
            p['actors'][k]=label
        review.append(dict(asset=a,id=k,family=row['family'],jp=jp,thai=text,mode=row['mode'],template=row.get('template')))
    for a,p in patch.items():
        dst=now['assets'].setdefault(a,dict(entries={},actors={}))
        for field in ('entries','actors'):dst[field].update(p[field])
    write('translations/choice-completion-th.json',dict(scope='All-game scene choice UI and related shared UI, no new spoken dialogue',assets=patch))
    now.update(scope='Ch1–9 dialogue plus all-game choice/system UI supplement; later spoken dialogue unchanged',source_only=True,choice_completion=True)
    write('translations/working-choice-completion-th.json',now)
    write('qa/choice-completion/review-records.json',review)
    import build_prototype as b
    seed=read(ctx['cluster_map']);clusters={c for p in now['assets'].values() for t in p['entries'].values() for c in b.split_clusters(re.sub('<[^>]+>','',t)) if any('\u0e00'<=ch<='\u0e7f' for ch in c)}
    print('New UI',len(review),'combined',sum(len(p['entries']) for p in now['assets'].values()),'text assets',len(now['assets']))
    print('Missing clusters',sorted(clusters-set(seed)))


if __name__=='__main__':main()
