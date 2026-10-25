"""Freeze the release and append a separate all-game UI-choice supplement."""
import hashlib,shutil,uuid
from collections import Counter,defaultdict
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from choice_completion import family,official_name,JP


def main():
    q='qa/choice-completion'
    assert not (W/q/'baseline.json').exists(),'Keep frozen snapshot and indices'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source'])
    snap=W/q/'revisions'/uuid.uuid4().hex
    for f in [ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','tools/audit_shared_dialogs.py']:
        p=snap/f;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/f,p)
    write(q+'/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    corpus=read('reference/rebirth-jp-corpus.json');same=defaultdict(set)
    for a,p in base['assets'].items():
        data=corpus[Path(a).name]
        for key,text in p['entries'].items():
            if family(Path(a).name,key) or not data[key].get('MetaData',{}).get('ACTOR') and not key.endswith(('_mma','_mfa','_mmk','_mfk')):
                same[data[key]['Text']].add(text)
    rows=[];templates=[];indices={};automatic={}
    for asset,data in corpus.items():
        rel='End/Content/Text/JP/'+asset;us=None
        for key,item in data.items():
            f=family(asset,key)
            if not f or not item['Text']:continue
            mode='existing' if key in base['assets'].get(rel,{}).get('entries',{}) else 'unchanged' if not JP.search(item['Text']) else 'translate'
            if us is None:us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
            row=dict(asset=rel,id=key,family=f,Japanese=item,English=us.get(key,{}),mode=mode)
            if mode=='translate':
                if official_name(key):automatic.setdefault(rel,{})[key]=us[key]['Text'];row['mode']='official_English_name'
                elif len(same[item['Text']])==1:automatic.setdefault(rel,{})[key]=next(iter(same[item['Text']]));row['mode']='review_existing_UI_reuse'
                else:
                    if item['Text'] not in indices:
                        i=len(templates);indices[item['Text']]=i;templates.append(dict(index=i,jp=item['Text'],us=us.get(key,{}).get('Text',''),examples=[],family=f))
                    row['template']=indices[item['Text']];templates[row['template']]['examples'].append(key)
            rows.append(row)
    write('reference/choice-completion-source.json',rows);write('reference/choice-completion-templates.json',templates)
    write('translations/choice-completion-automatic.json',automatic)
    stage='staging/ThaiJP_ChoiceCompletion_Working';shutil.copytree(W/ctx['stage'],W/stage)
    shutil.copy2(W/ctx['cluster_map'],W/'reference/choice-completion-cluster-map.json')
    shutil.copy2(W/'qa/chapter9/build-verification.json',W/q/'build-verification.json')
    write('reference/choice-completion-build.json',dict(chapters=list(range(1,10)),source='translations/working-choice-completion-th.json',
        stage=stage,qa=q,cluster_map='reference/choice-completion-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json'))
    print(len(rows),'UI rows;',Counter(r['mode'] for r in rows),';',len(templates),'manual templates')
    for t in templates:print(t['index'],t['examples'][0],t['jp'].replace('\r\n',' / '))


if __name__=='__main__':main()
