"""Render complete revised question/answer groups with staged game glyphs."""
import re,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from context_recheck import Q,decisions,digest
from preview_ch12_recheck import renderer

def main():
    ctx=read('qa/active-working-set.json');stage=W/ctx['stage'];rs=decisions();changed={(r['asset'],r['id']) for r in rs};groups=read(Q+'scene-choice-groups.json');contexts=read(Q+'all-record-contexts.json');by={(r['asset'],r['id']):r for r in contexts}
    panels=[];covered=set()
    for g in groups:
        keys=[r['id'] for r in g['records']]
        if any((g['asset'],k) in changed for k in keys):
            panels.append((f"Choice {g['index']}",g['asset'],keys));covered.update((g['asset'],k) for k in keys)
    # Semantic changes outside choice blocks: include the immediately adjacent
    # translated lines; source-order contexts are supplementary, not branch flow.
    for r in rs:
        key=r['asset'],r['id']
        if key in covered or all('Canonical' in d for d in r['decisions']):continue
        original=by[key];keys=[x['id'] for x in original['before'][-1:]]+[r['id']]+[x['id'] for x in original['after'][:1]]
        panels.append((r['id'],r['asset'],keys));covered.add(key)
    samplekeys=['$C1910_MAIN_0050_0900_00_red','$C2510_MAIN_1500_2700_00_riv','$CORLE_QST_03_0900_1000_00_dmi','$C2610_MAIN_3000_0300_00_zax','$minigame_chocoborace_chocobo06_explain']
    for k in samplekeys:
        r=next(r for r in contexts if r['id']==k);panels.append((k,r['asset'],[k]))
    data={a:txtres.parse(str(stage/a)) for label,a,keys in panels};fonts={size:renderer(stage,f'U_Com_JP_SystemFont{size}.uasset') for size in ['Large','Normal']};legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17);samples=[]
    pages=(len(panels)+3)//4
    for page in range(pages):
        pairs=[]
        for label,a,keys in panels[page*4:(page+1)*4]:
            texts=list(dict.fromkeys(re.sub('<[^>]+>','',data[a][k]['Text']).replace('\r','') for k in keys));text='\n'.join(texts);cells=[]
            for size,(gs,mask) in fonts.items():
                x=15;y=45;ops=[];bottom=100
                for ch in text:
                    if ch=='\n':x=15;y+=52;continue
                    g=gs[ord(ch)]
                    if x+g[8]>945:x=15;y+=52
                    if g[4] and g[5]:
                        m=mask(g);px=x+g[6];py=y+g[7];assert px>=0 and py>=30
                        ops.append((px,py,m));bottom=max(bottom,py+m.height+18)
                    x+=g[8]
                cell=Image.new('RGB',(960,bottom),'#17283d');ImageDraw.Draw(cell).text((10,8),size+' | '+label,font=legend,fill='#9fd8e8')
                for px,py,m in ops:assert px+m.width<=960;cell.paste((242,247,255),(px,py),m)
                cells.append(cell);samples.append(dict(label=label,asset=a,ids=keys,font=size,clipped=False))
            pairs.append(cells)
        heights=[max(c.height for c in pair) for pair in pairs];canvas=Image.new('RGB',(1960,60+sum(h+12 for h in heights)),'#091522');ImageDraw.Draw(canvas).text((15,15),f'Context review {page+1}/{pages} | Staged glyphs | Repeated prompt variants deduplicated | Illustrative, not in-game',font=legend,fill='#bfd7ed');y=55
        for pair,h in zip(pairs,heights):
            for col,cell in enumerate(pair):canvas.paste(cell,(10+980*col,y))
            y+=h+12
        canvas.save(W/Q/f'proof-{page+1}.png')
    write(Q+'proof.json',dict(source_sha256=digest(W/ctx['combined_source']),pages=pages,panels=len(panels),samples=samples,actual_staged_glyphs=True,fonts=['Large','Normal'],all_revised_choice_groups_complete=True,repeated_identical_prompt_text_deduplicated=True,source_order_neighbors_are_not_branch_flow=True,in_game_tested=False))
    print('Rendered',pages,'pages,',len(panels),'complete choice/dialogue/glossary panels')
if __name__=='__main__':main()
