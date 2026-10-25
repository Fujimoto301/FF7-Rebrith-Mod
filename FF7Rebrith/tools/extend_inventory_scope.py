"""Append reviewed all-game utility/minigame skill groups without renumbering."""
import json, re, sys, unicodedata
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
j=json.loads((W/'reference/rebirth-jp-corpus.json').read_text('utf-8'))['Resident_TxtRes.uasset']
u=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
src=json.loads((W/'reference/inventory-source.json').read_text('utf-8'))
ts=json.loads((W/'reference/inventory-templates.json').read_text('utf-8'))
known={i for r in src for i in r['ids']}; byjp={r['jp']:r for r in src}; templates={r['jp']:r['index'] for r in ts}
def normalize(t):
    t=re.sub(r'<[^>]*>|[^<]+',lambda m:m[0] if m[0].startswith('<') else unicodedata.normalize('NFKC',m[0]),t)
    ns=[]
    def replace(m):
        if m[0].startswith('<'):return m[0]
        ns.append(m[0]);return '{n'+str(len(ns)-1)+'}'
    return re.sub(r'<[^>]*>|\d+(?:[.,]\d+)*',replace,t),ns
for k,v in j.items():
    if k in known or not v['Text']:continue
    include=(k.startswith(('$CF_','$GF_','$GC_','$bt_','$key_skillPointAdd_','$key_recipebook_')) and 'help' in k)
    include|=k.startswith(('$ChocoboRaceAbility_','$minigame_ChocoboRace_PartsSkill_Detail_')) and ('Detail' in k)
    include|=k.startswith('$cardtext_card_')
    include|=k.startswith('$keyitem_SkillBook_') and k.endswith('_help')
    include|=k=='$keyitem_ItemCraftSystem_help'
    if not include:continue
    t=v['Text']
    if t in byjp:byjp[t]['ids'].append(k);continue
    nt,ns=normalize(t)
    if nt not in templates:
        n=len(ts);templates[nt]=n;ts.append(dict(index=n,jp=nt,en=u.get(k,{}).get('Text',''),ids=[k]))
    row=dict(index=len(src),ids=[k],jp=t,template=templates[nt],numbers=ns,en=u.get(k,{}).get('Text',''))
    byjp[t]=row;src.append(row)
for name,obj in [('inventory-source',src),('inventory-templates',ts)]:
    (W/f'reference/{name}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Descriptions',sum(len(r['ids']) for r in src),'unique',len(src),'templates',len(ts))
