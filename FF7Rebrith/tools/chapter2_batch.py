import json,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1];R=json.loads((W/'reference/chapter2-source.json').read_text('utf-8'))
if (W/'reference/chapter2-shared-source.json').exists():R+=json.loads((W/'reference/chapter2-shared-source.json').read_text('utf-8'))
if sys.argv[1]=='show':
 for r in R[int(sys.argv[2]):int(sys.argv[3])]:print(str(r['index'])+'|'+str(r['MetaData'].get('ACTOR','-'))+'|'+r['Text'].replace('\r\n',' / ').replace('\n',' / '))
elif sys.argv[1]=='save':
 p=W/'translations/chapter2'/sys.argv[2];out={}
 for line in sys.stdin.read().splitlines():
  if not line.strip():continue
  k,v=line.split('|',1);assert k.isdigit() and k not in out
  out[k]=v.replace('\\n','\r\n')
 assert not p.exists(),p
 p.write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8');print('Saved',p.name,len(out))
