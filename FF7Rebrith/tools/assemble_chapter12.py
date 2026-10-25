"""Append Ch12 to the immutable, final pronoun-reviewed Ch11 release."""
import copy,hashlib,re
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
CFG='reference/chapter12-build.json'
def values():
    out={}
    for p in sorted((W/'translations/chapter12').glob('batch-*.json')):
        v=read(p);assert not out.keys()&v.keys(),p;out.update(v)
    return out
def main():
    b=read('qa/chapter12/baseline.json');cfg=read(CFG);old=read(Path(b['snapshot'])/b['active']['combined_source']);now=copy.deepcopy(old)
    rows=read('reference/chapter12-source.json');ts=read('reference/chapter12-templates.json');vals=values();assert set(vals)=={str(t['index']) for t in ts}
    assert hashlib.sha256((W/'reference/chapter12-source.json').read_bytes()).hexdigest()==read('reference/chapter12-scope.json')['source_sha256']
    patch={};us={};jp={}
    for r in rows:
        a,k=r['asset'],r['id'];t=vals[str(r['template'])];assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),(k,t)
        assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['Japanese']['Text']),(k,'tags')
        p=patch.setdefault(a,dict(entries={},actors={}));p['entries'][k]=t
        ac=r['Japanese'].get('MetaData',{}).get('ACTOR')
        if ac:
            label=r['English'].get('MetaData',{}).get('ACTOR')
            if not label:
                if a not in us:
                    us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')));jp[a]=txtres.parse(str(W/'source'/a))
                votes=Counter(v.get('MetaData',{}).get('ACTOR') for n,v in us[a].items() if jp[a].get(n,{}).get('MetaData',{}).get('ACTOR')==ac and v.get('MetaData',{}).get('ACTOR'))
                if ac=='黒マントの男':label='Robed Man'
                elif ac=='テスト０':label='Test 0' # Exact JP identity; official enemy name in US.
                else:assert len(votes)==1,(k,ac,votes);label=next(iter(votes))
            assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',label),(k,label);p['actors'][k]=label
    for a,p in patch.items():
        for f in ('entries','actors'):
            assert not now['assets'][a][f].keys()&p[f].keys();now['assets'][a][f].update(p[f])
    override=W/'reference/chapter12-context-overrides.json'
    if override.exists():
        for r in read(override)['records']:
            a,k=r['asset'],r['id'];assert now['assets'][a]['entries'][k]==r['before'];now['assets'][a]['entries'][k]=r['after']
    for a,p in old['assets'].items():
        for k,t in p['actors'].items():assert now['assets'][a]['actors'][k]==t
    write('translations/chapter12-th.json',dict(chapter=12,title='A Golden Key',assets=patch,added_records=len(rows)))
    now.update(chapter12_records=len(rows),source_only=True,scope='Ch1–12 + Common; final Ch11 pronoun-reviewed base preserved; all Ch12 dates,11 odd jobs, protorelic finale, shared NPC catch-up and Enemy Intel UI')
    write(cfg['source'],now);print('Chapter12',len(rows),'new records;',len(vals),'templates; total',sum(len(p['entries']) for p in now['assets'].values()))
if __name__=='__main__':main()
