"""Freeze the current UI release before NPC recovery; never reset indices."""
import hashlib,shutil,uuid,copy,re
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from npc_recheck import selected


def main():
    q='qa/npc-recheck';assert not (W/q/'baseline.json').exists()
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);snap=W/q/'revisions'/uuid.uuid4().hex
    for rel in [ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json','tools/audit_shared_dialogs.py']:
        dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dest)
    write(q+'/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    rows=[];ts=[];ix={};corpus=read('reference/rebirth-jp-corpus.json')
    for a,d in corpus.items():
        rel='End/Content/Text/JP/'+a;us=None
        for k,v in d.items():
            family=selected(a,k)
            if not family or not v['Text']:continue
            if us is None:us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
            r=dict(asset=rel,id=k,family=family,Japanese=v,English=us.get(k,{}),mode='existing' if k in base['assets'].get(rel,{}).get('entries',{}) else 'translate')
            if r['mode']=='translate':
                # Do not automatically reuse first-person/character-specific dialogue.
                token=v['Text']
                if token not in ix:ix[token]=len(ts);ts.append(dict(index=len(ts),jp=token,us=us.get(k,{}).get('Text',''),examples=[],actors=[]))
                i=ix[token];r['template']=i;ts[i]['examples'].append(k)
                actor=us.get(k,{}).get('MetaData',{}).get('ACTOR','')
                if actor not in ts[i]['actors']:ts[i]['actors'].append(actor)
            rows.append(r)
    write('reference/npc-recheck-source.json',rows);write('reference/npc-recheck-templates.json',ts)
    stage='staging/ThaiJP_NPC_Recheck_Working';shutil.copytree(W/ctx['stage'],W/stage)
    shutil.copy2(W/ctx['cluster_map'],W/'reference/npc-recheck-cluster-map.json')
    shutil.copy2(W/'qa/choice-completion/build-verification.json',W/q/'build-verification.json')
    write('reference/npc-recheck-build.json',dict(chapters=list(range(1,10)),source='translations/working-npc-recheck-th.json',stage=stage,qa=q,cluster_map='reference/npc-recheck-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json'))
    print('NPC inventory',len(rows),Counter(r['mode'] for r in rows),'templates',len(ts),Counter(r['family'] for r in rows if r['mode']=='translate'))


if __name__=='__main__':main()
