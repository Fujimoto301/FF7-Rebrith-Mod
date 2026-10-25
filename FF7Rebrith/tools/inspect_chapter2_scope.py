import json,re,collections
from pathlib import Path
p=Path('FF7Rebrith')
c=json.loads((p/'reference/rebirth-jp-corpus.json').read_text('utf-8'))
for a,d in c.items():
 if 'GRASE' not in a and 'Resident' not in a: continue
 print('\nASSET',a)
 groups=collections.defaultdict(list)
 for k,v in d.items():
  if v['Text'] and (k.startswith(('$GRASE_','$KALMT_','$CHADL_','$mv','$C1920_','$C2010_','$SWAMP_'))):
   g='_'.join(k.split('_')[:3]);groups[g].append((k,v))
 for g,rs in groups.items():
  print(g,len(rs))
  if g.startswith(('$KALMT','$GRASE','$CHADL')):
   for k,v in (rs[:2]+rs[-2:]):print(k,v.get('MetaData',{}).get('ACTOR'),v['Text'].replace('\r\n',' / '))
  elif g.startswith('$mv'):
   for k,v in rs:print(k,v['Text'].replace('\r\n',' / '))
