"""Assemble Chapter11 over the immutable fully reviewed Chapter1–10 base."""
import copy,hashlib,re
from collections import Counter
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres

CFG='reference/chapter11-build.json'
def values():
    out={}
    for p in sorted((W/'translations/chapter11').glob('batch-*.json')):
        v=read(p);assert not out.keys()&v.keys(),p;out.update(v)
    return out
def main():
    cfg=read(CFG);b=read('qa/chapter11/baseline.json');old=read(Path(b['snapshot'])/b['active']['combined_source']);now=copy.deepcopy(old)
    rows=read('reference/chapter11-source.json');ts=read('reference/chapter11-templates.json');vals=values()
    assert set(vals)=={str(t['index']) for t in ts}
    extra=read('reference/chapter11-recheck-source.json') if (W/'reference/chapter11-recheck-source.json').exists() else []
    if extra:
        add=read('translations/chapter11-recheck-lines.json');assert set(add)=={r['template'] for r in extra} and not vals.keys()&add.keys();vals.update(add);rows+=extra
    assert hashlib.sha256((W/'reference/chapter11-source.json').read_bytes()).hexdigest()==read('reference/chapter11-scope.json')['source_sha256']
    patch={};jp={};us={}
    for r in rows:
        a,k=r['asset'],r['id'];t=vals[str(r['template'])]
        assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),(k,t)
        assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['Japanese']['Text']),(k,'tags')
        p=patch.setdefault(a,dict(entries={},actors={}));p['entries'][k]=t
        ac=r['Japanese'].get('MetaData',{}).get('ACTOR')
        if ac:
            label=r['English'].get('MetaData',{}).get('ACTOR')
            if not label:
                if a not in us:
                    us[a]=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')));jp[a]=txtres.parse(str(W/'source'/a))
                votes=Counter(v.get('MetaData',{}).get('ACTOR') for n,v in us[a].items() if jp[a].get(n,{}).get('MetaData',{}).get('ACTOR')==ac and v.get('MetaData',{}).get('ACTOR'))
                if ac=='黒マントの男':label='Robed Man' # JP explicitly singular; US actor absent on this exact take.
                else:
                    assert len(votes)==1,(k,ac,votes);label=next(iter(votes))
            assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',label),(k,label);p['actors'][k]=label
    for a,p in patch.items():
        for f in ('entries','actors'):
            assert not now['assets'][a][f].keys()&p[f].keys();now['assets'][a][f].update(p[f])
    # The frozen base already contains both overlays. Full-read corrections take
    # precedence where the older overlay describes an intermediate wording.
    from context_recheck import decisions
    from context_full_read import decisions as full_decisions
    effective={(r['asset'],r['id']):r['after'] for r in decisions()}
    effective.update({(r['asset'],r['id']):r['after'] for r in full_decisions()})
    for (a,k),t in effective.items():assert now['assets'][a]['entries'][k]==t,(a,k,'Latest editorial overlay lost')
    for a,p in old['assets'].items():
        for f in ('entries','actors'):assert all(now['assets'][a][f][k]==t for k,t in p[f].items()),(a,f)
    from chapter11_recheck import overlay as recheck_overlay
    recheck_overlay(now)
    from pronoun_context import overlay as pronoun_overlay
    pronoun_overlay(now)
    for a,p in patch.items():
        for k in p['entries']:p['entries'][k]=now['assets'][a]['entries'][k]
    write('translations/chapter11-th.json',dict(chapter=11,title='The Long Shadow of Shinra',assets=patch,added_records=len(rows)))
    now.update(chapter11_records=len(rows),source_only=True,scope='Ch1–11; all Nibel NPC states, both Ch11 odd jobs, four protorelic stages and shared regional dialogue; preserves full Ch1–10 editorial review')
    write(cfg['source'],now)
    print('Chapter11:',len(rows),'new records;',len(vals),'templates; combined',sum(len(p['entries']) for p in now['assets'].values()))
if __name__=='__main__':main()
