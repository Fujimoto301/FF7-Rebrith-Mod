"""Inventory Chapter6 ship story, tournament, boss and ambient NPCs."""
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
    return (asset=='8300-CORLE_TxtRes.uasset' and k.startswith(('$C2410_','$COSTT_NPC_10_','$COSTT_BOS_06_','$COSTT_QST_'))) or (asset=='Resident_TxtRes.uasset' and k.startswith('$CARDG_QST_11_'))

def main():
    assert not (W/'reference/chapter6-source.json').exists(),'Stable indices already prepared'
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-through-chapter5-th.json')
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
    write('reference/chapter6-source.json',rows);write('reference/chapter6-templates.json',templates)
    write('reference/chapter6-scope.json',dict(chapter=6,title='Fool’s Paradise',records=len(rows),templates=len(templates),already_translated=already,
        source_sha256=hashlib.sha256((W/'reference/chapter6-source.json').read_bytes()).hexdigest(),
        scope='Costa del Sol arrival, Amor del Amor activities, Hojo battle, beach relationship branches, Yuffie joining; Costa NPCs, activity dialogue and local Queen’s Blood. Later unlocked states are prepared but deferred after content review.',
        excluded='Corel mountain story and regional odd jobs begin Chapter7; later-return unlocks are deferred. Preserve Ch.1–5 and existing UI.',
        counts=dict(collections.Counter(r['asset'] for r in rows)),reuse_policy='Exact JP matches from previously translated dialogue, unique Thai wording, no gendered particles/pronouns or English names. Recheck context before assembly.'))
    write('translations/chapter6/reused-lines.json',reused)
    run=W/'qa/chapter6/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ['translations/working-through-chapter5-th.json','reference/through-chapter5-cluster-map.json','qa/chapter5/working-assets.json','qa/final-parts/latest.json','qa/active-working-set.json']:
        dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    write('qa/chapter6/baseline.json',dict(backup=str(run),base_source=str(run/'translations/working-through-chapter5-th.json'),
        previous_assets=str(run/'qa/chapter5/working-assets.json'),protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    print(len(rows),'new records;',len(templates),'unique templates;',len(reused),'exact neutral reuses;',len(already),'prior records retained')
if __name__=='__main__':main()
