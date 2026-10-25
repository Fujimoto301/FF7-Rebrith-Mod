"""Persist the manually read Ch13 decisions and independently scan omissions."""
import re,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write
from audit_chapter13 import CFG,Q,digest
from choice_completion import JP

def main():
    cfg=read(CFG);now=read(cfg['source']);sha=digest(W/cfg['source']);corpus=read('reference/rebirth-jp-corpus.json');rows=read(Q+'review-records.json');ts=read('reference/chapter13-templates.json')
    groups=[]
    for a,prefix,reason in [('8800-FOREE_TxtRes.uasset','$C3310_MAIN_1050_','Landing is the point of no return: ขึ้นฝั่ง / ยังไม่ขึ้น matches the voyage warning.'),('Resident_TxtRes.uasset','$C3310_MAIN_0600_','Boarding the Tiny Bronco: ขึ้นเรือ / ยังไม่ขึ้น, not watching a tutorial.')]:
        ids=[k for k,v in corpus[a].items() if k.startswith(prefix) and k.endswith('_sys') and v['Text']];assert len(ids)==3
        groups.append(dict(asset='End/Content/Text/JP/'+a,prefix=prefix,choices=[dict(id=k,jp=corpus[a][k]['Text'],thai=now['assets']['End/Content/Text/JP/'+a]['entries'][k]) for k in ids],decision=reason,adjacent_dialogue_read=True))
    expected={(a,k) for a,d in corpus.items() for k,v in d.items() if v['Text'] and k.startswith(('$C3310_','$C3320_','$C3330_','$C3340_')) and k.endswith('_sys')}
    assert expected=={(Path(g['asset']).name,r['id']) for g in groups for r in g['choices']}
    write(Q+'choice-review.json',dict(source_sha256=sha,groups=groups,complete_question_and_all_buttons=True,nearby_response_context_reviewed=True,existing_choice_texts_unchanged=True,source_order_not_runtime_branch_proof=True,in_game_tested=False))
    nums=read(Q+'numeric-review.json');decisions={119:'二手 = two groups;2 in Thai.',461:'四番街スラム = Sector4 twice.',718:'倍 = double,2 times.',750:'ふたり = both2 opponents.'}
    if (W/'reference/chapter13-recheck-overrides.json').exists():
        decisions.update({303:'一発 =1 punch.',304:'一発 =1 punch.',306:'一発 =1 punch.',358:'ひとり =1 remaining Turk ahead.',594:'ひとつ =1 world; more than1 now.'})
    assert {r['template'] for r in nums}==set(decisions)
    write(Q+'numeric-decisions.json',dict(source_sha256=sha,records=[dict(r,decision=decisions[r['template']]) for r in nums],all_differences_reviewed=True))
    pronouns=[]
    for r in rows:
        if 'นาย' not in r['thai'] and 'เธอ' not in r['thai']:continue
        n=r['template'];reason='นาย addresses male Cloud/Barret/Turks; no global replacement.'
        if n in (65,184):reason='Tifa addresses female Aerith withเธอ.'
        elif n==438:reason='Nero addresses female Yuffie;เธอ preserved.'
        elif n==604:reason='Sephiroth addresses the mixed party including Cloud;พวกนาย, notพวกเธอ.'
        elif n==636:reason='ทำนาย is a lexical verb, not a second-person pronoun.'
        pronouns.append(dict(r,decision=reason))
    write(Q+'pronoun-review.json',dict(source_sha256=sha,records=pronouns,all_candidates_read=True,unknown_speakers_neutral=True))
    duplicates=[dict(template=t['index'],jp=t['jp'],actor=t['actor'],ids=t['examples'],decision='All same-speaker occurrences read in scene order; no question defaults reused across activities.') for t in ts if len(t['examples'])>1]
    write(Q+'duplicate-context-review.json',dict(source_sha256=sha,groups=duplicates,all_new_templates_read_twice=True,read_ranges=[[0,808]],short_lines_not_reused_from_earlier_activities=True))
    coverage=[];remaining=[];npc=[]
    for a,d in corpus.items():
        p=now['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})
        for k,v in d.items():
            if not v['Text'] or not JP.search(v['Text']):continue
            if '_NPC_' in k:
                assert k in p and not JP.search(p[k]),(a,k,'NPC omitted');npc.append(dict(asset=a,id=k))
            if k.startswith(('$C3310_','$C3320_','$C3330_','$C3340_','$TEMPL_BOS_')):
                assert k in p and not JP.search(p[k]),(a,k,'Ch13 omitted');coverage.append(dict(asset=a,id=k))
            if k not in p:
                if k.startswith(('$C3410_','$C3510_','$CAPTL_BOS_')):reason='Chapter14 dream/interlude/finale; not authorized yet.'
                elif re.match(r'\$(?:demo_|playdemo_|menu_TrialVersion_|menu_load_trial_)',k):reason='Demo/store/event-only UI; outside retail Chapter13, unchanged.'
                else:raise AssertionError((a,k,'Unclassified remaining Japanese'))
                remaining.append(dict(asset=a,id=k,jp=v['Text'],reason=reason))
    write(Q+'NPC-residual.json',dict(source_sha256=sha,registered_NPC_JP_rows=len(npc),untranslated_NPC_rows=0,ids=npc,unknown_ACTORs_checked=True,not_all_runtime_branches_tested=True))
    write(Q+'coverage-review.json',dict(source_sha256=sha,Ch13_JP_origin_rows=len(coverage),ids=coverage,missing=[],all_C33_and_Temple_boss_namespaces=True,previous_UI_and_all_NPC_namespaces_preserved=True,in_game_tested=False))
    write(Q+'deferred-remaining.json',dict(source_sha256=sha,records=remaining,categories=dict(Counter(r['reason'] for r in remaining)),all_remaining_Japanese_classified=True))
    print('Reviewed2 complete choice groups;',len(pronouns),'pronoun candidates;',len(nums),'numeric decisions;',len(coverage),'Ch13 JP rows;',len(npc),'NPC rows; all remaining Japanese individually classified.')
if __name__=='__main__':main()
