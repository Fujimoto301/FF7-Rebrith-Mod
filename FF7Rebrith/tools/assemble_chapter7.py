"""Merge Chapter7 and adjacent UI over the immutable reviewed Chapters1–6 base."""
import copy,hashlib,json,re
from collections import Counter
from prepare_chapter7 import W,read,write,txtres
JP=re.compile('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]')
def values():
    d={}
    for p in sorted((W/'translations/chapter7').glob('*.json')):
        v=json.loads(p.read_text('utf-8'));assert not d.keys()&v.keys(),p;d.update(v)
    return d
def main():
    baseline=read('qa/chapter7/baseline.json');now=read('translations/working-ch1-6-recheck-th.json')
    assert now==read(baseline['base_source'])
    now=copy.deepcopy(now);patch={};sources={};us={}
    def add(a,k,v,t):
        if a not in sources:
            sources[a]=txtres.parse(str(W/'source'/a));us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')))
        assert sources[a][k]==v,(k,'source changed')
        assert t.strip() and not JP.search(t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',v['Text']),(k,'tags')
        p=patch.setdefault(a,dict(entries={},actors={}));assert k not in p['entries'];p['entries'][k]=t
        actor=v.get('MetaData',{}).get('ACTOR')
        if actor:
            label=us[a].get(k,{}).get('MetaData',{}).get('ACTOR')
            if not label:
                if re.fullmatch('[？?]+',actor):label='???'
                else:
                    votes=Counter(x.get('MetaData',{}).get('ACTOR') for n,x in us[a].items() if sources[a].get(n,{}).get('MetaData',{}).get('ACTOR')==actor and x.get('MetaData',{}).get('ACTOR'))
                    assert len(votes)==1,(k,actor,votes);label=next(iter(votes))
            assert label and not JP.search(label),(k,label);p['actors'][k]=label
    vals=values();rows=read('reference/chapter7-source.json');deferred={r['id'] for r in read('reference/chapter7-deferred.json')}
    scope=read('reference/chapter7-scope.json')
    assert hashlib.sha256((W/'reference/chapter7-source.json').read_bytes()).hexdigest()==scope['source_sha256']
    chosen=[r for r in rows if r['id'] not in deferred]
    assert {str(r['template']) for r in chosen}<=vals.keys()
    for r in chosen:
        t=vals[str(r['template'])]
        # Shared JP はい template: spoken Tifa uses ค่ะ, system choices use ใช่.
        if r['id'].endswith('_sys') and r['Text']=='はい':t='ใช่'
        add(r['asset'],r['id'],dict(Text=r['Text'],**({'MetaData':r['MetaData']} if r['MetaData'] else {})),t)
    supp=read('reference/chapter7-supplement-source.json');manual=read('translations/chapter7-supplement-manual.json');auto=read('translations/chapter7-supplement-automatic.json')
    for r in supp:
        if r['mode']=='existing':continue
        t=auto.get(r['id']) if 'template' not in r else manual[str(r['template'])]
        add(r['asset'],r['id'],r['Japanese'],t)
    for a,p in patch.items():
        for field in ('entries','actors'):
            assert not now['assets'][a][field].keys()&p[field].keys(),(a,field)
            now['assets'][a][field].update(p[field])
    output=dict(chapter=7,title='Those Left Behind',dialogue_records=len(chosen),supplement_added=sum(r['mode']!='existing' for r in supp),assets=patch)
    write('translations/chapter7-th.json',output)
    now.update(chapter7_records=len(chosen),chapter7_supplement_records=output['supplement_added'],scope='Chapters1–7 dialogue, NPCs and choices; all-game UI/effects/English names; preserves Ch1–6 recheck',source_only=True)
    write('translations/working-through-chapter7-th.json',now)
    write('reference/chapter7-build.json',dict(chapters=list(range(1,8)),source='translations/working-through-chapter7-th.json',stage='staging/ThaiJP_ThroughChapter7_Working',qa='qa/chapter7',cluster_map='reference/through-chapter7-cluster-map.json',seed='reference/ch1-6-recheck-cluster-map.json',punctuation_policy='reference/dialogue-punctuation-policy.json'))
    print(len(chosen),'chapter records;',output['supplement_added'],'supplement;',sum(len(p['entries']) for p in now['assets'].values()),'combined')
if __name__=='__main__':main()
