"""Add reviewed Chapter 3 to the preserved UI, inventory and name release."""
import copy,hashlib,json,re,sys
from collections import Counter
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
def read(p):return json.loads((W/p).read_text('utf-8'))
def write(p,v):
    p=W/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def main():
    rows=read('reference/chapter3-source.json');scope=read('reference/chapter3-scope.json')
    assert hashlib.sha256((W/'reference/chapter3-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    values={}
    for p in sorted((W/'translations/chapter3').glob('batch-*.json')):
        batch=json.loads(p.read_text('utf-8'));assert not values.keys()&batch.keys(),p;values.update(batch)
    assert set(values)=={str(r['index']) for r in rows},('Missing/extra indices',set(values)^{str(r['index']) for r in rows})
    assets={};originals={};us={}
    for r in rows:
        a=r['asset'];k=r['id'];t=values[str(r['index'])]
        if a not in originals:
            originals[a]=txtres.parse(str(W/'source'/a));us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')))
        assert originals[a][k]['Text']==r['Text'] and originals[a][k].get('MetaData',{})==r['MetaData']
        assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Text']),k
        patch=assets.setdefault(a,dict(entries={},actors={}));patch['entries'][k]=t
        actor=r['MetaData'].get('ACTOR')
        if actor:
            label=us[a].get(k,{}).get('MetaData',{}).get('ACTOR')
            if not label:
                if actor=='？？？？':label='???'
                else:
                    votes=Counter(v.get('MetaData',{}).get('ACTOR') for n,v in us[a].items()
                        if originals[a].get(n,{}).get('MetaData',{}).get('ACTOR')==actor and v.get('MetaData',{}).get('ACTOR'))
                    assert len(votes)==1,(k,actor,votes);label=next(iter(votes))
            assert label and label.isascii(),(k,label);patch['actors'][k]=label
    output=dict(chapter=3,title=scope['title'],translated_records=len(rows),assets=assets)
    write('translations/chapter3-th.json',output)
    combined=copy.deepcopy(read('translations/working-ui-completion-th.json'))
    # Earlier source layers must not be silently edited while translating Ch.3.
    baseline=read('qa/chapter3/baseline.json')
    assert combined==read(baseline['base_source']),'Base release changed; review and record a new revision'
    for a,p in assets.items():
        dest=combined['assets'].setdefault(a,dict(entries={},actors={}))
        for field in ('entries','actors'):
            assert not dest[field].keys()&p[field].keys(),(a,field,'Existing translation overwritten')
            dest[field].update(p[field])
    combined.update(scope='Chapters 1–3 dialogue plus verified all-game UI, inventory effects and official English enemy names',
        chapter3_records=len(rows),source_only=True)
    write('translations/working-through-chapter3-th.json',combined)
    print('Assembled',len(rows),'Chapter 3 lines;',sum(len(x['entries']) for x in combined['assets'].values()),'combined records')
if __name__=='__main__':main()
