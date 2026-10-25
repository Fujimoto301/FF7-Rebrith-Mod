"""Build a local 39-caption JP-audio subtitle prototype.

Thai grapheme clusters are shaped with HarfBuzz/FreeType into private-use
bitmap glyphs. Existing font glyphs and compressed texture blocks are kept.
This does not copy PlearnGaming font assets or their dialogue translation.
"""
from pathlib import Path
import io
import json
import math
import struct
import string
import subprocess
import sys
import unicodedata

WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
sys.path[:0] = [str(ROOT / "tools/python-libs"), str(ROOT / "tools"), str(WORK / "tools/cutscene-tool/1.0")]
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import freetype
import uharfbuzz as hb
from rectpack import newPacker, MaxRectsBssf
from inspect_reference_mods import fstring, number
import txtres

FONT = WORK / "tools/fonts/Sarabun-Regular.ttf"
STAGE = WORK / "staging/ThaiJP_Prototype_P"
QA = WORK / "qa"


def header_end(data):
    h = struct.unpack_from("<15i", data)
    return h[13] + h[14]


def with_body(data, body):
    end = header_end(data)
    head = bytearray(data[:end])
    export_offset = struct.unpack_from("<i", data, 44)[0]
    old_size = struct.unpack_from("<Q", data, export_offset + 8)[0]
    if old_size != len(data) - end:
        raise ValueError("Expected exactly one inline export")
    struct.pack_into("<Q", head, export_offset + 8, len(body))
    return bytes(head) + body


def split_clusters(text):
    out = []
    for ch in text:
        is_mark = unicodedata.category(ch).startswith("M") or ch == "ำ"
        if is_mark and out and "\u0e01" <= out[-1][0] <= "\u0e5b":
            out[-1] += ch
        else:
            out.append(ch)
    return out


