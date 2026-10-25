"""Merge the immutable Chapter10 inventory over the enemy-action corrected base."""
import copy,re,hashlib
from collections import Counter
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres

CFG='reference/chapter10-build.json'
def values():
    vals={}
    for p in sorted((W/'translations/chapter10').glob('*.json')):
        v=read(p);assert not vals.keys()&v.keys(),(p,vals.keys()&v.keys());vals.update(v)
    return vals

def main():
    cfg=read(CFG);b=read('qa/chapter10/baseline.json');base=read(Path(b['snapshot'])/b['active']['combined_source']);now=copy.deepcopy(base)
    rows=read('reference/chapter10-source.json');ts=read('reference/chapter10-templates.json');vals=values()
    expected={str(t['index']) for t in ts}
    if (W/'reference/chapter10-recheck-source.json').exists():
        extra=read('reference/chapter10-recheck-source.json');rows+=extra;v=read('translations/chapter10-recheck-lines.json')
        assert not vals.keys()&v.keys();vals.update(v);expected.update(r['template'] for r in extra)
    assert set(vals)==expected,('missing',expected-vals.keys())
    assert read('reference/chapter10-scope.json')['source_sha256']==hashlib.sha256((W/'reference/chapter10-source.json').read_bytes()).hexdigest()
    patch={};us={};jp={}
    for r in rows:
        a,k=r['asset'],r['id'];t=vals[str(r['template'])]
        assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),(k,t)
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
        now['assets'].setdefault(a,dict(entries={},actors={}))
        for field in ('entries','actors'):
            assert not now['assets'][a][field].keys()&p[field].keys(),(a,field);now['assets'][a][field].update(p[field])
    write('translations/chapter10-th.json',dict(chapter=10,title='Watcher of the Vale',assets=patch,added_records=len(rows)))
    now.update(chapter10_records=len(rows),source_only=True,scope='Ch1–10 with all Cosmo NPC states, four side quests, four protorelic challenges, Zack Midgar and shared returns; preserves enemy-action/NPC/choice corrections')
    from chapter4_door_fix import apply_overlay
    apply_overlay(now)
    from chapter4_choice_fix import overlay as apply_choice_overlay
    apply_choice_overlay(now)
    from context_recheck import overlay as apply_context_overlay,active as context_active,decisions
    apply_context_overlay(now)
    if context_active():
        current_patch=read('translations/chapter10-th.json')
        for r in decisions():
            p=current_patch['assets'].get(r['asset'],{})
            if r['id'] in p.get('entries',{}):p['entries'][r['id']]=r['after']
        write('translations/chapter10-th.json',current_patch)
    from context_full_read import overlay as full_overlay
    full_overlay(now)
    current_patch=read('translations/chapter10-th.json');full_overlay(current_patch);write('translations/chapter10-th.json',current_patch)
    write(cfg['source'],now)
    print('New',len(rows),'Combined',sum(len(p['entries']) for p in now['assets'].values()),'templates',len(vals))

if __name__=='__main__':main()
