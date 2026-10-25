import json,sys,re,collections,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'));import txtres
C=json.loads((W/'reference/rebirth-jp-corpus.json').read_text('utf-8'))
def scope(k):
 if k.startswith(('$C1920_','$C2010_','$KALMT_NPC_10_','$KALMT_NPC_20_','$GRASA_NPC_10_','$SWAMP_BOS_01_','$CHADL_QST_01_')):return True
 if k.startswith(tuple('$GRASE_QST_%02d_'%n for n in range(1,6))):
  return not(k.startswith('$GRASE_QST_05_') and int(k.split('_')[3])>=1200)
 return False
rows=[]
for a,d in C.items():
 selected=[(k,v) for k,v in d.items() if v['Text'] and scope(k)]
 if not selected:continue
 rel='End/Content/Text/JP/'+a;en=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
 for k,v in selected:rows.append(dict(index=len(rows),id=k,asset=rel,Text=v['Text'],MetaData=v.get('MetaData',{}),English=en.get(k,{})))
f=W/'reference/chapter2-source.json';assert not f.exists();f.write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
(W/'translations/chapter2').mkdir(exist_ok=True)
manifest={'scope':'Chapter 2 main dialogue, Kalm initial/raid NPC phases, five initial Grasslands odd jobs, Grasslands protorelic dialogue and Midgardsormr battle dialogue; includes shared Resident main/protorelic entries','rows':len(rows),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'excluded':{'C2110 and MYTHM':'Chapter 3 Mythril Mine','KALMT_NPC_30':'Later return phase contains Junon ceremony reports','GRASE_QST_06':'Hustle and Grind later quest','GRASE_QST_05 stages1200+':'Later Broden-absent replacement quest dialogue','mv_psbl0_0920':'Remake Intergrade ending recap before Rebirth','generic system and item skill databases':'Unrequested database/UI work; shared voiced C2010 tutorial explanations are included'}}
(W/'reference/chapter2-scope.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2));print(collections.Counter(r['asset'] for r in rows))
