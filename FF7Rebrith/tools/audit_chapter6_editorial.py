"""Context, source terminology and NPC completeness checks for Costa's first visit."""
import hashlib,json,re
from collections import Counter
from assemble_chapter6 import W,read,write,values

def main():
    rows=read('reference/chapter6-source.json');templates=read('reference/chapter6-templates.json');tr=values()
    deferred=read('reference/chapter6-deferred.json');deferred_ids={r['id'] for r in deferred}
    selected=[r for r in rows if r['id'] not in deferred_ids]
    current=read('translations/working-through-chapter6-th.json');patch=read('translations/chapter6-th.json')
    assert len(rows)==1805 and len(selected)==1698 and len(templates)==1737
    assert '男ジョニー' in templates[43]['jp'] and templates[44]['jp'].startswith('ホテルのオーナー')
    evidence={'Johnny':dict(gender='male',basis='Named introduction 男ジョニー in template43; connected named ACTOR Johnny.',templates=[43,44]),
        'unknown_NPCs':dict(gender='unresolved',basis='Neutral Thai; no sex inference from model codes or generic ACTOR labels.')}
    npc=[r for r in rows if r['id'].startswith('$COSTT_NPC_10_')]
    active_npc=[r for r in npc if r['id'] not in deferred_ids]
    assert len(npc)==796 and len(active_npc)==698
    sensitive=[];context=[]
    overrides=read('reference/chapter6-ui-overrides.json')
    for r in selected:
        t=overrides.get(r['id'],tr[str(r['template'])]);actor=r['English'].get('MetaData',{}).get('ACTOR','')
        assert t==patch['assets'][r['asset']]['entries'][r['id']]
        if re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',t):
            assert actor=='Johnny',(r['id'],t)
            assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน',t)
            sensitive.append(dict(id=r['id'],template=r['template'],actor=actor,jp=r['Text'],thai=t,evidence=evidence[actor]))
        if re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน|นาย|เธอ|พ่อ|แม่|พี่|น้อง|หนุ่ม|สาว|ชาย|หญิง|ลุง|ป้า|สามี|ภรรยา|แฟน|ทุกคน|ทั้งคู่',t):
            context.append(dict(id=r['id'],template=r['template'],actor=actor,jp=r['Text'],thai=t,
                decision='JP relationship/listener context reviewed; known gender references retained, unidentified speakers neutral.'))
    assert len(sensitive)==27
    assert all(not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน',tr[str(r['template'])]) for r in active_npc)
    assert tr['410']=='ใช่' and tr['411']=='ไม่ใช่' and tr['473']=='ก็ใช่'
    assert tr['164']=='ถูกวิสเปอร์เอาไปเหรอ' and 'อิฟาลน่า' in tr['307'] and 'อิฟาลน่า' in tr['379']
    # These remain untranslated in staging until their later story states.
    assert {r['id'].split('_')[4] for r in deferred if r['id'].startswith('$COSTT_NPC_10_0100_')}=={'15900','15910','15920','15930','16000','16100'}
    name_fallbacks={k:v for a,p in patch['assets'].items() for k,v in p['actors'].items()
        if any(r['id']==k and not r['English'].get('MetaData',{}).get('ACTOR') for r in rows)}
    assert name_fallbacks=={'$C2410_MAIN_0100_0700_13_nem':'Swimsuit Girl','$C2410_MAIN_4500_1200_00_hjo':'Hojo','$COSTT_QST_05_0200_0810_00_tif':'Tifa'}
    write('qa/chapter6/contextual-gender-review.json',dict(source_records_scanned=1805,selected_records=1698,prepared_templates=1737,
        total_Costa_NPC_records=796,selected_NPC_records=698,deferred_NPC_records=98,
        selected_NPC_without_ACTOR=sum(not r['MetaData'].get('ACTOR') for r in active_npc),
        sensitive_records=sensitive,relationship_pronoun_address_review=context,speaker_evidence=evidence,
        gender_mismatches=[],unresolved_gendered_endings=[],unknown_NPCs_use_neutral_language=True,
        actor_fallbacks=name_fallbacks,all_prepared_templates_contextually_reviewed=True,
        full_new_video_audio_review=False,runtime_tested=False))
    # Keep exact evidence for Plearn names and separate new JP transliterations.
    plearn=read('reference/plearngaming/remake/decoded-corpus.json');terms={}
    for a in plearn['assets']:
        for r in a.get('entries',[]):
            for word in ('จอห์นนี่','อิฟาลน่า','วิสเปอร์','โกลด์ซอซเซอร์'):
                if word in r.get('text','') and word not in terms:terms[word]=dict(asset=a['asset'],id=r.get('id'),thai=r['text'])
    assert len(terms)==4
    write('qa/chapter6/proper-name-review.json',dict(policy='Official same-ID English ACTOR/UI names; Thai proper names in dialogue; JP tags preserved.',
        Plearn_terms=terms,existing_glossary='reference/plearngaming/glossary.json',
        new_JP_transliterations={'Kapono':'คาโปโน','Jenny':'เจนนี่','Riana':'เรียนา','Dokaccha':'โดคัตชา','Maahir (JP マコイ)':'มาคอย',
            'Happy Tender (JP ハッピーテンダー / US Hidden Cactuar)':'แฮปปี้เทนเดอร์','Wheelie':'วีลลี'},
        UI_name_corrections={'Pirate’s Rampage pirate-ship stage':'Official US Brigantine; JP color tags retained',
            'Run Wild battle-royal stage':'Official US Free-for-All'},
        new_terms_are_not_claimed_as_Plearn_verified=True,
        video_references=['https://www.youtube.com/watch?v=i4gD0mmj5vc','https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU'],
        no_new_full_video_audio_review=True))
    print('Contextual review passed:',len(selected),'selected,',len(active_npc),'NPCs,',len(sensitive),'gender-sensitive records,',len(context),'context candidates.')

if __name__=='__main__':main()
