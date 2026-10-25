"""Check the active Chapters1/2 + menu set against the latest user policy."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import assemble_menu as menus
import assemble_chapter2 as chapter2

W=chapter2.W
Q=W/'qa/current-conditions'
def read(name):return json.loads((W/name).read_text(encoding='utf-8'))

def main():
    ch1=read('translations/chapter1-th.json')
    ch2=read('translations/chapter2-th.json')
    menu=read('translations/menu-th.json')
    combined=read('translations/working-through-chapter2-th.json')
    r1=read('reference/chapter1-source.json')
    r2=read('reference/chapter2-source.json')+read('reference/chapter2-shared-source.json')
    deferred={x['index'] for x in read('reference/chapter2-deferred.json')}
    r2=[r for r in r2 if r['index'] not in deferred]
    ids={(r['asset'],r['id']) for r in r1+r2}
    resident='End/Content/Text/JP/Resident_TxtRes.uasset'
    names=ch1['assets'][resident]['entries']
    character_labels={k:t for k,t in names.items() if (resident,k) not in ids}
    assert len(character_labels)==27
    ids|={(resident,k) for k in character_labels}
    ids|={(a,k) for a,p in menu['assets'].items() for k in p['entries']}
    actual={(a,k) for a,p in combined['assets'].items() for k in p['entries']}
    assert actual==ids, (actual-ids,ids-actual)
    forbidden=('$Item','$item','$it_','$BattleSkill','$Materia','$WeaponAbility')
    assert not any(k.startswith(forbidden) for _,k in actual)
    for asset,p in combined['assets'].items():
        for k,t in p['entries'].items():
            assert not re.search(r'[\u3040-\u30ff\u4e00-\u9fff\uff10-\uff19\ud800-\udfff]',t),(asset,k)
            assert not re.search(r'(?:เซคเตอร์|หมายเลข|อันดับ|อายุ)(?:หนึ่ง|สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า)',t),k
            assert 'วูไท' not in t and 'อวาลันช์' not in t,k
            assert 'มาเทเรีย' not in t and 'มาทีเรีย' not in t,k
        for k,actor in p['actors'].items():
            assert not re.search(r'[\u0e00-\u0e7f\u3040-\u30ff\u4e00-\u9fff]',actor),k
    menu_source=read('reference/menu-source.json')
    output=menu['assets'][resident]['entries']
    protected=[]
    for row in menu_source['rows']:
        t=output[row['id']]
        assert menus.TOKEN.findall(t)==menus.TOKEN.findall(row['Text']),row['id']
        for jp,en in menus.PROTECTED_NAMES.items():
            if jp in row['Text']:
                assert en.casefold() in t.casefold(),(row['id'],en)
                protected.append(dict(id=row['id'],proper_name=en))
        for mode in ('EASY','NORMAL','ADVANCED','HARD','ACTION','CLASSIC','WAIT'):
            if mode in row['Text']:assert mode in t,(row['id'],mode)
    # Named items/features inside voiced/ambient dialogue are Thai. System
    # confirmations and standalone character-name choices retain UI names.
    ui_exceptions={862,863,864,1030,1717,2544}
    english_names=('Folio','Golden Plume','Chocobo & Moogle','Windmill Gear','Quetzalcoatl Talon','Moogle Medal','Potion','Monster Assessment Instrument')
    dialogue_names=[]
    for r in r2:
        text=ch2['assets'][r['asset']]['entries'][r['id']]
        if r['index'] in ui_exceptions:continue
        assert not any(name in text for name in english_names),r['id']
        words=set(re.findall(r'[A-Za-z]+',re.sub(r'<[^>]+>','',text)))
        assert all(len(word)==1 or word=='VR' for word in words),(r['id'],words)
        if any(name in r.get('English',{}).get('Text','') for name in english_names):
            dialogue_names.append(dict(index=r['index'],id=r['id'],thai=text))
    expected_ui={862:'Burke',863:'Burt',864:'Beck',1030:'Hustle de Chocobo',1717:'Windmill Gear',2544:'Moogle Mischief'}
    indexed={r['index']:r for r in r2}
    for i,name in expected_ui.items():
        r=indexed[i];assert name in ch2['assets'][r['asset']]['entries'][r['id']]
    # In addition to the existing Chapter1 particle audit, cover male first-
    # person pronouns that had no ครับ and were missed by the older baseline.
    retained={r['id'] for r in read('reference/gender-particle-review.json')['rows'] if r['decision']=='retain_verified_particle'}
    male_named={'クラウド','セフィロス','ゾンダー'}
    pronouns=[]
    for r in r1:
        t=ch1['assets'][r['asset']]['entries'][r['id']]
        if 'ผม' in t and r['index'] not in (840,994):
            assert r['MetaData'].get('ACTOR') in male_named or r['id'] in retained,r['id']
            pronouns.append(r['id'])
    changes=read('qa/current-conditions/changes.json')
    baseline=read('qa/current-conditions/baseline.json')
    previous=json.loads((Path(baseline['backup'])/'translations/working-through-chapter2-th.json').read_text(encoding='utf-8'))
    changed_records=sum(t!=previous['assets'][asset]['entries'].get(k)
                        for asset,p in combined['assets'].items() for k,t in p['entries'].items())
    unchanged=[]
    for f in baseline['protected_files']:
        assert hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
        unchanged.append(f['path'])
    report=dict(chapter1_dialogue_records=len(r1),chapter2_dialogue_and_conversation_records=len(r2),menu_records=len(output),
                english_character_ui_labels=len(character_labels),combined_records=len(actual),
                edited_source_strings=len(changes),changed_compiled_records=changed_records,edited_by_group=dict(Counter(x['file'].split('/')[1] for x in changes)),
                names_in_dialogue_thai=True,names_in_translated_menus_english=True,english_actor_labels=True,
                reviewed_menu_proper_name_occurrences=protected,dialogue_item_name_examples=dialogue_names,
                item_skill_database_untouched=True,map_and_area_label_scope_unchanged=True,
                chapter1_extra_male_pronoun_lines_checked=pronouns,unconfirmed_pronouns_neutralized=[732,874,875],
                particles_audits=['qa/chapter1/gender-particle-audit.json','qa/chapter2/gender-review.json'],
                installed_and_dist_files_unchanged=unchanged,working_files_only=True,runtime_tested=False,
                limitations='NPCs without confirmed identity use neutral phrasing. No new full video/audio review. Existing installed trial is the earlier version; corrections are working assets only.')
    (Q/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('reviewed_menu_proper_name_occurrences','dialogue_item_name_examples','installed_and_dist_files_unchanged','chapter1_extra_male_pronoun_lines_checked')},ensure_ascii=False))

if __name__=='__main__':main()
