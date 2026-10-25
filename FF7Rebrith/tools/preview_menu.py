"""Render menu labels from working glyph assets; never a game screenshot."""
import json
from pathlib import Path
import re

import verify_chapter1 as v
from PIL import Image, ImageDraw, ImageFont
import txtres

WORK = v.WORK
STAGE = WORK / "staging/ThaiJP_Working"
QA = WORK / "qa/menu"
COMMON = "End/Content/Menu/Billboard/Common"
FONT = "U_Com_JP_SystemFontLarge"


def main():
    records, _ = v.glyphs((STAGE / COMMON / (FONT + ".uasset")).read_bytes())
    glyphs = {g[0]:g for g in records}
    entries = txtres.parse(str(STAGE / "End/Content/Text/JP/Resident_TxtRes.uasset"))
    pages = {}
    out = Image.new("RGB", (1800, 1300), "#101a2a")
    draw = ImageDraw.Draw(out)
    legend = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    draw.text((35,25), "Working menu font proof | Rendered from staged assets, not in-game", font=legend, fill="#c0d2e6")
    draw.text((35,62), "Title / Main / Pause | Original Latin glyphs + Noto Sans Thai Light (300)", font=legend, fill="#809bb9")
    measurements=[]

    def page(number):
        if number not in pages:
            p=STAGE/COMMON/f"{FONT}-{number:02d}.uasset"
            if not p.exists():p=WORK/"source"/COMMON/p.name
            pages[number]=v.atlas(p)[0].getchannel("R")
        return pages[number]

    def text(key, x, y, width, center=True, fill=(239,245,255)):
        for line_index,line in enumerate(entries[key]["Text"].splitlines()):
            line=re.sub(r"<[^>]+>","",line)
            codes=[glyphs[ord(c)] for c in line]
            advance=sum(g[8] for g in codes)
            assert advance <= width,(key,"Preview panel overflow",advance,width)
            pen=x+(width-advance)//2 if center else x
            for g in codes:
                if g[4] and g[5]:
                    mask=page(g[1]).crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
                    out.paste(fill,(pen+g[6],y+line_index*45+g[7]),mask)
                pen+=g[8]
            measurements.append(dict(id=key,line=line_index,width=advance,panel_width=width))

    panels=[
        (30,"Title screen",["$menu_title_0001_0000","$menu_title_0001_0001","$menu_title_0001_0002","$menu_title_0001_0004","$menu_title_0001_0005","$menu_title_0001_0006"]),
        (620,"Main menu",["$menu_mainmenu_0000_0000","$menu_mainmenu_0000_0001","$menu_mainmenu_0000_0002","$menu_mainmenu_0000_0003","$menu_mainmenu_0000_0006","$menu_mainmenu_0000_0007","$menu_mainmenu_0000_0008","$menu_mainmenu_0000_0010","$menu_mainmenu_0000_0011","$menu_mainmenu_0000_0018"]),
        (1210,"Pause menu",["$menu_pause_0000_0000","$menu_pause_0002_0000","$menu_pause_0002_0001","$menu_pause_0001_0001","$menu_pause_0001_0002"]),
    ]
    for x,title,keys in panels:
        draw.rounded_rectangle((x,125,x+560,870),radius=16,fill="#091221",outline="#284970",width=2)
        draw.text((x+24,145),title,font=legend,fill="#81b8e4")
        for i,key in enumerate(keys):
            top=205+i*61
            if i==1:draw.rounded_rectangle((x+12,top-7,x+548,top+47),radius=7,fill="#12427a")
            text(key,x+22,top,516)
    draw.rounded_rectangle((30,900,1770,1270),radius=16,fill="#091221",outline="#284970",width=2)
    draw.text((58,920),"Confirmation dialog",font=legend,fill="#81b8e4")
    text("$menu_pause_0004_0000",60,974,1680)
    text("$menu_pause_0004_0001",580,1210,240)
    text("$menu_pause_0004_0002",980,1210,240)
    QA.mkdir(parents=True,exist_ok=True)
    path=QA/"menu-preview.png"
    out.save(path)
    (QA/"preview-verification.json").write_text(json.dumps(dict(rendered_from_working_assets=True,in_game_screenshot=False,measurements=measurements),indent=2)+"\n",encoding="utf-8")
    print(path)


if __name__=="__main__":
    main()
