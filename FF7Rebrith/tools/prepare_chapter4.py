"""Inventory Junon story, ambient NPCs and initial regional side content."""
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
    if asset=='8200-JUNOE_TxtRes.uasset':
        if k.startswith(('$C2110_MAIN_3800_','$C2110_MAIN_3900_','$C2110_MAIN_4000_','$C2120_','$C2210_',
            '$JNONT_NPC_10_','$JNONV_NPC_10_','$JUNOA_NPC_10_','$CHADL_QST_02_','$JUNOV_BOS_04_')):return True
        if any(k.startswith(f'$JUNOE_QST_{i:02d}_') for i in range(1,6)):return True
    if asset=='Resident_TxtRes.uasset':
        if k.startswith(('$CHADL_QST_02_','$CARDG_QST_09_','$CARDG_QST_10_','$WORLD_CDV_02_0300_','$WORLD_MGV_01_0300_','$MOGLE_QST_01_1100_')):return True
        m=re.match(r'\$WORLD_CDV_01_0100_(\d+)_',k)
        if m and (3300<=int(m[1])<=5900 or 19900<=int(m[1])<=20300 or 25700<=int(m[1])<=25900):return True
        if re.match(r'\$WORLD_CDV_01_0300_0[456]00_',k):return True
        if re.match(r'\$WORLD_CDV_02_0100_(?:5200|5300|5310)_',k):return True
        if re.match(r'\$WORLD_CDV_03_0100_0[1-7]00_',k):return True
    return False

def main():
    assert not (W/'reference/chapter4-source.json').exists(),'Stable indices already prepared'
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-through-chapter3-th.json')
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
    write('reference/chapter4-source.json',rows);write('reference/chapter4-templates.json',templates)
    write('reference/chapter4-scope.json',dict(chapter=4,title='Dawn of a New Era',records=len(rows),templates=len(templates),already_translated=already,
        source_sha256=hashlib.sha256((W/'reference/chapter4-source.json').read_bytes()).hexdigest(),
        scope='Junon approach, Under Junon and parade main story, all phase-10 Junon NPC speech including actorless ambient lines, five initial odd jobs, Fort Condor protorelic, Terror of the Deep battle, local Queen’s Blood, Junon Chadley/MAI and second Moogle shop.',
        excluded='C2310/C2320 and ferry dialogue are Chapter5; JUNOE_QST06/07 are later return quests; later named-region research remains outside this chapter.',
        counts=dict(collections.Counter(r['asset'] for r in rows)),reuse_policy='Exact JP matches from previously translated dialogue, unique Thai wording, no gendered particles/pronouns or English names. Recheck context before assembly.'))
    write('translations/chapter4/reused-lines.json',reused)
    run=W/'qa/chapter4/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ['translations/working-through-chapter3-th.json','reference/through-chapter3-cluster-map.json','qa/chapter3/working-assets.json','qa/final-parts/latest.json','qa/active-working-set.json']:
        dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    write('qa/chapter4/baseline.json',dict(backup=str(run),base_source=str(run/'translations/working-through-chapter3-th.json'),
        previous_assets=str(run/'qa/chapter3/working-assets.json'),protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    print(len(rows),'new records;',len(templates),'unique templates;',len(reused),'exact neutral reuses;',len(already),'prior records retained')
if __name__=='__main__':main()
