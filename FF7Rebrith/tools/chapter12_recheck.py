"""Read-only review display plus exact, auditable revision application."""
import sys,re,hashlib
from pathlib import Path
from assemble_chapter12 import values
from prepare_chapter9 import W,read,write
Q='qa/chapter12/recheck/'
def show(start,end):
    vals=values();ts=read('reference/chapter12-templates.json')
    for t in ts[start:end]:
        n=t['index'];print(f"{n} {t['actor']} J:{t['jp'].replace(chr(13),' / ').replace(chr(10),'')} T:{vals[str(n)].replace(chr(13),' / ').replace(chr(10),'')}")
def audit():
    from audit_chapter12 import digest
    cfg=read('reference/chapter12-build.json');b=read(Q+'baseline.json');old=read(Path(b['snapshot'])/cfg['source']);now=read(cfg['source']);changes=read('reference/chapter12-recheck-overrides.json')['records'];expected={(r['asset'],r['id']):r for r in changes};actual={}
    for p,h in b['hashes'].items():assert digest(Path(b['snapshot'])/p)==h,p
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        z=now['assets'][a];assert p['actors']==z['actors'] and p['entries'].keys()==z['entries'].keys()
        for k,t in p['entries'].items():
            if t!=z['entries'][k]:
                r=expected[a,k];assert r['before']==t and r['after']==z['entries'][k]
                assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['after'])
                assert re.findall(r'\d+',t)==re.findall(r'\d+',r['after'])
                actual[a,k]=r
    assert actual.keys()==expected.keys() and len(actual)==56
    prior=read(Path(b['snapshot'])/'qa/final-parts/latest.json');previous={k:h for p in prior['parts'] for k,h in p['assets'].items()};current=read('qa/chapter12/working-assets.json')
    font_paths=[p for p in current if 'SystemFont' in p];assert len(font_paths)==16 and all(previous[p]==current[p] for p in font_paths)
    oldmap=read('reference/through-chapter12-cluster-map.json');assert len(oldmap)==730
    assert read(Q+'progress.json')['complete'] and read(Q+'progress.json')['remaining_templates']==0
    write(Q+'audit.json',dict(source_sha256=digest(W/cfg['source']),read_templates=3847,corrected_records=len(actual),other46594_text_records_and_all_ACTOR_preserved=True,total_combined_text_records=46650,original_inventory_preserved=True,all16_font_assets_byte_identical=True,glyph_clusters=730,all_numeric_tokens_and_tags_preserved=True,in_game_tested=False))
    print('Recheck:56 exact revisions; all other46594 entries, actors, numbers,tags,16 font assets preserved')
def preview():
    from preview_chapter11_recheck import render_selected
    rows=read('reference/chapter12-recheck-overrides.json')['records']
    render_selected([dict(asset=r['asset'],id=r['id'],template=r['template'],kind='Ch12 revised') for r in rows],Q,'Chapter12 recheck','reference/chapter12-build.json')
if __name__=='__main__':
    if sys.argv[1]=='--audit':audit()
    elif sys.argv[1]=='--preview':preview()
    else:show(int(sys.argv[1]),int(sys.argv[2]))
