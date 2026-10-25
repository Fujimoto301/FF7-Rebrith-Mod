"""Compact source display and persistent translation progress for Chapter14."""
import sys,re
from prepare_chapter9 import W,read,write
Q='qa/chapter14/'
def show(start,end):
    for r in read('reference/chapter14-templates.json')[start:end]:
        print(f"[{r['index']}] {r['actor']} {r['examples'][0]}")
        print('J',r['jp'].replace('\r\n',' / ').replace('\r',' / '));print('U',r['us'].replace('\r\n',' / '))
def progress():
    ts=read('reference/chapter14-templates.json');vals={}
    for p in sorted((W/'translations/chapter14').glob('batch-*.json')):
        v=read(p);assert not vals.keys()&v.keys(),p;vals.update(v)
    assert vals.keys()<={str(t['index']) for t in ts}
    for k,t in vals.items():
        j=ts[int(k)]['jp'];assert t.strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',t),(k,t)
        assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',j),(k,'tags')
        assert not re.search('แอริธ|แซ็ค|นะค่ะ|ไหมค่ะ|เหรอค่ะ',t),(k,t)
    p=read(Q+'progress.json');p.update(translated_templates=len(vals),remaining_templates=len(ts)-len(vals),translated_ranges=sorted(int(k) for k in vals));write(Q+'progress.json',p)
    print('Translated',len(vals),'/',len(ts),'remaining',len(ts)-len(vals))
if __name__=='__main__':
    if sys.argv[1]=='--show':show(int(sys.argv[2]),int(sys.argv[3]))
    elif sys.argv[1]=='--progress':progress()
