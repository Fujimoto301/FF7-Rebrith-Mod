"""Assemble reviewed Junon dialogue without changing earlier release layers."""
import copy,hashlib,json,re
from collections import Counter
from pathlib import Path
from assemble_chapter3 import W,read,write,txtres

JP=re.compile('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]')
def values():
    out={}
    for p in sorted((W/'translations/chapter4').glob('*.json')):
        d=json.loads(p.read_text('utf-8'));assert not out.keys()&d.keys(),p;out.update(d)
    assert set(out)=={str(r['index']) for r in read('reference/chapter4-templates.json')}
    return out

def main():
    rows=read('reference/chapter4-source.json');scope=read('reference/chapter4-scope.json')
    assert hashlib.sha256((W/'reference/chapter4-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    translated=values();deferred={r['id'] for r in read('reference/chapter4-deferred.json')}
    overrides=read('reference/chapter4-ui-overrides.json')
    assets={};originals={};us={}
    for r in rows:
        if r['id'] in deferred:continue
        a=r['asset'];k=r['id'];t=overrides.get(k,translated[str(r['template'])])
        if a not in originals:
            originals[a]=txtres.parse(str(W/'source'/a));us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')))
        assert originals[a][k]['Text']==r['Text'] and originals[a][k].get('MetaData',{})==r['MetaData'],k
        assert t.strip() and not JP.search(t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Text']),k
        patch=assets.setdefault(a,dict(entries={},actors={}));patch['entries'][k]=t
        actor=r['MetaData'].get('ACTOR')
        if actor:
            label=us[a].get(k,{}).get('MetaData',{}).get('ACTOR')
            if not label:
                known={'クラウド':'Cloud','ティファ':'Tifa','エアリス':'Aerith','バレット':'Barret','レッドXIII':'Red XIII','ユフィ':'Yuffie'}
                if actor in known:label=known[actor]
                elif re.fullmatch('[？?]+',actor):label='???'
                else:
                    votes=Counter(v.get('MetaData',{}).get('ACTOR') for n,v in us[a].items()
                        if originals[a].get(n,{}).get('MetaData',{}).get('ACTOR')==actor and v.get('MetaData',{}).get('ACTOR'))
                    assert len(votes)==1,(k,actor,votes);label=next(iter(votes))
            assert label and not JP.search(label),(k,label)
            patch['actors'][k]=label
    output=dict(chapter=4,title=scope['title'],translated_records=sum(len(p['entries']) for p in assets.values()),assets=assets)
    write('translations/chapter4-th.json',output)
    combined=copy.deepcopy(read('translations/working-through-chapter3-th.json'))
    baseline=read('qa/chapter4/baseline.json')
    assert combined==read(baseline['base_source']),'Base release changed'
    for a,p in assets.items():
        dest=combined['assets'].setdefault(a,dict(entries={},actors={}))
        for field in ('entries','actors'):
            assert not dest[field].keys()&p[field].keys(),(a,field)
            dest[field].update(p[field])
    combined.update(scope='Chapters 1–4 dialogue plus all-game UI, inventory effects and English enemy names',
        chapter4_records=output['translated_records'],source_only=True)
    write('translations/working-through-chapter4-th.json',combined)
    print('Assembled',output['translated_records'],'Chapter 4 records;',sum(len(p['entries']) for p in combined['assets'].values()),'combined')
if __name__=='__main__':main()
