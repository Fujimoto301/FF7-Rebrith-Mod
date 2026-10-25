"""
triggerpatch.py — same-length, in-place edits to trigger/volume gating
properties in FF7 Rebirth cooked .umap files.

Aimed at progression gating: making a later trigger read as already activated so
a sequence is skipped. On the level side that means the properties
AEndStreamingVolume exposes —

    ActivateProgress / ShowProgress / DeactivateProgress   uint32 (chapter progress)
    ActivateStoryFlag / ShowStoryFlag / DeactivateStoryFlag  FName (e.g.
                                        stfStory1000_EASTC_Ch02_Step088_990)
    bDisabled, bForce                                      bool

— plus equivalents on other classes (EndShootingCoaster*TriggerBox's
ActivateOnStateTrigger, EndFieldActionDamageReciveVolume's
CollisionControlByStoryFlag, and so on).

THE ONE RULE: every write is the same length as the value it replaces, so no
offset, bundle or graph fixup is ever needed and the file size never changes.
That is what makes this safe. Two consequences you cannot argue with:

  * A property that is not serialised in that actor cannot be set. Unversioned
    serialisation omits anything equal to the class default, so there are no
    bytes to overwrite. The tool refuses rather than guessing.
  * A property whose current value is zero is *zero-masked* and also occupies no
    bytes, so it cannot be changed either. (Writing a zero INTO an existing
    non-zero value is fine — the mask bit only says whether bytes are present.)

FName targets have a second constraint: an FName is an 8-byte (index, number)
reference into the package's own name map, so you can only repoint it to a name
already in that .umap. --inspect lists the candidates.

Read the original, write a copy: input files are never modified in place.

Usage:
    # see what is patchable on an actor, and what names it could point at
    python triggerpatch.py --assets <Field> --usmap Mappings.usmap --uht <dir> \
        --inspect --level 1000-EASTC/... --actor SV_Foo [--grep stfStory]

    # apply an edit list
    python triggerpatch.py --assets <Field> --usmap Mappings.usmap --uht <dir> \
        --edits edits.json --outdir patched/

edits.json:
    {"edits": [
      {"level": "1000-EASTC/Prog/1000-EASTC_LP",
       "actor": "2100-StreamingVolume_Gimmick",
       "set": {"ActivateProgress": 0, "ActivateStoryFlag": "None"}}
    ]}
"""
import argparse
import json
import os
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zenasset import Usmap, Reader
from levelvolumes import (ClassResolver, TolerantAsset, bundle_offsets,
                          ENUM_UNDERLYING, EXTRA_NATIVE_STRUCTS)

# Fixed-width property types we are willing to overwrite in place.
FIXED_WIDTH = {
    'BoolProperty': 1, 'ByteProperty': 1, 'Int8Property': 1,
    'Int16Property': 2, 'UInt16Property': 2,
    'IntProperty': 4, 'UInt32Property': 4, 'FloatProperty': 4,
    'Int64Property': 8, 'UInt64Property': 8, 'DoubleProperty': 8,
    'NameProperty': 8,
}


class PatchError(Exception):
    pass