def write_string(value):
    raw = value.encode("utf-16-le")
    return struct.pack("<i", -(len(raw) // 2 + 1)) + raw + b"\0\0" if value else b"\0" * 4


def patch_text(source, translations, cmap):
    data = source.read_bytes()
    names = txtres.read_names(data)
    # Read the supplied game's actual 2-byte property header and Language.
    stream = io.BytesIO(data)
    stream.seek(header_end(data) + 2)
    if fstring(stream) != "JP" or number(stream, "I") != 0:
        raise ValueError("Unexpected Language property layout")
    count_pos = stream.tell()
    count = number(stream, "I")
    body = bytearray(data[header_end(data):count_pos + 4])
    seen = set()
    for _ in range(count):
        start = stream.tell()
        key = fstring(stream)
        text_pos = stream.tell()
        original = fstring(stream)
        text_end = stream.tell()
        nmeta = number(stream, "I")
        for _ in range(nmeta):
            number(stream, "I")
            number(stream, "I")
            fstring(stream)
        stop = stream.tell()
        if key not in translations:
            body.extend(data[start:stop])
            continue
        encoded = "".join(cmap.get(part, part) for part in split_clusters(translations[key]))
        body.extend(data[start:text_pos] + write_string(encoded) + data[text_end:stop])
        seen.add(key)
    if stream.tell() != len(data) or seen != set(translations):
        raise ValueError("Translation keys or export boundary mismatch")
    return with_body(data, body)


def raster_cluster(cluster, size):
    face = freetype.Face(str(FONT))
    face.set_pixel_sizes(0, size)
    hfont = hb.Font(hb.Face(FONT.read_bytes()))
    hfont.scale = (size * 64, size * 64)
    hb.ot_font_set_funcs(hfont)
    buf = hb.Buffer()
    buf.add_str(cluster)
    buf.guess_segment_properties()
    hb.shape(hfont, buf)
    pieces, pen = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        face.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER)
        bitmap = face.glyph.bitmap
        x = round((pen + pos.x_offset) / 64) + face.glyph.bitmap_left
        y = -round(pos.y_offset / 64) - face.glyph.bitmap_top
        if bitmap.width and bitmap.rows:
            raw = bytes(bitmap.buffer)
            img = Image.frombytes("L", (bitmap.width, bitmap.rows), raw, "raw", "L", abs(bitmap.pitch))
            pieces.append((x, y, img))
        pen += pos.x_advance
    left = min(x for x, y, img in pieces) - 2
    top = min(y for x, y, img in pieces) - 2
    right = max(x + img.width for x, y, img in pieces) + 2
    bottom = max(y + img.height for x, y, img in pieces) + 2
    canvas = Image.new("L", (right - left, bottom - top))
    for x, y, img in pieces:
        box = (x - left, y - top, x - left + img.width, y - top + img.height)
        canvas.paste(ImageChops.lighter(canvas.crop(box), img), box)
    return canvas, left, top, round(pen / 64)


def dds_header(width, height, mips):
    return (b"DDS " + struct.pack("<7I", 124, 0xA1007, height, width, width * height, 0, mips)
            + b"\0" * 44 + struct.pack("<8I", 32, 4, int.from_bytes(b"DX10", "little"), 0, 0, 0, 0, 0)
            + struct.pack("<5I", 0x401008, 0, 0, 0, 0) + struct.pack("<5I", 83, 3, 0, 1, 0))


def mip_layout(data, body_offset):
    # This build uses 118 bytes before the inline BC5 mip and 36-byte tails.
    width, height = struct.unpack_from("<2I", data, body_offset + 8)
    at = body_offset + 118
    out = []
    for level in range(int(math.log2(max(width, height))) + 1):
        size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
        out.append((at, width, height, size))
        if data[at + size:at + size + 8] != struct.pack("<2I", max(4, width), max(4, height)):
            raise ValueError(f"Unexpected texture mip boundary at level {level}, expected {width}x{height}, got {data[at + size:at + size + 12].hex()}")
        at += size + 36
        width, height = max(1, width // 2), max(1, height // 2)
    return out


def patch_font(path, cmap, allow_expand=False, scale_override=None, align_digits=False, align_latin=False):
    data = path.read_bytes()
    end = header_end(data)
    glyph_start = 10 if data[end:end + 2] == b"\1\11" else 12
    count = struct.unpack_from("<I", data, end + glyph_start - 4)[0]
    glyphs = [struct.unpack_from("<6H2hH", data, end + glyph_start + i * 18) for i in range(count)]
    if any(g[0] in {ord(v) for v in cmap.values()} for g in glyphs):
        raise ValueError("Private-use glyph collision")
    page = max(g[1] for g in glyphs)
    page_glyphs = [g for g in glyphs if g[1] == page]
    last_row = max(g[3] for g in page_glyphs)
    row_end = max(g[2] + g[4] for g in page_glyphs if g[3] + g[5] > last_row)
    ystart = ((last_row + 3) // 4) * 4
    xstart = ((row_end + 11) // 4) * 4
    fontsize, outline = struct.unpack_from("<2I", data, len(data) - 12)
    scale = 0.8 if path.stem.endswith("Large4K") and not path.stem.endswith("XLarge4K") else 1.15
    if path.stem.endswith("XLarge"):
        scale = 0.9
    if scale_override is not None:
        scale = scale_override
    size = round(fontsize * scale)
    digit_keys = {k for k in cmap if len(k) == 1 and k in "0123456789"} if align_digits else set()
    latin_keys = {k for k in cmap if len(k) == 1 and k in string.ascii_letters} if align_latin else set()
    rasters = [(k, *raster_cluster(k, size)) for k in cmap if k not in digit_keys | latin_keys]
    rasters.sort(key=lambda r: -r[1].height)
    texpath = path.with_name(path.stem + f"-{page:02d}.uasset")
    texture = texpath.read_bytes()
    mipmap = mip_layout(texture, header_end(texture))
    packed = b"".join(texture[o:o + sz] for o, w, h, sz in mipmap)
    texw, texh = mipmap[0][1:3]
    atlas = Image.open(io.BytesIO(dds_header(texw, texh, len(mipmap)) + packed)).convert("RGB")
    bottom = ((max(g[3] + g[5] for g in page_glyphs) + 11) // 4) * 4
    regions = []
    if xstart < texw - 4 and bottom - ystart > 8:
        regions.append((xstart, ystart, texw - 4 - xstart, bottom - ystart - 4))
    regions.append((4, bottom, texw - 8, texh - 4 - bottom))
    packer = newPacker(rotation=False, pack_algo=MaxRectsBssf)
    for cluster, raster, left, top, advance in rasters:
        packer.add_rect(raster.width + 4, raster.height + 4, rid=cluster)
    for region_id, (rx, ry, rw, rh) in enumerate(regions):
        packer.add_bin(rw, rh, bid=region_id)
    packer.pack()
    placements = {rid: (regions[packer[bn].bid][0] + px, regions[packer[bn].bid][1] + py)
                  for bn, px, py, pw, ph, rid in packer.rect_list()}
    expanded = False
    if len(placements) != len(rasters):
        if not allow_expand:
            raise ValueError(f"No spare atlas space in {path.name}: fitted {len(placements)}/{len(rasters)}")
        # Keep original glyph coordinates and size; add space below the atlas.
        # All original mip blocks are restored after compression below.
        old_height = texh
        # Large UI corpora can need more than one doubling. Keep the original
        # width and pixel coordinates, and pack only below the original image.
        while True:
            texh *= 2
            if texh > 4096:
                raise ValueError(f"Atlas would exceed 4096 pixels: {path.name}")
            packer = newPacker(rotation=False, pack_algo=MaxRectsBssf)
            for cluster, raster, left, top, advance in rasters:
                packer.add_rect(raster.width + 4, raster.height + 4, rid=cluster)
            # Retain safe spare areas on the original page as additional bins.
            # Requiring every new glyph to fit solely below the old image can
            # overflow at4096 even though the page still has unused native-safe space.
            expanded_regions = regions + [(4, old_height + 4, texw - 8, texh - old_height - 8)]
            for region_id, (rx, ry, rw, rh) in enumerate(expanded_regions):
                if rw > 0 and rh > 0:packer.add_bin(rw, rh, bid=region_id)
            packer.pack()
            placements = {rid: (expanded_regions[packer[bn].bid][0] + px, expanded_regions[packer[bn].bid][1] + py)
                          for bn, px, py, pw, ph, rid in packer.rect_list()}
            if len(placements) == len(rasters):
                break
        larger = Image.new("RGB", (texw, texh))
        larger.paste(atlas, (0, 0))
        atlas = larger
        expanded = True
    new_glyphs, rects = [], []
    for cluster, raster, left, top, advance in rasters:
        x, y = placements[cluster]
        edge = raster.filter(ImageFilter.MaxFilter(3 if outline <= 1 else 5))
        rgb = Image.merge("RGB", (raster, edge, Image.new("L", raster.size)))
        atlas.paste(rgb, (x, y))
        # Original Japanese font offsets are measured from the top of its line.
        new_glyphs.append((ord(cmap[cluster]), page, x, y, raster.width, raster.height, left, fontsize + top, advance))
        rects.append((x, y, raster.width, raster.height))
    digit_alignment = {}
    latin_alignment = {}
    if digit_keys or latin_keys:
        anchor, _, anchor_top, _ = raster_cluster("ก", size)
        anchor_box = anchor.point(lambda p: 255 if p >= 64 else 0).getbbox()
        baseline = fontsize + anchor_top + anchor_box[3]
        original_map = {g[0]: g for g in glyphs}
        source_pages = {page: atlas}
        def original_ink_box(original):
            if original[1] not in source_pages:
                source_texture = path.with_name(path.stem + f"-{original[1]:02d}.uasset").read_bytes()
                source_mips = mip_layout(source_texture, header_end(source_texture))
                source_packed = b"".join(source_texture[o:o+sz] for o,w,h,sz in source_mips)
                w,h = source_mips[0][1:3]
                source_pages[original[1]] = Image.open(io.BytesIO(dds_header(w,h,len(source_mips)) + source_packed)).convert("RGB")
            mask = source_pages[original[1]].getchannel("R").crop((original[2], original[3], original[2]+original[4], original[3]+original[5]))
            return mask.point(lambda p: 255 if p >= 64 else 0).getbbox()
        latin_shift = 0
        if latin_keys:
            capital_h = original_map[ord("H")]
            latin_shift = baseline - (capital_h[7] + original_ink_box(capital_h)[3])
        for character in sorted(digit_keys | latin_keys):
            original = original_map[ord(character)]
            ink_box = original_ink_box(original)
            shift = baseline - (original[7] + ink_box[3]) if character in digit_keys else latin_shift
            alias = list(original)
            alias[0] = ord(cmap[character])
            alias[7] += shift
            new_glyphs.append(tuple(alias))
            info = dict(vertical_shift=shift, ink_bottom=alias[7]+ink_box[3], source_page=original[1])
            (digit_alignment if character in digit_keys else latin_alignment)[character] = info
    imagepath = QA / (path.stem + ".png")
    atlas.save(imagepath)
    mip_count = int(math.log2(max(texw, texh))) + 1
    subprocess.run([str(WORK / "tools/texconv.exe"), "-y", "-f", "BC5_UNORM", "-m", str(mip_count), "-o", str(QA), str(imagepath)], check=True, stdout=subprocess.DEVNULL)
    dds = imagepath.with_suffix(".dds").read_bytes()
    dds_offset = 148 if dds[84:88] == b"DX10" else 128
    expected_size = sum(max(1, (max(1, texw >> level) + 3) // 4) * max(1, (max(1, texh >> level) + 3) // 4) * 16 for level in range(mip_count))
    if dds[:4] != b"DDS " or dds[84:88] not in (b"DX10", b"BC5U", b"ATI2") or len(dds) != expected_size + dds_offset:
        raise ValueError("Unexpected texconv BC5 output")
    if expanded:
        result = expand_texture(texture, dds[dds_offset:], texw, texh, mipmap)
        # expand_texture first restores the complete old mip payload. Reapply
        # only new-glyph blocks when the packing also used original spare space.
        # Otherwise those valid placements would be overwritten with empty pixels.
        if any(ry < old_height for rx, ry, rw, rh in rects):
            result = patch_texture_blocks(result, dds, dds_offset,
                                          mip_layout(result, header_end(result)), rects)
    else:
        result = patch_texture_blocks(texture, dds, dds_offset, mipmap, rects)
    body = bytearray(data[end:end + glyph_start])
    struct.pack_into("<I", body, glyph_start - 4, count + len(new_glyphs))
    for g in sorted(glyphs + new_glyphs):
        body.extend(struct.pack("<6H2hH", *g))
    body.extend(data[end + glyph_start + count * 18:])
    return with_body(data, body), bytes(result), dict(font=path.name, clusters=len(cmap), page=page, atlas_y=ystart, thai_pixel_size=size, atlas_size=[texw,texh], expanded=expanded, aligned_digits=digit_alignment, aligned_latin=latin_alignment)


def patch_texture_blocks(texture, dds, dds_offset, mipmap, rects):
    result = bytearray(texture)
    compressed_at = dds_offset
    for level, (offset, width, height, mip_size) in enumerate(mipmap):
        # Change only blocks intersecting new Thai glyphs. Japanese blocks stay identical.
        blocks = set()
        for rx, ry, rw, rh in rects:
            scale = 2 ** level
            x0, y0 = max(0, rx // scale - 2), max(0, ry // scale - 2)
            x1, y1 = min(width, math.ceil((rx + rw) / scale) + 2), min(height, math.ceil((ry + rh) / scale) + 2)
            for by in range(y0 // 4, (y1 + 3) // 4):
                for bx in range(x0 // 4, (x1 + 3) // 4):
                    blocks.add(by * max(1, (width + 3) // 4) + bx)
        for block in blocks:
            start = block * 16
            result[offset + start:offset + start + 16] = dds[compressed_at + start:compressed_at + start + 16]
        compressed_at += mip_size
    return result


def expand_texture(texture, compressed, width, height, old_mips):
    """Rebuild inline UE4 texture platform data, preserving original mip bytes.

    Layout follows vendored FTexturePlatformData/FTexture2DMipMap/FByteBulkData.
    The original inline flags are 0x48 (no external payload). Width is unchanged.
    """
    end = header_end(texture)
    body = bytearray(texture[end:end + 94])
    assert struct.unpack_from("<I", body, 90)[0] == len(old_mips)
    assert struct.unpack_from("<I", body, 63)[0] == width
    count = int(math.log2(max(width, height))) + 1
    struct.pack_into("<I", body, 12, height)
    struct.pack_into("<I", body, 67, height)
    struct.pack_into("<I", body, 90, count)
    bias = struct.unpack_from("<Q", texture, old_mips[0][0] - 8)[0] - old_mips[0][0]
    at = 0
    for level in range(count):
        mw, mh = max(1, width >> level), max(1, height >> level)
        size = max(1,(mw+3)//4) * max(1,(mh+3)//4) * 16
        raw = bytearray(compressed[at:at+size])
        assert len(raw) == size
        if level < len(old_mips):
            old_at, old_w, old_h, old_size = old_mips[level]
            assert old_w == mw and old_h <= mh and old_size <= size
            raw[:old_size] = texture[old_at:old_at + old_size]
        payload_offset = end + len(body) + 24 + bias
        body.extend(struct.pack("<4IQ",1,0x48,size,size,payload_offset))
        body.extend(raw)
        body.extend(struct.pack("<3I",max(4,mw),max(4,mh),1))
        at += size
    assert at == len(compressed)
    last_at, last_w, last_h, last_size = old_mips[-1]
    body.extend(texture[last_at + last_size + 12:])
    delta = len(body) - (len(texture) - end)
    struct.pack_into("<Q",body,55,struct.unpack_from("<Q",body,55)[0] + delta)
    output = with_body(texture,body)
    new_mips = mip_layout(output,header_end(output))
    assert len(new_mips) == count
    for (a,w,h,s), (na,nw,nh,ns) in zip(old_mips,new_mips):
        assert output[na:na+s] == texture[a:a+s], "Original mip bytes changed"
    return output


def main():
    QA.mkdir(parents=True, exist_ok=True)
    translation = json.loads((WORK / "translations/prototype-th.json").read_text(encoding="utf-8"))
    clusters = sorted({c for text in translation["entries"].values() for c in split_clusters(text) if "\u0e01" <= c[0] <= "\u0e5b"})
    cmap = {cluster: chr(0xE800 + i) for i, cluster in enumerate(clusters)}
    (WORK / "reference/prototype-cluster-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=2), encoding="utf-8")
    target = STAGE / translation["asset"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(patch_text(WORK / "source" / translation["asset"], translation["entries"], cmap))
    # Verify the actual serialized result, including caption IDs and UTF-16 text.
    parsed = txtres.parse(str(target))
    reverse = str.maketrans({v: k for k, v in cmap.items()})
    if {k: v["Text"].translate(reverse) for k, v in parsed.items()} != translation["entries"]:
        raise ValueError("Subtitle round-trip mismatch")
    fonts = []
    common = Path("End/Content/Menu/Billboard/Common")
    for source in sorted((WORK / "source" / common).glob("U_Com_JP_SystemFont*.uasset")):
        if "-" in source.name:
            continue
        fontdata, texdata, stats = patch_font(source, cmap)
        dest = STAGE / common / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(fontdata)
        dest.with_name(source.stem + f'-{stats["page"]:02d}.uasset').write_bytes(texdata)
        fonts.append(stats)
    report = dict(captions=len(parsed), clusters=len(clusters), fonts=fonts, runtime_tested=False)
    (QA / "build-verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
