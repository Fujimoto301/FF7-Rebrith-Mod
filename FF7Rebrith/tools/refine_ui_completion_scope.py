"""Annotate shared location names and temporal exceptions; never renumber."""
import json,re,collections
from create_ui_completion_scope import W,read,write
def main():
 rows=read('reference/ui-completion-source.json');scope=read('reference/ui-completion-scope.json')
 names=collections.defaultdict(collections.Counter)
 for r in rows:
  if r['category']=='locations' and r['mode']=='english':names[r['jp']][r['en']]+=1
 temporal=re.compile(r'^(?:[0-9０-９一二三四五六七八九十]+年前|現在|翌日|数刻前|数日前|数時間前|数週間前|数年後)$')
 changed=[]
 for r in rows:
  k=r['id'];t=r['jp']
  if temporal.fullmatch(t):
   if r['mode']=='english':
    # These exceptions were selected as location labels but contain only time.
    r['mode']='temporal_override';scope['automatic'].pop(k,None)
    changed.append({'id':k,'mode':'temporal_override','jp':t})
   continue
  if r['category']=='field_prompts' and (t in names or k.startswith('$level_3110_TEMPL_')):
   assert r['en'].strip(),k
   r['mode']='english';scope['automatic'][k]=r['en'];changed.append({'id':k,'mode':'english','jp':t,'en':r['en']})
 scope['temporal_overrides']={r['id']:r['jp'] for r in rows if r['mode']=='temporal_override'}
 write('reference/ui-completion-source.json',rows);write('reference/ui-completion-scope.json',scope)
 write('qa/ui-completion/shared-location-and-time-review.json',changed)
 print('Refined',len(changed),'shared labels; temporal exceptions:',scope['temporal_overrides'])
if __name__=='__main__':main()
