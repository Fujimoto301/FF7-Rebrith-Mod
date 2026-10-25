import sys,json
from prepare_chapter8 import read,write,W
rows=read('reference/chapter8-supplement-templates.json')
selected={r['template'] for r in read('reference/chapter8-supplement-source.json') if 'template' in r}
p='translations/chapter8-supplement-manual.json';done=read(p) if (W/p).exists() else {}
if sys.argv[1]=='show':
 for r in rows[int(sys.argv[2]):int(sys.argv[3])]:
  if r['index'] in selected and str(r['index']) not in done:print(str(r['index'])+'|'+','.join(r['actors'])+'|'+r['jp'].replace('\r\n',' / '))
elif sys.argv[1]=='save':
 for line in sys.stdin.read().splitlines():
  if not line.strip():continue
  k,v=line.split('|',1);assert k.isdigit() and k not in done,k;done[k]=v.replace('\\n','\r\n')
 write(p,done);print('manual',len(done))