class PatchableAsset(TolerantAsset):
    """Adds byte-level location of each serialised property value."""

    def locate(self, start, struct_name):
        """Walk an export's unversioned block recording where each value lives.

        Returns a list of dicts: name, type, offset (absolute), size, value,
        zeroed. Zero-masked entries have size 0 — present in the schema, absent
        from the byte stream.
        """
        schema = self.usmap.schema_chain(struct_name)
        if not schema:
            raise PatchError('no schema for %s' % struct_name)
        r = Reader(self.d, start)

        frags = []
        while True:
            packed = r.read('<H')
            frags.append({'skip': packed & 0x7F, 'hasZeros': bool(packed & 0x80),
                          'values': packed >> 9, 'last': bool(packed & 0x100)})
            if frags[-1]['last']:
                break
        num_zero_bits = sum(f['values'] for f in frags if f['hasZeros'])
        zero_mask = []
        if num_zero_bits > 0:
            if num_zero_bits <= 8:
                raw = r.read('<B')
            elif num_zero_bits <= 16:
                raw = r.read('<H')
            else:
                raw = 0
                for w in range((num_zero_bits + 31) // 32):
                    raw |= r.read('<I') << (32 * w)
            zero_mask = [(raw >> i) & 1 for i in range(num_zero_bits)]

        by_index = {}
        for gi, p in schema:
            by_index.setdefault(gi, p)

        found, idx, zi = [], 0, 0
        for f in frags:
            idx += f['skip']
            for _ in range(f['values']):
                is_zero = False
                if f['hasZeros']:
                    is_zero = bool(zero_mask[zi])
                    zi += 1
                p = by_index.get(idx)
                if p is None:
                    return found
                before = r.o
                try:
                    value = self.read_value(r, p, is_zero, 0)
                except Exception:
                    return found
                found.append({'name': p['name'], 'type': p['type'],
                              'prop': p, 'offset': before, 'size': r.o - before,
                              'value': value, 'zeroed': is_zero})
                idx += 1
        return found

    def name_index(self, text):
        """Index of an existing name-map entry, or None."""
        try:
            return self.names.index(text)
        except ValueError:
            return None


def encode_value(asset, entry, new_value):
    """Bytes for new_value, or raise PatchError. Must match entry['size']."""
    ptype, size = entry['type'], entry['size']
    if entry['zeroed'] or size == 0:
        raise PatchError(
            "'%s' is currently zero/default, so it occupies no bytes in the "
            "file and cannot be changed by a same-length patch. Changing it "
            "needs a fragment-header rewrite and export resize." % entry['name'])
    want = FIXED_WIDTH.get(ptype)
    if ptype == 'EnumProperty':
        want = ENUM_UNDERLYING.get(
            (entry['prop'].get('inner') or {}).get('type', 'ByteProperty'), ('<B', 1))[1]
    if want is None:
        raise PatchError("'%s' is a %s; only fixed-width properties can be "
                         "patched in place." % (entry['name'], ptype))
    if want != size:
        raise PatchError("'%s': expected %d bytes, found %d in the file"
                         % (entry['name'], want, size))

    if ptype == 'BoolProperty':
        if not isinstance(new_value, bool):
            raise PatchError("'%s' needs true/false" % entry['name'])
        return b'\x01' if new_value else b'\x00'

    if ptype == 'NameProperty':
        if not isinstance(new_value, str):
            raise PatchError("'%s' needs a name string" % entry['name'])
        base, number = new_value, 0
        idx = asset.name_index(base)
        if idx is None and '_' in base:
            # FName round-trips as Name_N with number = N+1
            head, _, tail = base.rpartition('_')
            if tail.isdigit() and asset.name_index(head) is not None:
                base, number, idx = head, int(tail) + 1, asset.name_index(head)
        if idx is None:
            raise PatchError(
                "'%s' is not in this package's name map, so it cannot be "
                "referenced. Run --inspect to list the %d available names."
                % (new_value, len(asset.names)))
        return struct.pack('<II', idx, number)

    if ptype == 'EnumProperty':
        names = asset.usmap.enums.get(entry['prop'].get('enum') or '', [])
        if isinstance(new_value, str):
            if new_value not in names:
                raise PatchError("'%s' is not a value of enum %s"
                                 % (new_value, entry['prop'].get('enum')))
            new_value = names.index(new_value)
        fmt = ENUM_UNDERLYING[(entry['prop'].get('inner') or {}).get(
            'type', 'ByteProperty')][0]
        return struct.pack(fmt, int(new_value))

    fmt = {'ByteProperty': '<B', 'Int8Property': '<b', 'Int16Property': '<h',
           'UInt16Property': '<H', 'IntProperty': '<i', 'UInt32Property': '<I',
           'FloatProperty': '<f', 'Int64Property': '<q', 'UInt64Property': '<Q',
           'DoubleProperty': '<d'}[ptype]
    if ptype in ('FloatProperty', 'DoubleProperty'):
        return struct.pack(fmt, float(new_value))
    return struct.pack(fmt, int(new_value))


# --------------------------------------------------------------------------

class Session:
    def __init__(self, assets, usmap_path, uht=None, cache='.classhash-cache.json'):
        self.assets = assets
        self.usmap = Usmap(usmap_path)
        self.resolver = ClassResolver(self.usmap, uht, cache)
        from zenasset import NATIVE_STRUCTS
        NATIVE_STRUCTS.update(EXTRA_NATIVE_STRUCTS)

    def open(self, level):
        path = os.path.join(self.assets, level.replace('/', os.sep) + '.umap')
        if not os.path.exists(path):
            raise PatchError('no such level: %s' % path)
        return path, PatchableAsset(path, self.usmap)

    def find_actor(self, asset, actor, export=None):
        """Locate one actor. Actor names are NOT unique.

        UE distinguishes same-named actors by the FName *number*, which the
        export map stores separately, so a level can hold seven exports all
        reading as EndStreamingVolume_EV_FOREE — and only some of them carry the
        gating property you want. Refuse to guess: if the name is ambiguous and
        no export index was given, list the candidates and stop.
        """
        offsets = bundle_offsets(asset)
        matches = [e for e in asset.exports if e['name'] == actor]
        if not matches:
            raise PatchError('actor %s not found' % actor)
        if export is not None:
            matches = [e for e in matches if e['index'] == export]
            if not matches:
                raise PatchError('no export %s named %s' % (export, actor))
        if len(matches) > 1:
            hints = []
            for e in matches:
                cls = self.resolver.get(e['class'])
                label = ''
                if cls and cls in self.usmap.structs and e['index'] in offsets:
                    try:
                        got = {x['name']: x['value']
                               for x in asset.locate(offsets[e['index']], cls)}
                        label = got.get('VolumeLabel') or got.get('LocationId') or ''
                    except Exception:
                        pass
                hints.append('export %d%s' % (e['index'],
                                              ' (%s)' % label if label else ''))
            raise PatchError(
                '%d exports are named %s — add "export": <n> to the edit to pick '
                'one. Candidates: %s' % (len(matches), actor, '; '.join(hints)))
        e = matches[0]
        cls = self.resolver.get(e['class'])
        if not cls or cls not in self.usmap.structs:
            raise PatchError('actor %s has an unresolved class' % actor)
        if e['index'] not in offsets:
            raise PatchError('actor %s has no serialised payload' % actor)
        return e, cls, offsets[e['index']]


def cmd_inspect(sess, level, actor, grep, export_idx=None):
    _path, asset = sess.open(level)
    export, cls, start = sess.find_actor(asset, actor, export_idx)
    entries = asset.locate(start, cls)
    print('%s  (%s, export %d)' % (actor, cls, export['index']))
    print('%-34s %-16s %8s %6s  %s' % ('PROPERTY', 'TYPE', 'OFFSET', 'BYTES', 'VALUE'))
    for e in entries:
        patchable = (not e['zeroed'] and e['size'] > 0
                     and (e['type'] in FIXED_WIDTH or e['type'] == 'EnumProperty'))
        mark = ' ' if patchable else 'x'
        val = e['value']
        if isinstance(val, (dict, list)):
            val = json.dumps(val)[:44]
        print('%s %-32s %-16s %8d %6d  %s'
              % (mark, e['name'], e['type'], e['offset'], e['size'], val))
    print('\nx = not patchable in place (zero/default, or variable width)')
    if grep:
        hits = [n for n in asset.names if grep.lower() in n.lower()]
        print('\nname-map entries matching %r (%d of %d):'
              % (grep, len(hits), len(asset.names)))
        for n in sorted(hits)[:60]:
            print('   ', n)
    return 0


def apply_edits(sess, edits, outdir, verify=True):
    by_level = {}
    for ed in edits:
        by_level.setdefault(ed['level'], []).append(ed)

    results = []
    for level, group in sorted(by_level.items()):
        src, asset = sess.open(level)
        data = bytearray(asset.d)
        original = bytes(asset.d)
        changes = []

        for ed in group:
            export, cls, start = sess.find_actor(asset, ed['actor'], ed.get('export'))
            entries = {e['name']: e for e in asset.locate(start, cls)}
            for prop, new_value in ed.get('set', {}).items():
                if prop not in entries:
                    raise PatchError(
                        "%s / %s: '%s' is not serialised in this actor (it is "
                        "at its class default), so there are no bytes to patch."
                        % (level, ed['actor'], prop))
                entry = entries[prop]
                blob = encode_value(asset, entry, new_value)
                if len(blob) != entry['size']:
                    raise PatchError('internal: size mismatch on %s' % prop)
                old = bytes(data[entry['offset']:entry['offset'] + entry['size']])
                data[entry['offset']:entry['offset'] + entry['size']] = blob
                changes.append({'actor': ed['actor'], 'export': export['index'],
                                'property': prop,
                                'offset': entry['offset'], 'bytes': entry['size'],
                                'from': entry['value'], 'to': new_value,
                                'changed_bytes': old != blob})

        dst = os.path.join(outdir, level.replace('/', os.sep) + '.umap')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as fh:
            fh.write(bytes(data))

        record = {'level': level, 'source': src, 'output': dst,
                  'changes': changes,
                  'size_in': len(original), 'size_out': len(data),
                  'byte_identical': bytes(data) == original}
        if verify:
            record['verify'] = verify_patch(sess, src, dst, group, changes)
        results.append(record)
    return results


def verify_patch(sess, src, dst, group, changes):
    """Re-parse the patched file and prove exactly the intended bytes moved."""
    out = {'size_unchanged': os.path.getsize(src) == os.path.getsize(dst)}

    before = PatchableAsset(src, sess.usmap)
    after = PatchableAsset(dst, sess.usmap)

    # 1. every requested value reads back
    reads_back, mismatches = True, []
    for ed in group:
        _e, cls, start = sess.find_actor(after, ed['actor'], ed.get('export'))
        got = {x['name']: x['value'] for x in after.locate(start, cls)}
        for prop, want in ed.get('set', {}).items():
            if got.get(prop) != want:
                reads_back = False
                mismatches.append({'actor': ed['actor'], 'property': prop,
                                   'wanted': want, 'got': got.get(prop)})
    out['values_read_back'] = reads_back
    if mismatches:
        out['mismatches'] = mismatches

    # 2. nothing else in the package moved: differing bytes must be exactly the
    #    ranges we wrote
    a, b = open(src, 'rb').read(), open(dst, 'rb').read()
    diff = {i for i in range(min(len(a), len(b))) if a[i] != b[i]}
    intended = set()
    for c in changes:
        intended.update(range(c['offset'], c['offset'] + c['bytes']))
    out['bytes_differing'] = len(diff)
    out['all_diffs_inside_patched_ranges'] = diff <= intended

    # 3. every other export still decodes identically
    off_a, off_b = bundle_offsets(before), bundle_offsets(after)
    touched = {(c['actor'], c.get('export')) for c in changes}
    drift = 0
    for e in before.exports:
        cls = sess.resolver.get(e['class'])
        if not cls or cls not in sess.usmap.structs or e['index'] not in off_a:
            continue
        if (e['name'], e['index']) in touched:
            continue
        try:
            pa = before.read_unversioned(Reader(before.d, off_a[e['index']]), cls)
            pb = after.read_unversioned(Reader(after.d, off_b[e['index']]), cls)
        except Exception:
            continue
        if pa != pb:
            drift += 1
    out['other_exports_unchanged'] = (drift == 0)
    out['other_exports_drifted'] = drift
    out['ok'] = (out['size_unchanged'] and reads_back
                 and out['all_diffs_inside_patched_ranges']
                 and out['other_exports_unchanged'])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--assets', required=True)
    ap.add_argument('--usmap', required=True)
    ap.add_argument('--uht')
    ap.add_argument('--cache', default='.classhash-cache.json')
    ap.add_argument('--inspect', action='store_true')
    ap.add_argument('--level')
    ap.add_argument('--actor')
    ap.add_argument('--grep', help='with --inspect, filter the name map')
    ap.add_argument('--export', type=int, help='disambiguate same-named actors')
    ap.add_argument('--edits')
    ap.add_argument('--outdir', default='patched')
    ap.add_argument('--report', help='write the change/verify report as JSON')
    args = ap.parse_args(argv)

    sess = Session(args.assets, args.usmap, args.uht, args.cache)

    if args.inspect:
        if not (args.level and args.actor):
            ap.error('--inspect needs --level and --actor')
        return cmd_inspect(sess, args.level, args.actor, args.grep, args.export)

    if not args.edits:
        ap.error('give --edits or --inspect')
    with open(args.edits) as fh:
        doc = json.load(fh)
    edits = doc['edits'] if isinstance(doc, dict) else doc

    results = apply_edits(sess, edits, args.outdir)
    ok = True
    for r in results:
        v = r.get('verify', {})
        ok = ok and v.get('ok', False)
        print('%s -> %s' % (r['level'], r['output']))
        print('   size %d -> %d (%s)'
              % (r['size_in'], r['size_out'],
                 'unchanged' if r['size_in'] == r['size_out'] else 'CHANGED'))
        for c in r['changes']:
            print('   %-28s #%-4s %-24s %s -> %s  @%d (%d bytes)%s'
                  % (c['actor'], c.get('export'), c['property'], c['from'], c['to'],
                     c['offset'], c['bytes'],
                     '' if c['changed_bytes'] else '  [no-op]'))
        print('   verify: %s' % json.dumps(v))
    if args.report:
        with open(args.report, 'w') as fh:
            json.dump(results, fh, indent=1)
    print('\n%s' % ('ALL EDITS VERIFIED' if ok else 'VERIFICATION FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
