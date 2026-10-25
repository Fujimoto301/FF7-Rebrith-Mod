"""Second-pass gender/relationship review, including every selected Junon NPC ID.

Lexical coverage is exhaustive; identity claims are limited to named characters
and recorded context. This does not claim to identify every NPC from video.
"""
import hashlib,re
from collections import Counter,defaultdict
from pathlib import Path
from assemble_chapter4 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from audit_chapter4 import MALE,FEMALE,STAGE

QA='qa/chapter4/gender-recheck/'
PARTICLE=re.compile(r'ครับ|กระผม|ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|ดิชั้น|หม่อมฉัน|กระหม่อม|เจ้าค่ะ|เจ้าคะ|เพคะ|พ่ะย่ะค่ะ|ขอรับ|ผม|จ๊ะ|จ้ะ|จ๋า|ฮะ|ฮ่ะ|ย่ะ')
ADDRESS=re.compile(r'นาย|เธอ|หล่อน|หนู|เจ๊|พี่|น้อง|ลูก|พ่อ|แม่|ลุง|ป้า|หนุ่ม|สาว|ชาย|หญิง|ผัว|เมีย|สามี|ภรรยา|เจ้าคุณ|ฝ่าบาท')
JP_CONTEXT=re.compile(r'彼女|彼氏|お姉|お兄|お父|お母|娘|息子|嫁|妻|夫|女|男|弟|妹|姉|兄')
SEXED_SELF=re.compile(r'ครับ|กระผม|ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|ดิชั้น|หม่อมฉัน|กระหม่อม|เจ้าค่ะ|เจ้าคะ|เพคะ|พ่ะย่ะค่ะ|ผม')
FEMALE_FORM=re.compile(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|ดิชั้น|หม่อมฉัน|เจ้าค่ะ|เจ้าคะ|เพคะ')
MALE_FORM=re.compile(r'ครับ|กระผม|กระหม่อม|พ่ะย่ะค่ะ|ผม')
GENERIC_CODES={'mma','mfa','mmk','mfk','skm','skf','sma','sfa','sys'}

def clean_actor(s):return re.sub('<[^>]+>','',s).strip()
def gender_of(s):
    actors=[x.strip() for x in clean_actor(s).split('&')]
    if all(x in MALE for x in actors):return 'male'
    if all(x in FEMALE for x in actors):return 'female'
    return 'unverified'

def main():
    baseline=read(QA+'baseline.json');previous=read(baseline['old_combined'])
    now=read('translations/working-through-chapter4-th.json');patch=read('translations/chapter4-th.json')['assets']
    rows=read('reference/chapter4-source.json');deferred={r['id'] for r in read('reference/chapter4-deferred.json')}
    corpus=read('reference/rebirth-jp-corpus.json');fixes=read(QA+'corrections.json')
    allowed={(r['asset'],r['id']) for c in fixes['changes'] for r in c['records']}
    changed=set()
    assert now.keys()==previous.keys()
    for a,p in previous['assets'].items():
        assert now['assets'][a]['actors']==p['actors']
        assert now['assets'][a]['entries'].keys()==p['entries'].keys()
        for k,t in p['entries'].items():
            if now['assets'][a]['entries'][k]!=t:changed.add((a,k))
    assert changed==allowed and len(changed)==fixes['records']
    for change in fixes['changes']:
        for r in change['records']:
            assert previous['assets'][r['asset']]['entries'][r['id']]==change['before']
            assert now['assets'][r['asset']]['entries'][r['id']]==change['after']
    cmap=read('reference/through-chapter4-cluster-map.json');reverse=str.maketrans({v:k for k,v in cmap.items()})
    parsed={a:txtres.parse(str(STAGE/a)) for a in patch}
    # Reuse named character identities only for unique non-generic suffixes.
    identity=defaultdict(set);identity_ids=defaultdict(list)
    for r in rows:
        actor=clean_actor(r['English'].get('MetaData',{}).get('ACTOR',''))
        code=r['id'].rsplit('_',1)[-1]
        if code not in GENERIC_CODES and gender_of(actor)!='unverified':
            key=(r['asset'],code);identity[key].add(actor);identity_ids[key].append(r['id'])
    records=[];focus=[];endings=[];npc=[];counts=Counter();actors=Counter()
    for r in rows:
        a=r['asset'];k=r['id']
        if k in deferred:continue
        t=patch[a]['entries'][k];before=previous['assets'][a]['entries'][k]
        assert parsed[a][k]['Text'].translate(reverse)==t
        actor=clean_actor(patch[a]['actors'].get(k,''));named=actor
        code=k.rsplit('_',1)[-1]
        if gender_of(named)=='unverified' and len(identity.get((a,code),set()))==1:
            named=next(iter(identity[(a,code)]))
        gender=gender_of(named)
        # The lexical ผม in these two records is hair, not a male pronoun.
        gender_text=t.replace('ผม','') if r['template'] in {583,1635} else t
        if gender=='male':assert not FEMALE_FORM.search(gender_text),(k,t)
        elif gender=='female':assert not MALE_FORM.search(gender_text),(k,t)
        else:assert not SEXED_SELF.search(gender_text),(k,actor,t)
        assert not re.search(r'นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|รึค่ะ|ค่ะ\s*\?',t),(k,t)
        # จ๊ะ is used by any gender when addressing a child/pet. ฮะ in ฮะๆ
        # is laughter; เจ๊ง/เจ๊า/เป้าหมาย are not personal gender references.
        flags=[]
        if PARTICLE.search(t) or PARTICLE.search(before):flags.append('particle_or_pronoun_or_lexical_homograph')
        if ADDRESS.search(t) or ADDRESS.search(before):flags.append('address_or_relationship_or_lexical_homograph')
        if JP_CONTEXT.search(r['Text']):flags.append('jp_context_candidate')
        is_npc=k.startswith(('$JNONT_NPC_10_','$JNONV_NPC_10_','$JUNOA_NPC_10_'))
        item=dict(id=k,template=r['template'],actor_label=actor,resolved_named_identity=named,
            speaker_gender=gender,identity_basis='Named JP/US actor or unique named-character suffix' if gender!='unverified' else 'Not inferred from generic NPC codes; neutral self-reference',
            npc=is_npc,has_actor=bool(r['MetaData'].get('ACTOR')),jp=r['Text'],thai=t,focus=flags,
            included_in_staged_binary=True)
        records.append(item);counts[gender]+=1;actors[actor]+=1
        if flags:focus.append(item)
        if SEXED_SELF.search(gender_text):endings.append(item)
        if is_npc:npc.append(item)
    raw={k for k,v in corpus['8200-JUNOE_TxtRes.uasset'].items()
        if k.startswith(('$JNONT_NPC_10_','$JNONV_NPC_10_','$JUNOA_NPC_10_')) and v['Text']}
    assert len(raw)==922 and len(raw&deferred)==32
    assert {r['id'] for r in npc}==raw-deferred and len(npc)==890
    assert sum(not r['has_actor'] for r in npc)==781
    assert len(records)==3206
    for i in (1790,2644,2877):
        assert not re.search('สาว|หนุ่ม',next(r['thai'] for r in records if r['template']==i))
    context_notes=[
        dict(templates=[1341,1344,1506],decision='Wife references retained: 嫁/妻 in the same exchange establishes the relationship; no male first-person particle is inferred.'),
        dict(templates=[1421,1422,1428,1429,2814,2815,2817,2825],decision='Brother references retained where 兄/弟 is explicit in Japanese; Devin self-reference ผม is supported by 弟.'),
        dict(templates=[647,649,650,651,656,2428,2477],decision='Father/daughter references retained where パパ/父/娘 is explicit; speaker gender is not taken from the listener.'),
        dict(templates=[2480,2482,2484,2486,2490],decision='Claire pregnancy/child context checked together. Maternal reassurance retained; no gender is assigned to the unborn child.'),
        dict(templates=[583,1635],decision='ผม means hair; not counted as male first-person usage.'),
        dict(templates=[1592],decision='จ๊ะ retains baby talk to a cat; it is not evidence that the speaker is female.'),
        dict(templates=[2711,2733],decision='Finn calls the group おじさん explicitly in JP; this is retained as his teasing address, not used to infer the party is all male.'),
        dict(templates=[2834],decision='ขอรับ 3 กิล means receive 3 gil; not an added male ending.'),
    ]
    write(QA+'records.json',dict(records=records,all_selected_rows_lexically_scanned=True,video_audio_verified=False))
    write(QA+'focused-review.json',dict(records=focus,context_notes=context_notes,
        particle_forms='Male ครับ; female ค่ะ in statements / คะ in questions / นะคะ. Only as appropriate; neutral forms for unidentified speakers.',
        no_gender_from_mma_mfa=True,new_video_audio_review=False))
    assert fingerprint()==baseline['protected']
    summary=dict(chapter=4,all_selected_records=len(records),npc_records=len(npc),npc_without_actor=781,
        source_npc_records=922,later_npc_states_excluded=32,all_later_records_excluded=len(deferred),
        focused_records=len(focus),self_reference_or_politeness_records=len(endings),speaker_policy_counts=dict(counts),
        corrections=fixes['records'],previous_actor_labels_unchanged=True,only_documented_translation_corrections=True,
        missing_selected_npc_ids=[],gender_mismatches=[],wrong_female_particle_forms=[],
        unidentified_speakers_use_neutral_language=True,installed_files_unchanged=True,
        full_video_audio_review=False,runtime_tested=False)
    write(QA+'summary.json',summary)
    print('Detailed Ch.4 recheck passed:',len(records),'records;',len(npc),'NPC records (781 actorless);',len(focus),'focused cases;',fixes['records'],'corrections')
if __name__=='__main__':main()
