"""Read and save reviewed UI translation batches with stable template indices."""
import json,re,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1]
rows=json.loads((W/'reference/ui-completion-templates.json').read_text('utf-8'))
if sys.argv[1]=='show':
 source=json.loads((W/'reference/ui-completion-source.json').read_text('utf-8'))
 needed={r['template'] for r in source if r['mode']=='manual'}
 for r in rows[int(sys.argv[2]):int(sys.argv[3])]:
  if r['index'] not in needed:continue
  print(r['index'],r['jp'].replace('\r\n',' / '))
  if '--en' in sys.argv:print(' EN:',r['en'].replace('\r\n',' / '))
else:
 raw=sys.stdin.read();p=W/'translations/ui-completion'/sys.argv[2];p.parent.mkdir(parents=True,exist_ok=True)
 rawpath=W/'qa/ui-completion/batch-inputs'/sys.argv[2];rawpath.parent.mkdir(parents=True,exist_ok=True)
 rawpath.write_text(raw,'utf-8')
 out={}
 for line in raw.splitlines():
  if not line.strip():continue
  n,t=line.split('|',1);n=int(n);t=t.replace('\\n','\r\n');src=rows[n]['jp']
  assert str(n) not in out and t.strip(),n
  tokens=lambda s:sorted(re.findall(r'<[^>]+>|\{n\d+\}',s))
  assert tokens(src)==tokens(t),(n,tokens(src),tokens(t))
  assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t),n
  out[str(n)]=t
 assert not p.exists(),p
 p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
 print('Saved',p.name,len(out))
