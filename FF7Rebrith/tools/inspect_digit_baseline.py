"""Measure the observed mismatch using original numerals and staged Thai ink."""
import json
import struct
import verify_chapter1 as v

common = "End/Content/Menu/Billboard/Common"
cmap = json.loads((v.WORK / "reference/chapter1-cluster-map.json").read_text(encoding="utf-8"))
for path in sorted((v.STAGE / common).glob("U_Com_JP_SystemFont*.uasset")):
    if "-" in path.name:
        continue
    records, _ = v.glyphs(path.read_bytes())
    lookup = {g[0]: g for g in records}
    pages = {}
    def bottom(g):
        if g[1] not in pages:
            texture = path.with_name(path.stem + f"-{g[1]:02d}.uasset")
            if not texture.exists():
                texture = v.WORK / "source" / common / texture.name
            pages[g[1]] = v.atlas(texture)[0].getchannel("R")
        mask = pages[g[1]].crop((g[2], g[3], g[2]+g[4], g[3]+g[5]))
        box = mask.point(lambda p: 255 if p >= 64 else 0).getbbox()
        return g[7] + box[3]
    thai = bottom(lookup[ord(cmap["ก"])])
    print(path.stem, "Thai bottom", thai,
          "original digit bottoms", {d: bottom(lookup[ord(d)]) for d in "0123456789"})
