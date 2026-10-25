"""Freeze the current enemy-action/NPC corrected base and inventory Chapter10."""
import collections,hashlib,re,shutil,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter10_scope import primary,shared,defer


def main():
    assert not (W/'reference/chapter10-source.json').exists(),'Immutable indices already exist'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);corpus=read('reference/rebirth-jp-corpus.json')
    snap=W/'qa/chapter10/revisions'/uuid.uuid4().hex
    for rel in [ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json']:
        p=snap/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
    write('qa/chapter10/baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    byjp=collections.defaultdict(set)
    for a,p in base['assets'].items():
        for k,t in p['entries'].items():
            j=corpus[Path(a).name][k];actor=re.sub('<[^>]+>','',p['actors'].get(k,''))
            byjp[(j['Text'],actor)].add(t)
    rows=[];ts=[];ix={};reuse={};deferred=[]
    for a,d in corpus.items():
        candidates=[(k,v) for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and shared(k))]
        if not candidates:continue
        rel='End/Content/Text/JP/'+a;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v in candidates:
            if k in base['assets'].get(rel,{}).get('entries',{}):continue
            row=dict(asset=rel,id=k,Japanese=v,English=us.get(k,{}),reason=defer(k))
            if row['reason']:deferred.append(row);continue
            actor=re.sub('<[^>]+>','',us.get(k,{}).get('MetaData',{}).get('ACTOR',''));token=(v['Text'],actor)
            if token not in ix:
                i=len(ts);ix[token]=i;ts.append(dict(index=i,jp=v['Text'],us=us.get(k,{}).get('Text',''),actor=actor,examples=[]))
                # Same exact JP AND actor with a unique reviewed translation only.
                if len(byjp[token])==1:reuse[str(i)]=next(iter(byjp[token]))
            i=ix[token];ts[i]['examples'].append(k);row['template']=i;rows.append(row)
    write('reference/chapter10-source.json',rows);write('reference/chapter10-templates.json',ts);write('reference/chapter10-deferred.json',deferred)
    write('translations/chapter10/reused-lines.json',reuse)
    write('reference/chapter10-scope.json',dict(records=len(rows),templates=len(ts),reused_templates=len(reuse),deferred=len(deferred),assets=dict(collections.Counter(r['asset'] for r in rows)),source_sha256=hashlib.sha256((W/'reference/chapter10-source.json').read_bytes()).hexdigest()))
    cfg=dict(chapters=list(range(1,11)),source='translations/working-through-chapter10-th.json',stage='staging/ThaiJP_ThroughChapter10_Working',qa='qa/chapter10',cluster_map='reference/through-chapter10-cluster-map.json',seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json')
    write('reference/chapter10-build.json',cfg);shutil.copytree(W/ctx['stage'],W/cfg['stage'])
    print(read('reference/chapter10-scope.json'))
    print('First unreviewed templates:')
    for t in ts[:130]:
        if str(t['index']) not in reuse:print(t['index'],t['actor'],t['jp'].replace('\r\n',' / '))


if __name__=='__main__':main()
