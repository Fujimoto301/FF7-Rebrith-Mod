"""Inventory whole UI families shown in the user's screenshots, excluding speech."""
import json,re,sys,unicodedata,collections,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
R='End/Content/Text/JP/Resident_TxtRes.uasset'
def read(p):return json.loads((W/p).read_text('utf-8'))
def write(p,v):
 p=W/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def category(k):
 if k.startswith('$menu_options_'):return 'settings'
 if k.startswith(('$menu_Manual_','$menu_Tutorial_','$menu_tutorial_','$tutorial_')):return 'manuals_and_tutorials'
 if k.startswith(('$Item_E_','$Item_W_')) and 'help' in k:return 'equipment_lore'
 if k.startswith('$status_'):return 'status'
 if k.startswith('$help_'):return 'menu_help'
 if k.startswith(('$menu_DlcMenu_','$menu_keyguide_','$menu_button_')):return 'menu_navigation'
 if k.startswith(('$menu_camera_','$Photograph_')):return 'photo_mode'
 if k.startswith('$chapter_') or (k.startswith('$str') and re.search(r'Parent$|_Chapter$',k)):return 'chapter_labels'
 if k.startswith('$cutscene_') or k.startswith('$lvl_time_'):return 'temporal_captions'
 if k.startswith('$str'):return 'story_objectives'
 if k.startswith('$checkpoint'):return 'checkpoints'
 if re.match(r'^\$(?:map\d|area\d)',k) or k.startswith(('$hub_','$lvl_Location_','$lvl_loc_','$lvl_loctitle_')) or k=='$map_Midgar':return 'locations'
 if k.startswith(('$level_','$lvl_')):return 'field_prompts'
 return None
def normalized(t):
 t=re.sub(r'<[^>]*>|[^<]+',lambda m:m[0] if m[0].startswith('<') else unicodedata.normalize('NFKC',m[0]),t)
 ns=[]
 def rep(m):
  if m[0].startswith('<'):return m[0]
  ns.append(m[0]);return '{n'+str(len(ns)-1)+'}'
 return re.sub(r'<[^>]*>|\d+(?:[.,]\d+)*',rep,t),ns
def main():
 assert not (W/'reference/ui-completion-source.json').exists(),'Keep stable indices; do not regenerate over translations.'
 j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
 old=read('translations/working-inventory-th.json')['assets'][R]['entries']
 reuse={}
 for p in ['translations/inventory-th.json','translations/menu-th.json']:
  for k,t in read(p)['assets'][R]['entries'].items():reuse.setdefault(j[k]['Text'],t)
 rows=[];templates=[];bytext={};automatic={};preserved={};excluded=[]
 for k,v in j.items():
  c=category(k);t=v['Text']
  if not c or not t:continue
  if v.get('MetaData',{}).get('ACTOR'):excluded.append(k);continue
  en=u.get(k,{}).get('Text','')
  if k in old:preserved[k]=old[k];continue
  mode='manual'
  if c=='chapter_labels':mode='english'
  if c=='locations' and not k.endswith('_help'):mode='english'
  if not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t):mode='unchanged'
  if t in reuse:mode='reuse'
  row=dict(index=len(rows),id=k,asset=R,category=c,jp=t,en=en,mode=mode)
  if mode=='english':
   assert en.strip(),k;automatic[k]=en
  elif mode=='unchanged':automatic[k]=t
  elif mode=='reuse':automatic[k]=reuse[t]
  else:
   nt,ns=normalized(t)
   if nt not in bytext:
    bytext[nt]=len(templates);templates.append(dict(index=len(templates),jp=nt,en=en,category=c,ids=[]))
   n=bytext[nt];templates[n]['ids'].append(k);row.update(template=n,numbers=ns)
  rows.append(row)
 write('reference/ui-completion-source.json',rows);write('reference/ui-completion-templates.json',templates)
 write('reference/ui-completion-scope.json',dict(asset=R,selected_ids=[r['id'] for r in rows],automatic=automatic,previously_translated=preserved,excluded_actor_records=excluded,enemy_names_deferred=True,chapter_titles_english=True,temporal_captions_thai=True,source_sha256=hashlib.sha256((W/'source'/R).read_bytes()).hexdigest()))
 print('New records',len(rows),'manual templates',len(templates),'automatic',len(automatic),'prior',len(preserved))
 print(collections.Counter(r['category'] for r in rows))
 print('Manual JP chars',sum(len(r['jp']) for r in templates))
if __name__=='__main__':main()
