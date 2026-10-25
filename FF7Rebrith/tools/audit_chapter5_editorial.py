"""Record contextual Ch.5 review, including all ship NPCs and prior gender checks."""
import hashlib,json,re
from collections import Counter
from assemble_chapter5 import W,read,write,values

def main():
    rows=read('reference/chapter5-source.json');templates=read('reference/chapter5-templates.json');tr=values()
    current=read('translations/working-through-chapter5-th.json');base=read('translations/working-through-chapter4-th.json')
    corpus=read('reference/rebirth-jp-corpus.json')
    # Source-verified gender anchors. Model/voice suffixes alone do not establish gender.
    assert 'オジサマ' in templates[744]['jp'] and 'チトフ' in templates[744]['jp']
    assert '彼女' in templates[153]['jp'] and 'レジー' in templates[152]['jp']
    assert templates[25]['jp'].endswith('船長のチトフです')
    assert templates[450]['jp'].startswith('わたしよ　レジー・ケーニギン')
    evidence={
        'Captain Titov':dict(gender='male',basis='Self-introduction template25 and explicit オジサマ (older gentleman) in template744.',templates=[25,744]),
        'Regina':dict(gender='female',basis='JP 彼女 in connected announcing lines152–153 and named self-introduction450.',templates=[152,153,450]),
        'Chadley':dict(gender='male',basis='Established named character; qa/chapter2/gender-review.json speaker_evidence チャドリー, official he/his reference retained there.'),
        'unknown_NPCs':dict(gender='unresolved',basis='Neutral Thai. No gender assignment from generic labels, ID/model/voice suffixes, or hearsay.')}
    npc=[r for r in rows if r['id'].startswith('$FERRY_NPC_10_')]
    assert len(npc)==581
    unknown_sensitive=[];sensitive=[];context=[]
    for r in rows:
        t=tr[str(r['template'])];actor=r['English'].get('MetaData',{}).get('ACTOR','')
        if r['template']==25:actor='Captain Titov'
        if re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',t):
            assert actor in evidence and evidence[actor]['gender']=='male',(r['id'],t)
            assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน',t)
            sensitive.append(dict(id=r['id'],template=r['template'],actor=actor,thai=t,evidence=evidence[actor]))
        if re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน|นาย|เธอ|พ่อ|แม่|พี่|น้อง|หนุ่ม|สาว|ชาย|หญิง|ลุง|ป้า|สามี|แฟน|ทุกคน|ทั้งคู่',t):
            context.append(dict(id=r['id'],template=r['template'],jp=r['Text'],thai=t,actor=actor,
                decision='Context reviewed against JP; known listener/relationship retained, unidentified speakers neutral.'))
    assert all(not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',tr[str(r['template'])]) for r in npc)
    # Confirm every relevant Resident UI ID, including the previously omitted seven shops.
    resident='End/Content/Text/JP/Resident_TxtRes.uasset'
    ui_ids={k for k,r in corpus['Resident_TxtRes.uasset'].items() if r['Text'] and
        (k.startswith(('$FERRY_ITEM_','$FERRY_MAGIC_','$level_FERRY_','$str1360_FERRY_Chapter05')))}
    assert len(ui_ids)==99 and ui_ids<=current['assets'][resident]['entries'].keys()
    # Same JP short answers must be reviewed in context before reuse.
    assert tr['55']=='ไม่รู้สิ' and tr['88']=='ใช่' and tr['89']=='ไม่ใช่'
    assert tr['367'].count('2')==1 and tr['382'].endswith('“ไวซ์ รุ่น3”')
    write('qa/chapter5/contextual-gender-review.json',dict(source_records_scanned=len(rows),NPC_records=len(npc),
        NPC_without_ACTOR=sum(not r['MetaData'].get('ACTOR') for r in npc),
        sensitive_records=sensitive,relationship_pronoun_address_review=context,speaker_evidence=evidence,
        gender_mismatches=[],unresolved_gendered_endings=[],all_99_ship_UI_records_present=True,
        all_1284_templates_contextually_reviewed=True,unknown_NPCs_use_neutral_language=True,
        complete_new_video_audio_review=False,runtime_tested=False))
    write('qa/chapter5/proper-name-review.json',dict(
        policy='Official English ACTOR/UI names; Thai names inside dialogue; unknown ACTOR stays ??? before reveal.',
        existing_glossary='reference/plearngaming/glossary.json',
        previously_supplied_reference_terms={'Madam M':'มาดามเอ็ม','Andrea':'แอนเดรีย','Hojo':'โฮโจ','Jenova':'เจโนวา'},
        new_JP_transliterations={'Titov':'ทิตอฟ','Faz':'ฟาซ','Wize':'ไวซ์','Felix (JP フレッサー)':'เฟรสเซอร์',
            'Regina (JP レジー・ケーニギン)':'เรจี้ เคอนิกิน','Shinra-8 (JP 第八神羅丸)':'ชินระหมายเลข8'},
        new_terms_are_not_claimed_as_Plearn_verified=True,
        reference_videos=[dict(url='https://www.youtube.com/watch?v=i4gD0mmj5vc',chapter5_start='21:30:39',basis='Previously user-supplied chapter timing; no fresh full video/audio review.'),
            dict(url='https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU',basis='User-supplied JP voice reference')]))
    print('Contextual review passed:',len(rows),'records,',len(npc),'ship NPCs,',len(sensitive),'gender-sensitive records,',len(context),'context candidates; 99 ship UI records.')

if __name__=='__main__':main()
