"""Append neighbouring categories discovered during independent completeness search."""
import hashlib
from prepare_chapter9 import *

def main():
    rows=read('reference/chapter9-source.json');ts=read('reference/chapter9-templates.json');existing={(r['asset'],r['id']) for r in rows};reuse=read('translations/chapter9/reused-lines.json');base=read('translations/working-through-chapter8-th.json');ix={(t['group'],t['jp']):t['index'] for t in ts}
    rel='End/Content/Text/JP/Resident_TxtRes.uasset';c=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
    added=[]
    for k,v in c.items():
        if not v['Text'] or (rel,k) in existing or k in base['assets'][rel]['entries'] or not (shared(k) or ui(k)):continue
        group='UI' if ui(k) else 'speech';key=(group,v['Text'])
        if key not in ix:
            i=len(ts);ix[key]=i;ts.append(dict(index=i,jp=v['Text'],us=us.get(k,{}).get('Text',''),group=group,examples=[],actors=[]))
            if group=='UI' and (ui(k)=='Gongaga_shop_UI' or k.startswith('$key_qst') and not k.endswith('_help') or k.endswith('_Title') or not re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text'])):reuse[str(i)]=us[k]['Text'] if re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']) else v['Text']
        i=ix[key];ts[i]['examples'].append(k);actor=us[k].get('MetaData',{}).get('ACTOR','')
        if actor not in ts[i]['actors']:ts[i]['actors'].append(actor)
        row=dict(asset=rel,id=k,Japanese=v,English=us[k],template=i,group=group,reason=None);rows.append(row);added.append(k)
    for r in rows:r['reason']=defer(r['id'])
    write('reference/chapter9-source.json',rows);write('reference/chapter9-templates.json',ts);write('reference/chapter9-deferred.json',[r for r in rows if r['reason']]);write('translations/chapter9/reused-lines.json',reuse)
    scope=read('reference/chapter9-scope.json');scope.update(source_sha256=hashlib.sha256((W/'reference/chapter9-source.json').read_bytes()).hexdigest(),records=len(rows),templates=len(ts),selected=sum(not r['reason'] for r in rows),deferred=sum(bool(r['reason']) for r in rows),groups=dict(Counter(r['group'] for r in rows if not r['reason'])));write('reference/chapter9-scope.json',scope)
    write('qa/chapter9/adjacent-additions.json',added);print(scope)

if __name__=='__main__':main()
