import json,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1]
rows=json.loads((W/'reference/chapter8-templates.json').read_text('utf-8'))
deferred={d['id'] for d in json.loads((W/'reference/chapter8-deferred.json').read_text('utf-8'))}
selected={r['template'] for r in json.loads((W/'reference/chapter8-source.json').read_text('utf-8')) if r['id'] not in deferred}
done={}
for p in (W/'translations/chapter8').glob('*.json'):done.update(json.loads(p.read_text('utf-8')))
if sys.argv[1]=='show':
    for r in rows[int(sys.argv[2]):int(sys.argv[3])]:
        if str(r['index']) in done or r['index'] not in selected:continue
        print(str(r['index'])+'|'+','.join(r['actors'])+'|'+r['jp'].replace('\r\n',' / '))
elif sys.argv[1]=='save':
    p=W/'translations/chapter8'/sys.argv[2];out={}
    for line in sys.stdin.read().splitlines():
        if not line.strip():continue
        k,v=line.split('|',1);assert k.isdigit() and k not in out and k not in done,k
        out[k]=v.replace('\\n','\r\n')
    assert not p.exists(),p
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8');print('Saved',p.name,len(out))

