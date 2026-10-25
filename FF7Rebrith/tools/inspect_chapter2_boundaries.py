import json,collections
from pathlib import Path
c=json.loads(Path('FF7Rebrith/reference/rebirth-jp-corpus.json').read_text('utf-8'))
d=c['8100-GRASE_TxtRes.uasset']
for pref in ['$GRASE_QST_05_','$CHADL_QST_01_','$C2010_MAIN_','$KALMT_NPC_20_','$KALMT_NPC_30_']:
 print('\nPREFIX',pref)
 gs=collections.defaultdict(list)
 for k,v in d.items():
  if k.startswith(pref) and v['Text']:gs['_'.join(k.split('_')[:4]) if 'QST' in pref or 'NPC' in pref else '_'.join(k.split('_')[:3])].append((k,v))
 for g,rs in gs.items():
  print(g,len(rs))
  for k,v in rs[:2]+rs[-1:]:print(k,v.get('MetaData',{}).get('ACTOR'),v['Text'].replace('\r\n',' / '))
