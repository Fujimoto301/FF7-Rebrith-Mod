"""Compile reviewed all-game menu effects; keep menu names in official English."""
import collections, copy, hashlib, json, re, sys
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'tools/cutscene-tool/1.0'))
import txtres
R='End/Content/Text/JP/Resident_TxtRes.uasset'
def read(p):return json.loads((W/p).read_text('utf-8'))
def write(p,v):
    path=W/p;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
def tags(t):return re.findall(r'<[^>]+>',t)
def is_name(k,j):
    if 'help' in k or 'Detail' in k:return False
    if k.startswith(('$Item_','$item_','$M_','$PC','$SU','$Chain','$EleBurst')):return True
    if re.match(r'^\$(?:it_|key_|keyitem_).+',k):return k+'_help' in j
    if k.startswith('$BattleSkill_'):return 'Layout' not in k
    if k.startswith(('$menu_EquipmentSkill_name_','$menu_WeaponUpgrade_Core_name_','$menu_WeaponUpgrade_skill_')):return True
    if re.match(r'^\$ChocoboRaceAbility_\d+$',k):return True
    if k.startswith(('$minigame_ChocoboRace_PartsSkill_Name_','$cardtext_card_name_')):return True
    if k.startswith(('$CF_','$GF_','$GC_')):return k+'_help' in j
    if k.startswith('$bt_'):return k+'_help' in j
    return False
def english_name(k,jp,en):
    # Two legacy US labels use a misspelled count tag; retain the JP contract.
    en=en.replace('<count-0>','<count=0>')
    if tags(en)==tags(jp):return en
    # Name decoration differs by locale. Preserve JP style/control tags exactly.
    jt=tags(jp);et=tags(en)
    if all(re.fullmatch(r'</?(?:color|i|b)(?:=[^>]+)?>',t) for t in jt+et):
        text=re.sub(r'<[^>]+>','',en)
        opening=[t for t in jt if not t.startswith('</')]
        closing=[t for t in jt if t.startswith('</')]
        return ''.join(opening)+text+''.join(closing)
    if not jt and all(t=='<nbsp>' for t in et):return en.replace('<nbsp>','')
    raise AssertionError(('Unreviewed name tag difference',k,jp,en))
def main():
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    u=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    src=read('reference/inventory-source.json');ts=read('reference/inventory-templates.json')
    translated={}
    for p in sorted((W/'translations/inventory').glob('batch-*.json')):
        for n,t in json.loads(p.read_text('utf-8')).items():
            assert n not in translated,('Duplicate template',n)
            translated[n]=t
    entries={};descriptions=[];names=[]
    for row in src:
        ids=[k for k in row['ids'] if not is_name(k,j)]
        if not ids:continue
        n=row['template'];assert str(n) in translated,('Missing translation',n)
        t=translated[str(n)]
        assert sorted(tags(t))==sorted(tags(ts[n]['jp'])),n
        if n!=1311:
            assert sorted(re.findall(r'\{n\d+\}',t))==sorted(re.findall(r'\{n\d+\}',ts[n]['jp'])),n
        else:
            # JP names Moogle Trio No.1/2 are Moogle Mage/Bard in US.
            assert 'Moogle Mage' in t and 'Moogle Bard' in t
        for i,num in enumerate(row['numbers']):t=t.replace('{n'+str(i)+'}',num)
        assert not re.search(r'\{n\d+\}|[\u3040-\u30ff\u3400-\u9fff]',t),n
        assert t.strip(),n
        for k in ids:
            assert k not in entries,k
            assert sorted(tags(t))==sorted(tags(j[k]['Text'])),k
            entries[k]=t;descriptions.append(k)
    for k,v in j.items():
        if not v['Text'] or not is_name(k,j):continue
        en=u.get(k,{}).get('Text','');assert en.strip(),('Missing US name',k)
        t=english_name(k,v['Text'],en)
        assert tags(t)==tags(v['Text']),(k,'Name tags changed')
        assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t),k
        assert k not in entries,k
        entries[k]=t;names.append(k)
    base=read('translations/working-through-chapter2-th.json')
    combined=copy.deepcopy(base)
    combined['scope']='Chapters 1–2, existing menus, all-game item/skill menu effects; source/working assets only'
    combined['assets'][R]['entries'].update(entries)
    combined['inventory_description_records']=len(descriptions)
    combined['inventory_english_name_records']=len(names)
    inventory={'scope':'All-game item/skill menu effects with official English names','assets':{R:{'entries':entries,'actors':{}}}}
    write('translations/inventory-th.json',inventory)
    write('translations/working-inventory-th.json',combined)
    scope={'asset':R,'source_sha256':hashlib.sha256((W/'source'/R).read_bytes()).hexdigest(),
           'descriptions':descriptions,'english_names':names,
           'description_groups':dict(collections.Counter('_'.join(k.split('_')[:2]) if k.startswith('$menu_') else k.split('_')[0] for k in descriptions)),
           'excluded':'Unrelated narrative, quest-only key-item flavor, equipment lore, enemy encyclopedia, general tutorials/settings. Actual equipment effects are included through EQSkill/EquipmentSkill/WeaponUpgrade.',
           'name_tag_exceptions':[k for k in names if tags(u[k]['Text'])!=tags(j[k]['Text'])]}
    write('reference/inventory-scope.json',scope)
    write('qa/inventory/assembly.json',{'description_records':len(descriptions),'english_name_records':len(names),'manual_templates':len(translated),'total_combined_text_records':sum(len(a['entries']) for a in combined['assets'].values()),'runtime_tested':False,'installed':False})
    print('Compiled',len(descriptions),'descriptions and',len(names),'official English names')
if __name__=='__main__':main()
