"""Retain exact prior evidence; audit all actual new particle occurrences."""
import hashlib,re
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from audit_gender_through_chapter8 import PARTICLES,NAMED,PARTY

def main():
    cfg=read('reference/chapter9-build.json');now=read(cfg['source']);old={r['id']:r for r in read('qa/chapter8/gender/records.json')['records']};cm=read(cfg['cluster_map']);reverse=str.maketrans({v:k for k,v in cm.items()})
    rows=[];totals=Counter({k:0 for k in PARTICLES});genders=Counter();npcs=Counter();byactor={};priorseen=set()
    us=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    assert 'his training' in us['$level_QUEST23_Task_Explanation_110']['Text']
    for a,p in now['assets'].items():
        staged=txtres.parse(str(W/cfg['stage']/a))
        for k,t in p['entries'].items():
            matches={name:len(pattern.findall(re.sub('<[^>]+>','',t))) for name,pattern in PARTICLES.items()}
            if not sum(matches.values()):continue
            assert staged[k]['Text'].translate(reverse)==t,k;actor=re.sub('<[^>]+>','',p['actors'].get(k,''))
            if k in old:
                r=old[k];assert r['thai']==t;kold=dict(r);gender=r['speaker_gender'];matches=r['counts'];evidence=r['evidence'];priorseen.add(k)
            else:
                if actor in NAMED:gender,reason=NAMED[actor];evidence=dict(method='Existing named character identity evidence',reason=reason)
                elif actor=='Sotetsu' or k in ('$GONGE_QST_02_0200_0500_00_sot','$GONGE_QST_02_0200_0600_00_sot'):
                    gender='male';evidence=dict(method='Exact self-introduction continuation before and after name reveal; US official quest refers to his training',source='source/End/Content/Text/US/Resident_TxtRes.uasset',id='$level_QUEST23_Task_Explanation_110',quote='accompany Sotetsu and help facilitate his training',JP_anchor='$GONGE_QST_02_0200_0700_00_sot')
                else:raise AssertionError((k,actor,'No evidence for gendered particle'))
                assert not re.search(r'นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|ค่ะ\s*\?',t),(k,t)
                if gender=='male':assert not matches['ค่ะ'] and not matches['คะ'],(k,t)
                else:assert not matches['ครับ'],(k,t)
            totals.update(matches);genders[gender]+=sum(matches.values());isnpc=actor not in PARTY
            if isnpc:npcs.update(matches)
            byactor.setdefault(actor,Counter({name:0 for name in PARTICLES})).update(matches)
            rows.append(dict(asset=a,id=k,actor_label=actor,speaker_gender=gender,counts=matches,npc_or_nonparty=isnpc,thai=t,evidence=evidence,matches_speaker_gender=True))
    assert priorseen==old.keys();prior=read('qa/chapter8/gender/summary.json')
    assert {name:sum(r['counts'][name] for r in rows if r['id'] in old) for name in PARTICLES}==prior['counts']
    summary=dict(chapters=list(range(1,10)),source_records_scanned=sum(len(p['entries']) for p in now['assets'].values()),particle_bearing_records=len(rows),actual_particle_occurrences=sum(totals.values()),counts=dict(totals),male_speaker_occurrences=genders['male'],female_speaker_occurrences=genders['female'],npc_or_nonparty_occurrences=sum(npcs.values()),npc_or_nonparty_counts=dict(npcs),gender_mismatches=[],unresolved_particle_bearing_speakers=[],all_prior701_particles_preserved=True,evidence_method='Prior exact-record reviews plus named ACTOR evidence; Sotetsu same-speaker introduction and official US his-training text. Generic mma/mfa alone never used.',combined_source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),runtime_tested=False,new_full_video_audio_review=False)
    write('qa/chapter9/gender/summary.json',summary);write('qa/chapter9/gender/records.json',dict(records=rows,by_actor={a:dict(v) for a,v in byactor.items()}))
    print(summary)

if __name__=='__main__':main()
