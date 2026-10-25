"""Compare Thai candidates with real game bitmap glyphs at their line size."""
import io
import json
from pathlib import Path
import struct
import sys

import build_prototype as b
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WORK = b.WORK


def main():
    for family in ("NotoSansThai", "NotoSansThaiLooped"):
        variable = TTFont(WORK / f"tools/fonts/{family}-Variable.ttf")
        font = instantiateVariableFont(variable, {"wght": 400, "wdth": 100}, inplace=False)
        font.save(WORK / f"tools/fonts/{family}-Regular.ttf")
    source = WORK / "source/End/Content/Menu/Billboard/Common/U_Com_JP_SystemFontNormal4K.uasset"
    data = source.read_bytes()
    end = b.header_end(data)
    n = struct.unpack_from("<I", data, end + 6)[0]
    glyphs = {g[0]: g for g in [struct.unpack_from("<6H2hH", data, end + 10 + i * 18) for i in range(n)]}
    size = struct.unpack_from("<I", data, len(data) - 12)[0]
    pages = {}
    for page in {glyphs[ord(c)][1] for c in "Cloud Sephiroth Tifa 早く来いクラウド" if ord(c) in glyphs}:
        tex = source.with_name(source.stem + f"-{page:02d}.uasset").read_bytes()
        mips = b.mip_layout(tex, b.header_end(tex))
        raw = b"".join(tex[o:o+s] for o,w,h,s in mips)
        pages[page] = Image.open(io.BytesIO(b.dds_header(mips[0][1],mips[0][2],len(mips))+raw)).convert("RGB")
    canvas = Image.new("RGB", (1500, 680), (20, 26, 34))
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
    draw.text((35,18),"Font comparison - extracted game glyphs and Thai candidates (not an in-game screenshot)",font=label_font,fill="white")
    for text,y in [("Cloud  Sephiroth  Tifa",105),("早く来い　クラウド",220)]:
        draw.text((35,y-42),"Original JP SystemFont",font=label_font,fill=(161,180,200))
        x=35
        for c in text:
            g=glyphs.get(ord(c))
            if not g:
                x+=size//2
                continue
            code,page,gx,gy,gw,gh,left,top,advance=g
            mask=pages[page].getchannel("R").crop((gx,gy,gx+gw,gy+gh))
            canvas.paste("white",(x+left,y+top),mask)
            x+=advance
    families=[("Sarabun",WORK/"tools/fonts/Sarabun-Regular.ttf"),
              ("Noto Sans Thai",WORK/"tools/fonts/NotoSansThai-Regular.ttf"),
              ("Noto Sans Thai Looped",WORK/"tools/fonts/NotoSansThaiLooped-Regular.ttf")]
    thai="คลาวด์ รีบมาได้แล้ว  ทีฟ่า  เซฟิรอธ"
    for (label,font),y in zip(families,(340,450,560)):
        draw.text((35,y-36),label+" Regular",font=label_font,fill=(161,180,200))
        b.FONT=font
        mask,left,top,advance=b.raster_cluster(thai,round(size*1.15))
        canvas.paste("white",(35+left,y+size+top),mask)
    canvas.save(WORK/"qa/font-comparison.png")
    print(f"Original font line size: {size}px; comparison saved")


if __name__=="__main__":
    main()
