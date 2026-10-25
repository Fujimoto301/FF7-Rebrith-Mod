"""Check every actual ครับ/ค่ะ/คะ occurrence in the current verified release.

Use exact record evidence for generic NPC labels; a generic actor code does not
establish gender. Preserve the intentional male stutter as a separate case.
"""
import hashlib,json,re
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write,txtres
from assemble_ui_completion import fingerprint

ROOT='qa/chapter8/gender/'
PARTICLES={'ครับ':re.compile('ครับ'),'ค่ะ':re.compile('ค่ะ'),'คะ':re.compile(r'คะ(?=[^\u0e00-\u0e7f]|$)')}
PARTY={'Cloud','Barret','Tifa','Aerith','Red XIII','Yuffie','Cait Sith','Sephiroth'}
NAMED={
    'Zack':('male','Established named protagonist Zack, JP ザックス; prior Chapter1 flashback actor identity.'),
    'Marlene':('female','Established named daughter of Dyne/Eleanor, cared for by Barret; JP マリン and Chapter8 family context.'),
    'Esther':('female','Established named chocobo manager Esther, JP エスト; explicit female named persona in the race meeting.'),
    'Cait Sith':('male','Established male cat persona Cait Sith, named ACTOR ケット・シー; gender of dialogue persona, not a biological claim about the robot.'),
    'Suspicious Man':('male','Exact JP ACTOR 不審な男 explicitly identifies a man for UNDRS_QST_02_0700 records.'),
    'Yuffie':('female','Established named character and prior Ch4/Ch6 contextual speaker review; mock polite requests in C2510.'),
    'Scarlet':('female','Established named character; JP スカーレット and US named actor in Corel flashback.'),
    'Reeve':('male','Established named Shinra executive Reeve; JP リーブ / US named actor.'),
    'Johnnys':('male','Group of identical Johnny clones; explicit self-identity in CORLE_QST_01 and prior 男ジョニー evidence.'),
    'Amina':('female','CORLE_QST_03_0900_1300–1400: Amina points to fellow women and Jules explicitly confirms female membership increase because of Tifa.'),
    'Terrified Woman':('female','Exact JP ACTOR おびえた女性 explicitly identifies a woman, later revealed as Ellie.'),
    'Johnny':('male','Explicit 男ジョニー in Ch.6 template43, connected named ACTOR and self-introduction.'),
    'Captain Titov':('male','Named JP self-introduction template25 and explicit オジサマ in chapter5 template744.'),
    'Cloud':('male','Named ACTOR; Chapter1 visual identity record and same named Cloud in Chapter4.'),
    'Tifa':('female','Named ACTOR; Chapter1 visual identity and Chapter2 お嬢さんたち context.'),
    'Aerith':('female','Named ACTOR; established character identity, also addressed with Tifa as お嬢さんたち.'),
    'Chadley':('male','Named ACTOR; existing Chapter2 speaker evidence and official he/his profile.'),
    'Chloe':('female','JP クリン is explicitly 妹 of Billy in C2010_MAIN_2000_2700; named US ACTOR Chloe.'),
    'Nene':('female','Resident CARDG_QST_08_0500_0200 explicitly calls Nene このお嬢ちゃん.'),
    'Elena':('female','Named ACTOR and self-introduction C2110_MAIN_1600_1600; prior official she/her profile evidence.'),
    'Tseng':('male','Named character; prior Chapter3/4 speaker identity review.'),
    'Heidegger':('male','Named character; prior Chapter4 speaker identity review.'),
    'MAI':('female','Established feminine AI persona in Chapter4 speaker review; this describes the dialogue voice/persona, not biological sex.'),
}

