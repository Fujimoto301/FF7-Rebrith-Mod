"""Inventory Chapter5 ship story, tournament, boss and ambient NPCs."""
import collections,hashlib,json,re,shutil,sys,uuid
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
from assemble_ui_completion import fingerprint
def read(p):return json.loads((W/p).read_text('utf-8'))
def write(p,v):
    p=W/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')

def in_scope(asset,k):
    return asset=='8200-JUNOE_TxtRes.uasset' and k.startswith(('$C2310_','$C2320_','$FERRY_NPC_10_','$FERRY_BOS_05_'))

def main():
    assert not (W/'reference/chapter5-source.json').exists(),'Stable indices already prepared'
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-through-chapter4-th.json')
    rows=[];reused={};by_jp=collections.defaultdict(set)
    for a,p in base['assets'].items():
        for k,t in p['entries'].items():
            src=c[Path(a).name][k]
            if (src.get('MetaData',{}).get('ACTOR') or k.startswith('$C')) and not re.search(r'ครับ|ค่ะ|คะ|ผม|ดิฉัน|\b[A-Za-z]{2,}\b',t):by_jp[src['Text']].add(t)
    templates=[];indices={};already=[]
    for asset,d in c.items():
        wanted=[(k,v) for k,v in d.items() if v['Text'] and in_scope(asset,k)]
        if not wanted:continue
        rel='End/Content/Text/JP/'+asset;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v in wanted:
            if k in base['assets'].get(rel,{}).get('entries',{}):already.append(dict(asset=rel,id=k));continue
            text=v['Text']
            if text not in indices:
                index=len(templates);indices[text]=index
                templates.append(dict(index=index,jp=text,examples=[],actors=[]))
                if len(by_jp[text])==1:reused[str(index)]=next(iter(by_jp[text]))
            template=indices[text];entry=templates[template]
            actor=us.get(k,{}).get('MetaData',{}).get('ACTOR','')
            if actor not in entry['actors']:entry['actors'].append(actor)
            entry['examples'].append(k)
            rows.append(dict(index=len(rows),id=k,asset=rel,Text=text,MetaData=v.get('MetaData',{}),English=us.get(k,{}),template=template))
    write('reference/chapter5-source.json',rows);write('reference/chapter5-templates.json',templates)
    write('reference/chapter5-scope.json',dict(chapter=5,title='Blood in the Water',records=len(rows),templates=len(templates),already_translated=already,
        source_sha256=hashlib.sha256((W/'reference/chapter5-source.json').read_bytes()).hexdigest(),
        scope='Shinra-8 voyage, all Queen’s Blood tournament dialogue/branches, ship emergency/Jenova story and battle dialogue, all ferry phase-10 NPC speech including actorless ambient lines.',
        excluded='Costa del Sol landing and later regional content begin Chapter6. Shared Resident item/magic effects are already in the all-game UI/inventory release, not new dialogue.',
        counts=dict(collections.Counter(r['asset'] for r in rows)),reuse_policy='Exact JP matches from previously translated dialogue, unique Thai wording, no gendered particles/pronouns or English names. Recheck context before assembly.'))
    write('translations/chapter5/reused-lines.json',reused)
    run=W/'qa/chapter5/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ['translations/working-through-chapter4-th.json','reference/through-chapter4-cluster-map.json','qa/chapter4/working-assets.json','qa/final-parts/latest.json','qa/active-working-set.json']:
        dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    write('qa/chapter5/baseline.json',dict(backup=str(run),base_source=str(run/'translations/working-through-chapter4-th.json'),
        previous_assets=str(run/'qa/chapter4/working-assets.json'),protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    print(len(rows),'new records;',len(templates),'unique templates;',len(reused),'exact neutral reuses;',len(already),'prior records retained')
if __name__=='__main__':main()
