"""Render Chapter 5 subtitles and runtime substitutions from actual staged glyphs."""
import json,re,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import verify_chapter1 as v
W=v.WORK;STAGE=W/'staging/ThaiJP_ThroughChapter5_Working';QA=W/'qa/chapter5'
COMMON=Path('End/Content/Menu/Billboard/Common')

def main(gender_recheck=False):
    rows=json.loads((W/'reference/chapter5-source.json').read_text('utf-8'))
    parsed={a:v.txtres.parse(str(STAGE/a)) for a in {r['asset'] for r in rows}}
    samples=[]
    indices=(18,25,88,98,153,367,382,418,450,584,638,676,744,806,1060,1206)
    for index in indices:
        r=next(r for r in rows if r["template"]==index);samples.append((f"Ch.5 #{index} | "+r['id'].rsplit('_',1)[-1],parsed[r['asset']][r['id']]['Text']))
    resident=v.txtres.parse(str(STAGE/'End/Content/Text/JP/Resident_TxtRes.uasset'))
    samples.append(('Native ASCII injected after encoding',resident['$sys_item_drop']['Text'].replace('<object=0>','Ether')))
    samples.append(('Native counts / EXP / AP',resident['$sys_get_exp_ap']['Text'].replace('<count=0>','1072').replace('<count=1>','12')))
    out=Image.new('RGB',(2000,70+len(samples)*230),'#0a1523');draw=ImageDraw.Draw(out)
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
    draw.text((25,15),'Chapter 5 | Actual staged glyphs | Proof wrapping only | Not in-game footage',font=legend,fill='#bad3e8')
    report=[]
    for col,size in enumerate(('Large','Normal')):
        stem='U_Com_JP_SystemFont'+size
        mapping={g[0]:g for g in v.glyphs((STAGE/COMMON/(stem+'.uasset')).read_bytes())[0]};pages={}
        def mask(g):
            if g[1] not in pages:
                p=STAGE/COMMON/f'{stem}-{g[1]:02d}.uasset'
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
        for row,(label,text) in enumerate(samples):
            left=20+col*990;top=65+row*230
            draw.rounded_rectangle((left,top,left+970,top+215),radius=10,fill='#13243a',outline='#31516b')
            draw.text((left+15,top+8),size+' | '+label,font=legend,fill='#94d2eb')
            text=re.sub('<[^>]+>','',text);pen=left+15;y=top+42;bottom=y;line=0
            for ch in text:
                if ch=='\r':continue
                if ch=='\n':pen=left+15;y+=48;line+=1;continue
                assert ord(ch) in mapping,(size,ch)
                g=mapping[ord(ch)]
                if pen+g[8]>left+950:pen=left+15;y+=48;line+=1
                if g[4] and g[5]:out.paste((238,245,253),(pen+g[6],y+g[7]),mask(g));bottom=max(bottom,y+g[7]+g[5])
                pen+=g[8]
            assert bottom<top+210,(size,label,'Proof overflow')
            report.append(dict(font=size,sample=label,lines=line+1,clipped=False))
    target=QA/'gender-recheck' if gender_recheck else QA
    out.save(target/'font-proof.png')
    (target/'font-proof.json').write_text(json.dumps(dict(actual_staged_glyphs=True,runtime_ascii_substituted_after_encoding=True,
        in_game_screenshot=False,preview_only_wrap=True,samples=report),indent=2)+'\n','utf-8')
    print(target/'font-proof.png')
if __name__=='__main__':main(gender_recheck='--gender-recheck' in sys.argv)
