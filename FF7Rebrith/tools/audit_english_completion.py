"""Verify every completed English/notation disposition against current staging."""
import hashlib,re
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres

def main():
    q=read('qa/context-full-read/queue.json')[32841:]
    report=read('qa/context-full-read/english-completion-review.json')
    ctx=read('qa/active-working-set.json'); source=read(ctx['combined_source'])
    assert report['total']==len(q)==len(report['records'])==7850
    assert len({(r['asset'],r['id']) for r in report['records']})==7850
    reverse=str.maketrans({v:k for k,v in read(ctx['cluster_map']).items()})
    parsed={};revised=0
    for old,r in zip(q,report['records']):
        assert all(old[k]==r[k] for k in ['index','asset','id','jp','us'])
        a=r['asset'];k=r['id']
        if a not in parsed:
            parsed[a]=(txtres.parse(str(W/'source'/a)),txtres.parse(str(W/'source'/a.replace('/JP/','/US/'))),txtres.parse(str(W/ctx['stage']/a)))
        jp,us,stage=parsed[a]
        assert jp[k]['Text']==r['jp'] and us[k]['Text']==r['us']
        assert r['after']==source['assets'][a]['entries'][k]==stage[k]['Text'].translate(reverse),(k,'Disposition lost')
        assert r['decision']
        revised+=r['before']!=r['after']
        if k.startswith('$GC_PC_'):
            assert re.search('[\u0e00-\u0e7f]',r['after']) and not any(c in r['after'] for c in '≥≤')
            assert re.findall(r'\d+',r['before'])==re.findall(r'\d+',r['after'])
    assert revised==report['revised_records']==137
    resident=source['assets']['End/Content/Text/JP/Resident_TxtRes.uasset']['entries']
    # Catch the original uppercase-Help classifier defect and prose accidentally
    # treated as an official English item name.
    assert all(re.search('[\u0e00-\u0e7f]',t) for k,t in resident.items() if 'help' in k.lower())
    required={'$status_icon_name_009':'Wall','$status_icon_name_037':'Auto-Life','$status_icon_name_038':'Darkness','$menu_options_keyboard_action_0049':'ATB Boost','$menu_camera_photoframe_default_03':'Best Buds','$level_sys_hookrope_to_jump':'กระโดด','$menu_options_keyboard_minigame_runwild_action_11':'กระโดด'}
    for k,t in required.items():assert resident[k]==t,k
    progress=read('qa/context-full-read/progress.json')
    assert progress['semantic_review_complete'] and progress['remaining_records']==0
    write('qa/context-full-read/english-completion-audit.json',dict(source_sha256=hashlib.sha256((W/ctx['combined_source']).read_bytes()).hexdigest(),verified_records=7850,revised_records=137,independent_JP_US_staged_readback=True,all_help_descriptions_Thai=True,conditions_and_literal_numbers_verified=True,method=report['method'],in_game_tested=False))
    print('English/notation completion verified:7850 dispositions,137 corrections; all help descriptions Thai.')

if __name__=='__main__':main()
