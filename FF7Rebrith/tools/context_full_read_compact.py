"""Read-only display: exact JP/Thai/actor duplicates share one displayed pair.

Every source ID/index remains visible. This command never records review or
asserts meaning; the editor must inspect the displayed pairs and ID membership.
"""
import json,sys
from collections import OrderedDict
from prepare_chapter9 import read

start,end=map(int,sys.argv[1:3])
rows=read('qa/context-full-read/queue.json')[start:end]
groups=OrderedDict()
for r in rows:
    key=(r['asset'],r['jp'],r['thai'],r['actor'])
    groups.setdefault(key,[]).append(r)
for (asset,jp,thai,actor),members in groups.items():
    print('IDs:', '; '.join(str(r['index'])+' '+r['id'] for r in members))
    print(actor,'|',jp.replace('\r','').replace('\n',' / '),'→',thai.replace('\r','').replace('\n',' / '))
print('Displayed',len(rows),'IDs;',len(groups),'exact JP/Thai/actor pairs. Not automatically recorded.')
