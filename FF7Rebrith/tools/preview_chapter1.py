"""Render real staged font glyphs and subtitles; this is not a game screenshot."""
import json
import re

import verify_chapter1 as v
from PIL import Image, ImageDraw, ImageFont
import txtres

WORK = v.WORK
COMMON = "End/Content/Menu/Billboard/Common"
FONT = "U_Com_JP_SystemFontLarge"


def main():
    records, _ = v.glyphs((v.STAGE / COMMON / (FONT + ".uasset")).read_bytes())
    glyph = {g[0]: g for g in records}
    pages = {}

    def page(number):
        if number not in pages:
            rel = COMMON + f"/{FONT}-{number:02d}.uasset"
            path = v.STAGE / rel
            if not path.exists():
                path = WORK / "source" / rel
            pages[number] = v.atlas(path)[0]
        return pages[number]

    output = Image.new("RGB", (1400, 780), "#111a24")
    draw = ImageDraw.Draw(output)
    label_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19)
    draw.text((38, 22), "Chapter 1 font proof | Rendered from staged assets, not an in-game screenshot", fill="#b8c9db", font=label_font)
    draw.text((38, 52), "Original English glyphs + Noto Sans Thai Light (300)", fill="#91a5bb", font=label_font)

    def text_line(text, y, fill=(244, 246, 250)):
        text = re.sub(r"<[^>]+>", "", text)
        codes = [glyph[ord(ch)] for ch in text]
        x = (output.width - sum(g[8] for g in codes)) // 2
        for g in codes:
            if g[4] and g[5]:
                mask = page(g[1]).getchannel("R").crop((g[2], g[3], g[2] + g[4], g[3] + g[5]))
                output.paste(fill, (x + g[6], y + g[7]), mask)
            x += g[8]

    all_text = {}
    edits = json.loads((WORK / "translations/chapter1-th.json").read_text(encoding="utf-8"))
    for asset in edits["assets"]:
        all_text.update(txtres.parse(str(v.STAGE / asset)))
    keys = ["$C1910_MAIN_0100_0300_00_mma", "$C1910_MAIN_0700_2200_00_cld", "$C1910_MAIN_3000_0800_00_tif"]
    for n, key in enumerate(keys):
        entry = all_text[key]
        y = 140 + n * 205
        draw.rounded_rectangle((30, y - 15, 1370, y + 165), radius=14, fill="#0a1018", outline="#25394f", width=1)
        text_line(entry["MetaData"]["ACTOR"], y, (172, 207, 241))
        for line_number, line in enumerate(entry["Text"].splitlines()):
            text_line(line, y + 52 + line_number * 47)
    path = v.QA / "subtitle-preview.png"
    output.save(path)
    print(f"Saved staged-font proof: {path}")


if __name__ == "__main__":
    main()
