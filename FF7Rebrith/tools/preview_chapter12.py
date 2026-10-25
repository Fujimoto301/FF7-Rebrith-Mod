"""Complete Ch12 choice sets and representative actual encoded font proof."""
import re,math,hashlib
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/chapter12-build.json');stage=W/cfg['stage'];rows=read('qa/chapter12/review-records.json');by={r['template']:r for r in rows};now=read(cfg['source']);corpus=read('reference/rebirth-jp-corpus.json')
    groups=read('qa/chapter12/choice-groups-expanded.json')['groups']
    selected=[]
    for g in groups:
        for r in g['choices']:r['thai']=now['assets'][g['asset']]['entries'][r['id']]
        selected.append(dict(asset=g['asset'],id=g['choices'][0]['id'],ids=[r['id'] for r in g['choices']],template=g['prefix'],actor='UI'))
    write('qa/chapter12/choice-review.json',dict(groups=groups,complete_question_and_all_buttons=True,nearby_response_context_reviewed=True,additional_groups_beyond_dialogue_groups=3,source_order_not_runtime_branch_proof=True,in_game_tested=False))
    selected += [by[n] for n in [42,52,218,663,904,977,1140,1161,1216,1255,1303,1336,1353,1528,2398,2560,2765,3414,3728,3734,3762,3781,3805,3844]]
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);report=[]
    data={a:txtres.parse(str(stage/a)) for a in {r['asset'] for r in selected}}
    fonts={size:renderer(stage,f'U_Com_JP_SystemFont{size}.uasset') for size in ['Large','Normal']}
    for page in range(math.ceil(len(selected)/4)):
        pairs=[]
        for r in selected[page*4:(page+1)*4]:
            cells=[]
            for size,(gs,mask) in fonts.items():
                text=re.sub('<[^>]+>','','\r\n'.join(data[r['asset']][k]['Text'] for k in r.get('ids',[r['id']]))).replace('\r','');ops=[];pen=14;y=42;bottom=130
                for ch in text:
                    if ch=='\n':pen=14;y+=55;continue
                    assert ord(ch) in gs,(r['id'],ch)
                    g=gs[ord(ch)]
                    if pen+g[8]>946:pen=14;y+=55
                    if g[4] and g[5]:
                        x=pen+g[6];yy=y+g[7];assert x>=0 and x+g[4]<=960 and yy>=30,(r['id'],'clip');ops.append((x,yy,mask(g)));bottom=max(bottom,yy+g[5]+18)
                    pen+=g[8]
                cell=Image.new('RGB',(960,bottom),'#17283d');dr=ImageDraw.Draw(cell);dr.text((10,8),size+' | '+str(r['template'])+' | '+r['actor'],font=legend,fill='#9fd8e8')
                for x,y,m in ops:cell.paste((242,247,255),(x,y),m)
                cells.append(cell);report.append(dict(id=r['id'],template=r['template'],font=size,clipped=False))
            pairs.append(cells)
        heights=[max(x.height for x in cs) for cs in pairs];canvas=Image.new('RGB',(1960,60+sum(h+12 for h in heights)),'#091522');dr=ImageDraw.Draw(canvas)
        dr.text((15,15),'Chapter12 | Actual staged glyphs | Illustrative wrapping and font selection | Not in-game',font=legend,fill='#bfd7ed');y=55
        for cs,h in zip(pairs,heights):
            for col,cell in enumerate(cs):canvas.paste(cell,(10+col*980,y))
            y+=h+12
        canvas.save(W/f'qa/chapter12/proof-{page+1}.png')
    cm=read(cfg['cluster_map']);seed=read(cfg['seed']);new=[k for k in cm if k not in seed]
    canvas=Image.new('RGB',(1960,1100),'#17283d');dr=ImageDraw.Draw(canvas);dr.text((15,10),'Chapter12 | Nine new clusters | Eight staged fonts | Not in-game',font=legend,fill='#bfd7ed');y=80
    for p in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        gs,mask=renderer(stage,p.name);dr.text((15,y),p.name,font=legend,fill='#9fd8e8');x=570
        for cluster in new:
            g=gs[ord(cm[cluster])]
            if g[4] and g[5]:canvas.paste((242,247,255),(x+g[6],y+g[7]),mask(g))
            x+=125
        y+=125
    canvas.save(W/'qa/chapter12/proof-16.png')
    write('qa/chapter12/proof.json',dict(source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),actual_staged_glyphs=True,samples=report,complete_choice_groups=len(groups),pages=16,new_clusters=new,all8_fonts_new_cluster_sheet=True,illustrative_wrapping=True,in_game_tested=False))
    print('Rendered16 pages;',len(groups),'complete choice sets;',len(selected),'samples')
if __name__=='__main__':main()
