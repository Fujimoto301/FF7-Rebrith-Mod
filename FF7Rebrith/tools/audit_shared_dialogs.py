"""Persistent regression gate for shared early-game tutorial/choice UI families."""
import hashlib,re
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write,txtres,JP
from prepare_ch12_recheck import family
from chapter6_activity_ui import selected as costa_selected
from prepare_ch1_6_recheck import ui_family,dialogue_decision
from extend_ch1_6_recheck import selected as extra_selected

def main():
    ctx=read('qa/active-working-set.json')
    if ctx.get('chapter14'):
        assert ctx['combined_source']==read('reference/chapter14-build.json')['source']
        from audit_chapter14 import main as audit_current_chapter14
        audit_current_chapter14()
    elif ctx.get('chapter13'):
        assert ctx['combined_source']==read('reference/chapter13-build.json')['source']
        from audit_chapter13 import main as audit_current_chapter13
        audit_current_chapter13()
        if (W/'reference/chapter13-recheck-overrides.json').exists():
            from chapter13_recheck import audit as audit_chapter13_recheck
            audit_chapter13_recheck()
    elif ctx.get('chapter12'):
        assert ctx['combined_source']==read('reference/chapter12-build.json')['source']
        from audit_chapter12 import main as audit_current_chapter12
        audit_current_chapter12()
        if (W/'reference/chapter12-recheck-overrides.json').exists():
            from chapter12_recheck import audit as audit_chapter12_recheck
            audit_chapter12_recheck()
    elif ctx.get('chapter11'):
        assert ctx['combined_source']==read('reference/chapter11-build.json')['source']
        from audit_chapter11 import main as audit_current_chapter11
        audit_current_chapter11()
        if (W/'qa/chapter11/recheck/baseline.json').exists():
            from chapter11_recheck import audit as audit_chapter11_recheck
            audit_chapter11_recheck()
        if (W/'qa/pronoun-context/baseline.json').exists():
            from pronoun_context import audit as audit_pronouns
            audit_pronouns()
    elif ctx.get('chapter10'):
        if ctx['combined_source']==read('reference/chapter10-build.json')['source']:
            from audit_chapter10 import main as audit_current_chapter10
            audit_current_chapter10()
            if (W/'qa/chapter10/recheck/current.json').exists():
                from audit_chapter10_recheck import main as audit_current_recheck
                audit_current_recheck()
        else:
            raise AssertionError('Add a Chapter10 regression gate before a later chapter is published')
    if ctx.get('enemy_actions'):
        if ctx['combined_source']==read('reference/enemy-actions-build.json')['source']:
            from enemy_actions import audit as audit_enemy_actions
        else:
            from audit_enemy_actions_regression import main as audit_enemy_actions
        audit_enemy_actions()
    if ctx.get('choice_completion') and not ctx.get('npc_recheck'):
        from choice_completion import family as choice_family,musical_notation
        # Reparse the complete source and stage before publishing, including scene choices.
        from audit_choice_completion import main as audit_all_choices
        audit_all_choices()
    if ctx.get('npc_recheck'):
        from choice_completion import family as choice_family,musical_notation
        if ctx['combined_source']==read('reference/npc-recheck-build.json')['source']:
            from audit_npc_recheck import main as audit_current_NPC
        else:
            from audit_npc_regression import main as audit_current_NPC
        audit_current_NPC()
    ch7=7 in ctx.get('chapters',[])
    ch8=8 in ctx.get('chapters',[])
    ch9=9 in ctx.get('chapters',[])
    if ch9:
        from prepare_chapter9 import ui as ch9_family,shared as ch9_speech,defer as ch9_defer
    if ch8:
        from chapter8_supplement import family as ch8_family
    if ch7:
        from chapter7_supplement import family as ch7_family
    assert 'combined_source' in ctx and 'cluster_map' in ctx,'Set the current combined source and glyph map in active-working-set before this audit'
    now=read(ctx['combined_source']);cmap=read(ctx['cluster_map']);reverse=str.maketrans({v:k for k,v in cmap.items()})
    asset='End/Content/Text/JP/Resident_TxtRes.uasset'
    source=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    staged=txtres.parse(str(W/ctx['stage']/asset));categories=Counter();ids=[]
    for k,v in source.items():
        group=family(k) or ('Costa_activity_UI' if costa_selected(k) else None) or ui_family(k) or ('adjoining_Fort_Condor_quest_and_shop_UI' if extra_selected(k) else None)
        if ch7:group=group or ch7_family(k)
        if ch8:group=group or ch8_family(k)
        if ch9:group=group or ch9_family(k)
        if ctx.get('choice_completion'):group=group or choice_family('Resident_TxtRes.uasset',k)
        if not group or not v['Text']:continue
        if not JP.search(v['Text']):continue
        assert k in now['assets'][asset]['entries'],(k,'Shared tutorial/choice UI missing')
        text=now['assets'][asset]['entries'][k]
        assert (not JP.search(text) or ctx.get('choice_completion') and musical_notation(k,text)) and text.strip(),k
        assert staged[k]['Text'].translate(reverse)==text,k
        assert re.findall('</?[^>]+>',text)==re.findall('</?[^>]+>',v['Text']),k
        categories[group]+=1;ids.append(k)
    assert all(k in ids for k in ['$minigame_cardgame_tutorial_Check','$minigame_cardgame_tutorial_YES','$minigame_cardgame_tutorial_NO'])
    shared_speech=[]
    ch7_speech={r['id'] for r in read('reference/chapter7-supplement-source.json') if r['asset']==asset and r['family']=='speech'} if ch7 else set()
    if ch7:ch7_speech.update(r['id'] for r in read('reference/chapter7-source.json') if r['asset']==asset)
    if ch8:ch7_speech.update(r['id'] for r in read('reference/chapter8-supplement-source.json') if r['asset']==asset and r['family']=='speech')
    if ch9:ch7_speech.update(k for k,v in source.items() if v['Text'] and ch9_speech(k) and not ch9_defer(k))
    for k,v in source.items():
        decision=dialogue_decision(k)
        if not v['Text'] or not (decision and decision[0]=='include' or k in ch7_speech):continue
        assert k in now['assets'][asset]['entries'],(k,'Shared NPC/system dialogue missing')
        assert staged[k]['Text'].translate(reverse)==now['assets'][asset]['entries'][k]
        shared_speech.append(k)
    # This gate follows the active set, so a later chapter cannot silently reset dots.
    import verify_chapter1 as v
    common=Path('End/Content/Menu/Billboard/Common');punctuation=[]
    for path in sorted((W/ctx['stage']/common).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        gs={g[0]:g for g in v.glyphs(path.read_bytes())[0]};pages={}
        def bottom(g):
            if g[1] not in pages:
                p=path.with_name(path.stem+f'-{g[1]:02d}.uasset')
                if not p.exists():p=W/'source'/common/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            box=pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5])).point(lambda p:255 if p>=64 else 0).getbbox()
            assert box
            return g[7]+box[3]
        assert bottom(gs[8230])==bottom(gs[ord('.')]),(path.name,'Ellipsis baseline regressed')
        punctuation.append(dict(font=path.name,ellipsis_matches_native_full_stop=True))
    assert len(punctuation)==8
    write('qa/shared-dialogs/latest.json',dict(combined_source=ctx['combined_source'],stage=ctx['stage'],
      source_sha256=hashlib.sha256((W/ctx['combined_source']).read_bytes()).hexdigest(),
      verified_JP_origin_records=len(ids),families=dict(categories),verified_ids=ids,missing=[],ellipsis_fonts=punctuation,
      verified_shared_NPC_or_system_records=len(shared_speech),shared_speech_ids=shared_speech,
      rule='At each new chapter, identify and add newly introduced activity/UI families to this gate. Check whole question/yes-no/cancel/retry/entry/HUD/instructions families, not only scene *_sys IDs.',
      limit='Coverage of registered families; not a claim that all minigames or late-return content in the game are translated.',runtime_tested=False))
    print('Shared-dialog gate passed:',len(ids),'Japanese-source UI records;',dict(categories))

if __name__=='__main__':main()
