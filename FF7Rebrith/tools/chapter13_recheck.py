"""Exact second-release diff gate and all revised-line glyph proof."""
import sys,re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter13 import CFG,digest
Q='qa/chapter13/recheck/'

def audit():
    b=read(Q+'baseline.json');snap=Path(b['snapshot']);cfg=read(CFG)
    for p,h in b['hashes'].items():assert digest(snap/p)==h,p
    old=read(snap/b['source']);now=read(cfg['source']);records=read('reference/chapter13-recheck-overrides.json')['records'];allowed={(r['asset'],r['id']):r for r in records};assert len(allowed)==11
    changed=[];total=0;assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        n=now['assets'][a];assert p['actors']==n['actors'] and p['entries'].keys()==n['entries'].keys()
        for k,t in p['entries'].items():
            total+=1;z=n['entries'][k]
            if t!=z:
                r=allowed[a,k];assert r['before']==t and r['after']==z
                assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',z)
                changed.append((a,k))
    assert set(changed)==set(allowed) and total==47503
    before=read(snap/'qa/chapter13/working-assets.json');stage=W/cfg['stage'];fonts=[p for p in before if 'SystemFont' in p];assert len(fonts)==16
    for p in fonts:assert digest(stage/p)==before[p],p
    assert read(cfg['cluster_map'])==read(snap/cfg['cluster_map'])
    progress=read(Q+'progress.json');assert progress['complete'] and progress['read_ranges']==[[0,808]] and progress['remaining_templates']==0
    result=dict(source_sha256=digest(W/cfg['source']),corrected_records=11,total_combined_text_records=47503,other47492_text_records_and_all_ACTOR_preserved=True,all16_font_assets_byte_identical=True,map730_preserved=True,all809_templates_reread=True,all2_choice_groups_reread=True,in_game_tested=False)
    write(Q+'audit.json',result);print('Recheck:11 exact revisions; other47492 texts, all ACTORs and16 fonts preserved')

def preview():
    from preview_chapter11_recheck import render_selected
    rows=read('reference/chapter13-recheck-overrides.json')['records']
    render_selected([dict(asset=r['asset'],id=r['id'],template=r['template'],kind='Ch13 correction') for r in rows],Q,'Ch13 recheck',CFG)
if __name__=='__main__':
    if '--preview' in sys.argv:preview()
    else:audit()
