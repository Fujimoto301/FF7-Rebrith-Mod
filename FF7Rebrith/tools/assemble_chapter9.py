"""Assemble complete Ch9 over the corrected, immutable current Ch8 baseline."""
import copy,re,hashlib
from collections import Counter
from prepare_chapter9 import W,read,write,txtres

def values():
    vals=read('translations/chapter9/reused-lines.json')
    for p in sorted((W/'translations/chapter9').glob('*.json')):
        if p.name=='reused-lines.json':continue
        vals.update(read(p))
    return vals

def main():
    b=read('qa/chapter9/baseline.json');now=read(b['base_source']);assert now==read('translations/working-through-chapter8-th.json');now=copy.deepcopy(now)
    rows=read('reference/chapter9-source.json');scope=read('reference/chapter9-scope.json');assert scope['source_sha256']==hashlib.sha256((W/'reference/chapter9-source.json').read_bytes()).hexdigest()
    vals=values();patch={};us={};jp={}
    for r in rows:
        if r['reason']:continue
        a,k=r['asset'],r['id'];t=vals[str(r['template'])]
        assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),(k,'tags')
        p=patch.setdefault(a,dict(entries={},actors={}));p['entries'][k]=t
        ac=r['Japanese'].get('MetaData',{}).get('ACTOR')
        if ac:
            label=r['English'].get('MetaData',{}).get('ACTOR')
            if not label:
                if a not in us:
                    us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')));jp[a]=txtres.parse(str(W/'source'/a))
                votes=Counter(v.get('MetaData',{}).get('ACTOR') for n,v in us[a].items() if jp[a].get(n,{}).get('MetaData',{}).get('ACTOR')==ac and v.get('MetaData',{}).get('ACTOR'))
                assert len(votes)==1,(k,ac,votes);label=next(iter(votes))
            assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',label),(k,label);p['actors'][k]=label
    for a,p in patch.items():
        for field in ('entries','actors'):
            now['assets'].setdefault(a,dict(entries={},actors={}))
            assert not now['assets'][a][field].keys()&p[field].keys(),(a,field);now['assets'][a][field].update(p[field])
    write('translations/chapter9-th.json',dict(chapter=9,title='The Planet Stirs',assets=patch,added_records=sum(len(p['entries']) for p in patch.values())))
    now.update(chapter9_records=scope['selected'],source_only=True,scope='Chapters1–9 dialogue, NPCs and choices; preserves correctedCh8 baseline; registered Gongaga whole UI families')
    write('translations/working-through-chapter9-th.json',now)
    write('reference/chapter9-build.json',dict(chapters=list(range(1,10)),source='translations/working-through-chapter9-th.json',stage='staging/ThaiJP_ThroughChapter9_Working',qa='qa/chapter9',cluster_map='reference/through-chapter9-cluster-map.json',seed='reference/through-chapter8-cluster-map.json',punctuation_policy='reference/dialogue-punctuation-policy.json'))
    print('Ch9',scope['selected'],'new;',sum(len(p['entries']) for p in now['assets'].values()),'combined;',len(now['assets']),'text assets')

if __name__=='__main__':main()