def main(active=False):
    global ROOT
    before=fingerprint();context=read('qa/active-working-set.json')
    assert context['chapters']==[1,2,3,4,5,6,7,8]
    stage=W/context['stage'];source=context['combined_source'] if active else 'translations/working-through-chapter6-th.json'
    if active:ROOT='qa/chapter8/gender/'
    current=read(source)
    corpus=read('reference/rebirth-jp-corpus.json')
    cmap=read(context['cluster_map'] if active else 'reference/through-chapter6-cluster-map.json');reverse=str.maketrans({v:k for k,v in cmap.items()})
    retained={r['id']:r for r in read('reference/gender-particle-review.json')['rows'] if r['decision']=='retain_verified_particle'}
    chapter2=read('qa/chapter2/gender-review.json')['speaker_evidence']
    chapter3=read('qa/chapter3/gender-review.json')['speaker_evidence']
    ch4={r['id']:r for r in read('qa/chapter4/gender-recheck/records.json')['records']}
    # Check the identity-context anchors against actual JP, not model-name suffixes.
    assert '妹のクリン' in corpus['8100-GRASE_TxtRes.uasset']['$C2010_MAIN_2000_2700_00_grb']['Text']
    assert 'お嬢ちゃん' in corpus['Resident_TxtRes.uasset']['$CARDG_QST_08_0500_0200_00_hem']['Text']
    assert 'ネネ' in corpus['Resident_TxtRes.uasset']['$CARDG_QST_08_0500_0200_00_hem']['Text']
    for jp in ('チャドリー','クリン','ティファ','ネネ'):assert chapter2[jp]['gender'] in ('male','female')
    assert chapter3['eln']['actor']=='Elena' and chapter3['eln']['gender']=='female'
    rows=[];totals=Counter({k:0 for k in PARTICLES});npc=Counter({k:0 for k in PARTICLES})
    genders=Counter();special=[];by_actor={}
    for a,p in current['assets'].items():
        actual=txtres.parse(str(stage/a));original=corpus[Path(a).name]
        for k,t in p['entries'].items():
            visible=re.sub('<[^>]+>','',t)
            matches={name:len(pattern.findall(visible)) for name,pattern in PARTICLES.items()}
            if not sum(matches.values()):continue
            assert actual[k]['Text'].translate(reverse)==t,k
            actor=re.sub('<[^>]+>','',p['actors'].get(k,''))
            if k=='$C2310_MAIN_0100_2600_00_ttv':
                assert actor=='Announcement'
                actor='Captain Titov'
            if k in retained:
                ev=retained[k]['evidence'];gender=ev['gender']
                basis=dict(method='Existing exact-record speaker evidence',reference='reference/gender-particle-review.json',evidence=ev)
            elif actor in NAMED:
                if actor=='Suspicious Man':assert original[k].get('MetaData',{}).get('ACTOR')=='不審な男',k
                gender,reason=NAMED[actor];basis=dict(method='Named character / JP context',reason=reason)
            elif actor=='???' and k.endswith('_eln'):
                assert k.startswith(('$C2110_MAIN_1500_','$C2110_MAIN_1600_'))
                assert original[k].get('MetaData',{}).get('ACTOR')=='？？？？'
                gender='female';basis=dict(method='Elena prior to name reveal',reference='qa/chapter3/gender-review.json',
                    evidence=chapter3['eln'])
            else:raise AssertionError((k,actor,'No record-specific or named speaker evidence'))
            if k=='$C1910_MAIN_7150_0500_00_mma':
                assert visible=='คะ…ครับ!' and original[k]['Text']=='はっ……はい！'
                assert gender=='male' and matches=={'ครับ':1,'ค่ะ':0,'คะ':1}
                matches['คะ']=0
                special.append(dict(id=k,thai=t,reason='คะ… is an initial stutter before ครับ, not a feminine sentence ending.',jp=original[k]['Text']))
            if gender=='male':assert not matches['ค่ะ'] and not matches['คะ'],(k,t)
            else:assert not matches['ครับ'],(k,t)
            assert not re.search(r'นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|รึค่ะ|ค่ะ\s*\?',visible),(k,t)
            totals.update(matches);genders[gender]+=sum(matches.values())
            is_npc=actor not in PARTY
            if is_npc:npc.update(matches)
            by_actor.setdefault(actor or '(no ACTOR)',Counter({x:0 for x in PARTICLES})).update(matches)
            rows.append(dict(asset=a,id=k,actor_label=actor,resolved_speaker='Elena' if actor=='???' else actor or 'Nibelheim innkeeper (exact matched record)',
                speaker_gender=gender,counts=matches,npc_or_nonparty=is_npc,chapter4=k in ch4,
                jp=original[k]['Text'],thai=t,evidence=basis,matches_speaker_gender=True))
    previous=read('qa/chapter7/gender/summary.json')
    old_ids={r['id'] for r in read('qa/chapter7/gender/records.json')['records']}
    prior=[r for r in rows if r['id'] in old_ids]
    assert len(prior)==previous['particle_bearing_records']==594
    assert {p:sum(r['counts'][p] for r in prior) for p in PARTICLES}==previous['counts']
    assert set(old_ids)=={r['id'] for r in prior}
    assert sum(totals.values())==sum(genders.values())
    assert sum(r['counts']['คะ']+r['counts']['ค่ะ'] for r in rows if r['actor_label']=='???')==10
    summary=dict(chapters=[1,2,3,4,5,6,7,8],source_records_scanned=sum(len(p['entries']) for p in current['assets'].values()),
        particle_bearing_records=len(rows),actual_particle_occurrences=sum(totals.values()),counts=dict(totals),
        male_speaker_occurrences=genders['male'],female_speaker_occurrences=genders['female'],
        npc_or_nonparty_occurrences=sum(npc.values()),npc_or_nonparty_counts=dict(npc),
        hidden_label_Elena_records=10,gender_mismatches=[],unresolved_particle_bearing_speakers=[],
        wrong_female_question_or_nakha_forms=[],stutter_cases=special,
        count_method='Occurrences in translated asset records, including repeats and นะคะ; excludes คะ in other Thai words and the one explicit male stutter.',
        evidence_method='Exact-record retained NPC evidence, named characters, JP relationship/introduction text and prior speaker reviews. Generic mma/mfa codes alone are not evidence.',
        used_existing_visual_identity_evidence=True,new_full_video_audio_review=False,runtime_tested=False,
        translation_changes=0,zip_changes=0,installed_files_unchanged=True,
        combined_source_sha256=hashlib.sha256((W/source).read_bytes()).hexdigest())
    assert fingerprint()==before
    write(ROOT+'records.json',dict(records=rows,by_actor={k:dict(v) for k,v in by_actor.items()}))
    write(ROOT+'summary.json',summary)
    print('Passed:',len(rows),'records /',sum(totals.values()),'actual particles;',dict(genders),'; mismatches 0; unresolved 0')
if __name__=='__main__':
    import sys
    main(active=True)
