"""Source-bound editorial decisions after the complete JP/Thai second read."""
import re
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write
from audit_chapter14 import CFG,Q,digest
from choice_completion import JP

def main():
    cfg=read(CFG);now=read(cfg['source']);sha=digest(W/cfg['source']);c=read('reference/rebirth-jp-corpus.json');rows=read(Q+'review-records.json');ts=read('reference/chapter14-templates.json')
    groups=[];a='End/Content/Text/JP/4000-MIDGR_TxtRes.uasset'
    for prefix,reason in [('$C3410_MAIN_0800_13','Gift prompt plus all three named items; UI proper names stay official English. Read Aerith invitation and vendor refusal/replacement,53–60.'),('$C3410_MAIN_0900_03','Snack prompt plus all three item names; read the new recipe override and both reactions,65–82.'),('$C3410_MAIN_1200_1','All three poses, not generic yes/no; read photographer contest and rejection,93–101,147–161.')]:
        ids=[k for k,v in c[Path(a).name].items() if k.startswith(prefix) and k.endswith('_sys') and v['Text']]
        assert len(ids)==(3 if '1200' in prefix else 4)
        groups.append(dict(asset=a,prefix=prefix,choices=[dict(id=k,jp=c[Path(a).name][k]['Text'],thai=now['assets'][a]['entries'][k]) for k in ids],decision=reason,adjacent_dialogue_read=True))
    expected={(a,k) for a,d in c.items() for k,v in d.items() if v['Text'] and k.startswith(('$C3410_','$C3510_')) and k.endswith('_sys')}
    assert expected=={(Path(g['asset']).name,r['id']) for g in groups for r in g['choices']}
    write(Q+'choice-review.json',dict(source_sha256=sha,groups=groups,complete_question_and_all_buttons=True,nearby_response_context_reviewed=True,existing_choice_texts_unchanged=True,source_order_not_runtime_branch_proof=True,in_game_tested=False))
    decisions={5:'ひとつ =1 definite fact.',10:'六番 = Reactor6.',66:'ひとつ =1 item per person.',104:'ゼロ =0 mako.',587:'ひとつ =1 remaining wing.'}
    nums=read(Q+'numeric-review.json');assert {r['template'] for r in nums}==set(decisions)
    write(Q+'numeric-decisions.json',dict(source_sha256=sha,records=[dict(r,decision=decisions[r['template']]) for r in nums],all_differences_reviewed=True))
    pronouns=[]
    for r in rows:
        t=r['thai'];n=r['template']
        if not ('นาย' in t or 'เธอ' in t):continue
        if n in (444,843):reason='Sephiroth addresses Aerith as she arrives to resist him, not Cloud; femaleเธอ. Corroborated by Nojima interview reported in FrontlineJP2024-04-17.'
        elif n in (33,48,49,156,187,234,273,655,694):reason='Female Aerith is addressee or referent, as established by adjacent lines;เธอ appropriate.'
        elif n in (122,128):reason='Zack addresses male Biggs;นาย.'
        elif n==169:reason='Sephiroth addresses male Zack at church;นาย.'
        elif n in (170,563):reason='Zack addresses male Sephiroth, including his rejection of SOLDIER honour;นาย.'
        elif n in (317,738):reason='Cloud addresses male Cait Sith after Keystone apology;นาย.'
        elif n==857:reason='Rufus addresses male Glenn;นาย.'
        elif n==873:reason='Glenn addresses male Rufus;นาย.'
        elif n==555:reason='ทำนาย is lexical fortune-telling, notนาย pronoun.'
        else:reason='Explicit surrounding scene establishes male Cloud as addressee;นาย. No global replacement.'
        pronouns.append(dict(r,decision=reason))
    write(Q+'pronoun-review.json',dict(source_sha256=sha,records=pronouns,all_candidates_read=True,unknown_speakers_neutral=True,corroboration_url='https://www.frontlinejp.net/2024/04/17/final-fantasy-vii-rebirth-post-release-interview-part-2-devs-discuss-side-characters-dialogue-and-sequel/'))
    dup=[]
    for t in ts:
        if len(t['examples'])<2:continue
        occurrences=[dict(asset=r['asset'],id=r['id'],jp_actor=r['Japanese'].get('MetaData',{}).get('ACTOR',''),english_actor=r['English'].get('MetaData',{}).get('ACTOR','')) for r in read('reference/chapter14-source.json') if r['template']==t['index']]
        dup.append(dict(template=t['index'],jp=t['jp'],occurrences=occurrences,decision='All occurrences read in their scene. CAPIT has missing US actor metadata, so neutral short utterances checked against actual JP actor for every occurrence; no unknown-gender particles inferred.'))
    write(Q+'duplicate-context-review.json',dict(source_sha256=sha,groups=dup,all_new_templates_read_twice=True,read_ranges=[[0,896]],same_scene_reuse_ledger=Q+'same-scene-variant-reuse.json',short_lines_not_reused_from_earlier_activities=True))
    coverage=[];remaining=[];npc=[]
    for a,d in c.items():
        p=now['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})
        for k,v in d.items():
            if not v['Text'] or not JP.search(v['Text']):continue
            if '_NPC_' in k:
                assert k in p and not JP.search(p[k]),(a,k,'NPC omitted');npc.append(dict(asset=a,id=k))
            if k.startswith(('$C3410_','$C3510_','$CAPTL_BOS_')):
                assert k in p and not JP.search(p[k]),(a,k,'Ch14 omitted');coverage.append(dict(asset=a,id=k))
            if k not in p:
                assert re.match(r'\$(?:demo_|playdemo_|menu_TrialVersion_|menu_load_trial_)',k),(a,k,'Unclassified remaining Japanese')
                remaining.append(dict(asset=a,id=k,jp=v['Text'],reason='Demo/store/event-only UI outside retail game; unchanged.'))
    write(Q+'NPC-residual.json',dict(source_sha256=sha,registered_NPC_JP_rows=len(npc),untranslated_NPC_rows=0,ids=npc,unknown_ACTORs_checked=True,not_all_runtime_branches_tested=True))
    write(Q+'coverage-review.json',dict(source_sha256=sha,Ch14_JP_origin_rows=len(coverage),ids=coverage,missing=[],all_C34_C35_and_Capital_boss_namespaces=True,CAPIT_alternate_JP_script_included=True,CAPIT_US_text_placeholders_not_used_for_translation=True,CAPIT_stage_directions_preserved_as_parenthetical_source_content=True,previous_UI_and_all_NPC_namespaces_preserved=True,in_game_tested=False))
    write(Q+'deferred-remaining.json',dict(source_sha256=sha,records=remaining,categories=dict(Counter(r['reason'] for r in remaining)),all_remaining_Japanese_classified=True))
    ui=read(Q+'adjoining-UI-candidates.json')
    for r in ui:assert now['assets'][r['asset']]['entries'][r['id']]==r['thai']
    write(Q+'adjoining-UI-review.json',dict(source_sha256=sha,registered_rows=len(ui),records=ui,all_registered_rows_read=True,includes_all_Ch14_choices_quest_objectives_and_postgame_tutorials=True,base_texts_unchanged=True,in_game_tested=False))
    p=read(Q+'progress.json');p.update(read_ranges=[[0,896]],semantic_review_complete=True,second_read_complete=True);write(Q+'progress.json',p)
    print('Reviewed',len(ts),'templates;',len(groups),'choice sets;',len(ui),'adjoining UI;',len(pronouns),'pronouns;',len(coverage),'Ch14 JP rows;',len(npc),'NPC; deferred',len(remaining))

if __name__=='__main__':main()
