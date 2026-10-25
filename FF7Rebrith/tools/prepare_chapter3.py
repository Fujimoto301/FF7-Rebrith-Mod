"""Freeze the scene-reviewed Mythril Mine chapter scope and previous release."""
import hashlib,json,shutil,sys,uuid
from collections import Counter
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
from assemble_ui_completion import fingerprint

def write(p,v):
    p=W/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')

def selected(k):
    return k.startswith(('$C2110_','$MYTHM_BOS_')) and not k.startswith(('$C2110_MAIN_3800_','$C2110_MAIN_3900_','$C2110_MAIN_4000_'))

def main():
    assert not (W/'reference/chapter3-source.json').exists(),'Keep stable indices and the original snapshot'
    c=json.loads((W/'reference/rebirth-jp-corpus.json').read_text('utf-8'));rows=[];later=[]
    for a,d in c.items():
        wanted=[(k,v) for k,v in d.items() if v['Text'] and (k.startswith(('$C2110_','$MYTHM_BOS_')))]
        if not wanted:continue
        rel='End/Content/Text/JP/'+a;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v in wanted:
            row=dict(id=k,asset=rel,Text=v['Text'],MetaData=v.get('MetaData',{}),English=us.get(k,{}))
            if selected(k):row['index']=len(rows);rows.append(row)
            else:row['reason']='Post-mine Junon-region approach, Fort Condor follow-up and checkpoint: defer to Chapter 4';later.append(row)
    assert len(rows)==253 and len(later)==14
    write('reference/chapter3-source.json',rows);write('reference/chapter3-deferred.json',later)
    write('reference/chapter3-scope.json',dict(chapter=3,title='Deeper into Darkness',records=len(rows),
        assets=dict(Counter(r['asset'] for r in rows)),
        source_sha256=hashlib.sha256((W/'reference/chapter3-source.json').read_bytes()).hexdigest(),
        selected_prefixes=['$C2110_','$MYTHM_BOS_'],excluded_prefixes=['$C2110_MAIN_3800_','$C2110_MAIN_3900_','$C2110_MAIN_4000_'],
        boundary='Entry, split parties, Turks encounter and all boss battle variants, reunion and mine-exit cinematic C2110_3600. Post-exit regional conversations are deferred, regardless of C2110 ID.',
        ui='Chapter 3 objectives/help/location labels already included in the all-game UI release; preserve them.'))
    run=W/'qa/chapter3/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ['translations/working-ui-completion-th.json','reference/ui-completion-cluster-map.json','qa/ui-completion/working-assets.json','qa/final-parts/latest.json']:
        dst=run/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dst)
    write('qa/chapter3/baseline.json',dict(backup=str(run),base_source=str(run/'translations/working-ui-completion-th.json'),
        previous_assets=str(run/'qa/ui-completion/working-assets.json'),protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    (W/'translations/chapter3').mkdir(parents=True,exist_ok=True)
    print('Prepared 253 Chapter 3 records, 14 post-mine lines deferred; release snapshot saved')

if __name__=='__main__':main()
