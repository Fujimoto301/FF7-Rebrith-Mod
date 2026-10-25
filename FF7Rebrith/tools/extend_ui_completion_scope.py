"""Append screenshot-related menu families without renumbering reviewed templates."""
import json,re,sys
from pathlib import Path
from create_ui_completion_scope import normalized
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
R='End/Content/Text/JP/Resident_TxtRes.uasset'
def read(p):return json.loads((W/p).read_text('utf-8'))
def write(p,v):(W/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
rows=read('reference/ui-completion-source.json');templates=read('reference/ui-completion-templates.json');scope=read('reference/ui-completion-scope.json')
j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
base=read('translations/working-inventory-th.json')['assets'][R]['entries']
seen={r['id'] for r in rows};bytext={t['jp']:t['index'] for t in templates};added=[]
prefixes=('$mainmenu_','$menu_Libra_','$menu_field_','$menu_FastTravel_','$menu_WM_',
 '$menu_WeaponUpgrade_','$menu_questboard_','$menu_itemcraft_','$menu_pcrein_',
 '$menu_chadleyshop_','$menu_shop_','$menu_partyname_','$menu_navimap_','$menu_mapicon_','$menu_map_')
for k,v in j.items():
 if not k.startswith(prefixes) or k in seen or k in base or not v['Text']:continue
 assert not v.get('MetaData',{}).get('ACTOR'),k
 t=v['Text'];en=u.get(k,{}).get('Text','');mode='manual'
 if k.startswith(('$menu_partyname_','$menu_navimap_')):mode='english'
 if not re.search('[\u3040-\u30ff\u3400-\u9fff]',t):mode='unchanged'
 row=dict(index=len(rows),id=k,asset=R,category='related_menu_completion',jp=t,en=en,mode=mode)
 if mode=='english':
  assert en.strip(),k;scope['automatic'][k]=en
 elif mode=='unchanged':scope['automatic'][k]=t
 else:
  nt,ns=normalized(t)
  if nt not in bytext:
   bytext[nt]=len(templates);templates.append(dict(index=len(templates),jp=nt,en=en,category=row['category'],ids=[]))
  n=bytext[nt];templates[n]['ids'].append(k);row.update(template=n,numbers=ns)
 rows.append(row);seen.add(k);scope['selected_ids'].append(k);added.append(k)
write('reference/ui-completion-source.json',rows);write('reference/ui-completion-templates.json',templates);write('reference/ui-completion-scope.json',scope)
if added:write('qa/ui-completion/menu-family-extension.json',{'families':prefixes,'added_ids':added,'new_record_count':len(added),'templates_total':len(templates),'preserves_existing_indices':True})
print('Appended',len(added),'records; templates',len(templates))
