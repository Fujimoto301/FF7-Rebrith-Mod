"""Audit inventory coverage, token/numeric contracts, names, and release protection."""
import collections, hashlib, json, re
from pathlib import Path
import assemble_inventory as a
W=a.W
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def main():
    s=a.read('reference/inventory-scope.json');r=s['asset']
    j=a.read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    u=a.txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    inv=a.read('translations/inventory-th.json')['assets'][r]['entries']
    base=a.read('translations/working-through-chapter2-th.json')
    combined=a.read('translations/working-inventory-th.json')
    assert sha(W/'source'/r)==s['source_sha256'].upper()
    selected=set(s['descriptions']);names=set(s['english_names'])
    assert not selected&names and set(inv)==selected|names
    jpchars=r'[\u3040-\u30ff\u3400-\u9fff]'
    source=a.read('reference/inventory-source.json')
    byid={k:row for row in source for k in row['ids']}
    for k in selected:
        t=inv[k];row=byid[k]
        assert row['jp']==j[k]['Text'],k
        assert t.strip() and not re.search(jpchars,t),k
        assert sorted(a.tags(t))==sorted(a.tags(j[k]['Text'])),k
        assert not re.search(r'\{n\d+\}',t),k
        if row['template']!=1311:
            # Literal numbers are normalized only outside control tags.
            expected=list(row['numbers'])
            added={333:['4'],1424:['1'],1388:['1'],1389:['3'],1390:['5'],1391:['7'],1392:['9'],1393:['11']}
            expected+=added.get(row['template'],[])
            assert collections.Counter(re.findall(r'\d+(?:[.,]\d+)*',re.sub(r'<[^>]+>','',t)))==collections.Counter(expected),k
        else:
            assert 'Moogle Mage' in t and 'Moogle Bard' in t
    for k in names:
        assert inv[k]==a.english_name(k,j[k]['Text'],u[k]['Text']),k
    untouched_prior=0
    for asset,patch in base['assets'].items():
        after=combined['assets'][asset]
        assert patch['actors']==after['actors'],asset
        for k,t in patch['entries'].items():
            if asset==r and k in inv:continue
            assert after['entries'][k]==t,(asset,k)
            untouched_prior+=1
    # Search every parsed asset; combat/menu data must all live in Resident.
    matched=collections.Counter()
    core=('$Item_M_','$item_','$Item_bigBomber','$M_','$PC','$SU','$Chain','$EleBurst','$BattleSkill_','$Materia_Description','$menu_EQSkill_','$menu_EquipmentSkill_help_','$menu_WeaponUpgrade_Core_help_','$menu_WeaponAbility_')
    extra=('$CF_','$GF_','$GC_','$bt_','$key_skillPointAdd_','$key_recipebook_','$keyitem_SkillBook_')
    for asset,d in a.read('reference/rebirth-jp-corpus.json').items():
        for k,v in d.items():
            if not v['Text']:continue
            target=(k.startswith(core) and ('help' in k or k.startswith(('$Materia_Description','$menu_EQSkill_','$menu_WeaponAbility_'))))
            target|=k.startswith(extra) and 'help' in k
            target|=k.startswith(('$ChocoboRaceAbility_','$minigame_ChocoboRace_PartsSkill_Detail_')) and 'Detail' in k
            target|=k.startswith('$cardtext_card_') and not a.is_name(k,j)
            target|=k=='$keyitem_ItemCraftSystem_help'
            if target:
                assert asset=='Resident_TxtRes.uasset' and k in selected,(asset,k,'Missing effect')
                matched[k.split('_')[0]]+=1
    last=a.read('qa/installation-latest.json');protected=[]
    for file in last['files']:
        for path in [Path(file['path']),W/'dist/ThaiJP_Chapter1_P'/file['file'],W/'dist/Chapter1-Test'/file['file']]:
            assert sha(path)==file['sha256'],str(path)
            protected.append({'path':str(path),'sha256':file['sha256']})
    checks={
        '$item_gravity_help':['เหลือ 3 ใน 4 ส่วน','ไม่มีผลกับศัตรูที่แข็งแกร่ง'],
        '$item_atel_help':['MP 20'],
        '$M_MAG_004_atk003_help':['ธาตุไฟ','ATB 2'],
        '$BattleSkill_041_help':['<count=1>%','<count=0>%'],
        '$BattleSkill_128_LastLeave_help':['HP 1','ตั้งแต่ 2','ไม่รวม'],
        '$M_CMD_003_atk003_help':['ตัว','หมดสภาพต่อสู้','ATB 2'],
        '$PC0005_AtkBurst10_help':['United Refocus','ATB 3'],
        '$menu_EQSkill_E_ACC_0008':['Reraise','แตก'],
    }
    samples=[]
    for k,needles in checks.items():
        assert k in inv,k
        for n in needles:assert n in inv[k],(k,n,inv[k])
        samples.append({'id':k,'jp':j[k]['Text'],'us':u[k]['Text'],'thai':inv[k],'reviewed_contract':needles})
    a.write('qa/inventory/critical-mechanics-review.json',samples)
    # Inventory descriptions normally use Normal/Small. Larger title fonts have
    # intentionally narrower original symbol repertoires; record those honestly.
    import verify_chapter1 as v
    stage=W/'staging/ThaiJP_Inventory_Working'
    actual=v.txtres.parse(str(stage/r))
    visible={c for k in inv for c in re.sub(r'<[^>]+>','',actual[k]['Text']) if not c.isspace()}
    coverage=[]
    for p in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        supported={chr(g[0]) for g in v.glyphs(p.read_bytes())[0]}
        missing=sorted(visible-supported)
        if 'Normal' in p.name or 'Small' in p.name:assert not missing,(p.name,missing)
        coverage.append({'font':p.name,'missing_visible_symbols':[{'character':c,'codepoint':hex(ord(c))} for c in missing]})
    a.write('qa/inventory/font-coverage.json',{'normal_and_small_complete':True,'font_specializations_retained':True,'fonts':coverage,'in_game_layout_tested':False})
    installed=(last.get('working_set_sha256','').upper()==sha(W/'translations/working-inventory-th.json'))
    report={'passed':True,'description_records':len(selected),'official_english_names':len(names),
            'coverage_groups':dict(matched),'all_selected_effects_translated':True,'same_id_us_names_verified':True,
            'control_tokens_preserved':True,'literal_numbers_verified':True,
            'normal_and_small_fonts_cover_all_inventory_text':True,
            'numeric_name_exceptions':{'1311':'JP Moogle Trio No.1/2 become official US names Moogle Mage/Moogle Bard. No gameplay quantity changed.'},
            'added_numeric_explanations':{'333':'四属性 rendered as 4 elements','1424':'ひとつ rendered as 1','1388–1393':'Roman armor grades rendered as Arabic digits in descriptions'},
            'previous_translations_preserved':untouched_prior,'prior_actor_metadata_preserved':True,
            'protected_installed_and_release_files':protected,'source_only':not installed,'installed':installed,'runtime_tested':False}
    a.write('qa/inventory/audit.json',report)
    print('Inventory audit passed:',len(selected),'effects;',len(names),'English names')
if __name__=='__main__':main()
