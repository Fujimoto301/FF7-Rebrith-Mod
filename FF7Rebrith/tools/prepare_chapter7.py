"""Inventory Chapter7 Corel mountain, North Corel, coastal odd jobs and shared choices."""
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
    return (asset=='8300-CORLE_TxtRes.uasset' and k.startswith(('$C2510_','$C2520_','$CORLV_NPC_10_','$CORLM_BOS_07_','$CORLM_BOS_08_','$CORLE_QST_01_','$CORLE_QST_02_','$CORLE_QST_03_','$CORLE_QST_04_'))) or (asset=='Resident_TxtRes.uasset' and k.startswith(('$CARDG_QST_02_',)))

def main():
    assert not (W/'reference/chapter7-source.json').exists(),'Stable indices already prepared'
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-ch1-6-recheck-th.json')
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
    write('reference/chapter7-source.json',rows);write('reference/chapter7-templates.json',templates)
    write('reference/chapter7-scope.json',dict(chapter=7,title='Those Left Behind',records=len(rows),templates=len(templates),already_translated=already,
        source_sha256=hashlib.sha256((W/'reference/chapter7-source.json').read_bytes()).hexdigest(),
        scope='Corel mountain climb, Turks, Yuffie mine adventure, North Corel and ropeway departure; coastal quests1–3 and Dr.Sheiran quest4 plus North Corel NPCs and Navalan QB. Later-return branches inventoried for individual deferral.',
        excluded='Gold Saucer arrival begins Chapter8; desert odd jobs5/6, Johnny crown/renovation endgame and later North Corel NPC states remain deferred. Preserve Ch.1–6 and all shared UI rechecks.',
        counts=dict(collections.Counter(r['asset'] for r in rows)),reuse_policy='Exact JP matches from previously translated dialogue, unique Thai wording, no gendered particles/pronouns or English names. Recheck context before assembly.'))
    write('translations/chapter7/reused-lines.json',reused)
    run=W/'qa/chapter7/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ['translations/working-ch1-6-recheck-th.json','reference/ch1-6-recheck-cluster-map.json','qa/ch1-6-recheck/working-assets.json','qa/final-parts/latest.json','qa/active-working-set.json']:
        dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    write('qa/chapter7/baseline.json',dict(backup=str(run),base_source=str(run/'translations/working-ch1-6-recheck-th.json'),
        previous_assets=str(run/'qa/ch1-6-recheck/working-assets.json'),protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    print(len(rows),'new records;',len(templates),'unique templates;',len(reused),'exact neutral reuses;',len(already),'prior records retained')
if __name__=='__main__':main()
