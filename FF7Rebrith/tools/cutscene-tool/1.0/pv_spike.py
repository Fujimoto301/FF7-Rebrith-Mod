"""
pv_spike.py — patch a generated-dialogue (PV_*) scene and stage it for UnrealReZen.

A deliberately small spike, separate from the EV_ pipeline: it does not import
patcher.py and nothing here is reachable from the existing tool. It exists to
answer one question — does removing a line collapse its time, or hold it? — and
to prove the two edit surfaces work at all.

What it can do
  --null-line   <GenerateId>       clear a line's voice + subtitle
  --repoint     <old>=<new>        point a BGM cue at another track
Both are FName index rewrites: an FName is 8 bytes (name index + number) into
the package name table, so nothing resizes and every offset in the Zen package
survives. The replacement name must already exist in that package's name table.

Usage
  python3 pv_spike.py --content <...>/End/Content --usmap <...>/Mappings.usmap \
      --scene Dialogue/Game/1300-JUNOA/PV_QST13_0030 \
      --null-line PV_QST13_0030_0020 --repoint bgm_kaiho_003=bgm_silence \
      --out D:/mods/PVSpike --name PVSpike \
      --game-dir "<game>/End/Content/Paks" --rezen "<tool>/UnrealReZen.exe"
"""
import os, sys, json, glob, shutil, struct, argparse, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zenasset import Usmap
import transforms as T


# ---------------- reading with offsets ----------------

def instrument(a):
    """Record (offset, value) for every FName the parser reads."""
    log = []
    orig = a.read_fname
    def f(r):
        o = r.o
        v = orig(r)
        log.append((o, v))
        return v
    a.read_fname = f
    return log


def parse_all(path, usmap):
    """Every export parsed, plus the FName offset log, keyed by export index."""
    a = T.Reader2(path, usmap)
    exports, logs = {}, {}
    for i, cn in enumerate(a.classNames):
        if cn is None or i not in a.dataOffset:
            continue
        log = instrument(a)
        try:
            exports[i] = a.read_export(i)
        except Exception as e:
            exports[i] = {'__error__': repr(e)[:120]}
        logs[i] = list(log)
        del a.read_fname          # drop the instrumented override
    return a, exports, logs


def name_index(a, name):
    try:
        return a.names.index(name)
    except ValueError:
        raise SystemExit(
            'name %r is not in this package\'s name table; it can only be '
            'repointed at a name already there' % name)


def fname_offsets(log, value):
    return [o for o, v in log if v == value]


# ---------------- the edit ----------------

class Edit:
    """One FName field rewrite, located by the value that is there now."""
    def __init__(self, path, export, field, old, new, where):
        self.path, self.export, self.field = path, export, field
        self.old, self.new, self.where = old, new, where
    def __repr__(self):
        return '%s  export %d  %-12s %s -> %s' % (
            os.path.basename(self.path), self.export, self.field, self.old, self.new)


def patch_file(path, usmap, edits, dry=False):
    """Apply edits to one package. Section fields by offset, template copies by scan."""
    a, before, logs = parse_all(path, usmap)
    d = bytearray(a.d)
    n0 = len(d)
    touched = []
    changed_names = {}

    for e in edits:
        idx_new = name_index(a, e.new)
        offs = fname_offsets(logs[e.export], e.old)
        if len(offs) != 1:
            raise SystemExit('%s: expected exactly one %r in export %d, found %d'
                             % (os.path.basename(path), e.old, e.export, len(offs)))
        o = offs[0]
        old_idx, num = struct.unpack_from('<II', d, o)
        struct.pack_into('<II', d, o, idx_new, num)
        touched.append((o, e.field, e.old, e.new))
        changed_names[(old_idx, num)] = idx_new

    # Some section templates carry a second copy of the value; some only carry a
    # GUID back to the section. Measured, not assumed: an EndDialogueBgmSection's
    # MusicName sits 4 bytes past its "<Class>Template" marker inside
    # MovieSceneCompiledData (confirmed on three scenes, including one where the
    # FName number is non-zero), while EndDialogueVoiceSection labels appear
    # there not at all. So anchor on the marker and only rewrite a slot whose
    # current value is exactly the one being replaced. A blind byte scan is not
    # safe here: a low name index makes "<idx> 00 00 00 00 00 00 00" a pattern
    # that occurs dozens of times in a compiled blob by chance.
    cd = [i for i, c in enumerate(a.classNames) if c == 'MovieSceneCompiledData']
    tmpl = 0
    for e in edits:
        cls = a.classNames[e.export]
        if not cls or not cls.endswith('Section'):
            continue
        marker = (cls + 'Template').encode()
        idx_new = name_index(a, e.new)
        for i in cd:
            lo = a.dataOffset[i]
            hi = lo + a.exports[i]['serialSize']
            s = lo
            while True:
                m = d.find(marker, s, hi)
                if m < 0:
                    break
                slot = m + len(marker) + 4
                s = m + len(marker)
                if slot + 8 > hi:
                    continue
                old_idx, num = struct.unpack_from('<II', d, slot)
                if old_idx >= len(a.names):
                    continue
                cur = a.names[old_idx] if num == 0 else '%s_%d' % (a.names[old_idx], num - 1)
                if cur != e.old:
                    continue
                struct.pack_into('<II', d, slot, idx_new, num)
                touched.append((slot, cls + 'Template', e.old, e.new))
                tmpl += 1

    assert len(d) == n0, 'package length changed — refusing to write'

    # Verify against the bytes, not the parse: transforms.py installs native
    # readers that return objects without __eq__, so comparing parsed exports
    # reports every float channel as different on two reads of the same file.
    def owner(off):
        for i in a.dataOffset:
            lo = a.dataOffset[i]
            if lo <= off < lo + a.exports[i]['serialSize']:
                return i
        return None

    expected = {owner(o) for o, *_ in touched}
    changed = []
    for i in sorted(a.dataOffset):
        lo = a.dataOffset[i]
        hi = lo + a.exports[i]['serialSize']
        if a.d[lo:hi] != bytes(d[lo:hi]):
            changed.append(i)
    stray = [i for i in changed if i not in expected]
    if stray:
        raise SystemExit('%s: unexpected byte changes in exports %s' %
                         (os.path.basename(path), stray))
    if not dry:
        open(path, 'wb').write(bytes(d))

    # re-read the patched file and report what the edited fields now say
    now = []
    if not dry:
        a2 = T.Reader2(path, usmap)
        for i in sorted(expected):
            if a2.classNames[i] == 'MovieSceneCompiledData':
                continue
            try:
                v = a2.read_export(i)
            except Exception as e:
                now.append((i, a2.classNames[i], 'unreadable: %r' % e))
                continue
            if a2.classNames[i] == 'EndDialogueSequence':
                rows = dict(v['Rows'])
                for e in edits:
                    if e.export == i and e.where in rows:
                        now.append((i, 'Rows[%s]' % e.where,
                                    {k: rows[e.where][k] for k in ('SoundID', 'TextId', 'OutputType')}))
            else:
                now.append((i, a2.classNames[i],
                            {k: v.get(k) for k in ('GenerateId', 'VoiceLabel', 'TextLabel', 'MusicName')
                             if k in v or k in ('MusicName',) and 'MusicName' in v}))

    return {'edits': len(edits), 'templateCopies': tmpl,
            'bytesTouched': touched, 'exportsChanged': changed,
            'afterValues': now, 'sizeStable': len(d) == n0}


# ---------------- locating what to edit ----------------

def plan_scene(scene_dir, usmap, null_lines, repoints):
    root = glob.glob(os.path.join(scene_dir, '*_Root.uasset'))
    if not root:
        raise SystemExit('no *_Root.uasset in %s' % scene_dir)
    root = root[0]
    per_file = {}

    a, exports, _ = parse_all(root, usmap)
    seq = [i for i, c in enumerate(a.classNames) if c == 'EndDialogueSequence']
    if not seq:
        raise SystemExit('%s has no EndDialogueSequence export' % os.path.basename(root))
    si = seq[0]
    rows = {k: v for k, v in exports[si]['Rows']}

    for gid in null_lines:
        if gid not in rows:
            raise SystemExit('%s is not a row in this scene. Rows: %s'
                             % (gid, ', '.join(sorted(rows))))
        r = rows[gid]
        for field in ('SoundID', 'TextId'):
            if r.get(field) in (None, 'None'):
                continue
            per_file.setdefault(root, []).append(
                Edit(root, si, 'Rows.' + field, r[field], 'None', gid))

    for old, new in repoints:
        for i, c in enumerate(a.classNames):
            if c == 'EndDialogueBgmSection' and exports[i].get('MusicName') == old:
                per_file.setdefault(root, []).append(
                    Edit(root, i, 'MusicName', old, new, 'bgm'))

    # the performance side lives in the shots, addressed by GenerateId
    for shot in sorted(glob.glob(os.path.join(scene_dir, 'Shot', '*.uasset'))):
        sa, sex, _ = parse_all(shot, usmap)
        for i, c in enumerate(sa.classNames):
            if c != 'EndDialogueVoiceSection':
                continue
            gid = sex[i].get('GenerateId')
            if gid not in null_lines:
                continue
            for field in ('VoiceLabel', 'TextLabel'):
                v = sex[i].get(field)
                if v in (None, 'None'):
                    continue
                per_file.setdefault(shot, []).append(
                    Edit(shot, i, field, v, 'None', gid))
    return root, rows, per_file


BAT = """@echo off
REM Built by pv_spike.py — generated-dialogue test mod.
set REZEN={rezen}
set GAMEDIR={gamedir}
set CONTENT=%~dp0staged
set OUT=%~dp0{name}_P.utoc

REM UnrealReZen indexes every .utoc under --game-dir, so an existing ~mods
REM folder would be folded into this pak. Move it aside and always put it back.
set "STASH=%GAMEDIR%\\~mods_stashed_by_pv_spike"
if exist "%GAMEDIR%\\~mods" move "%GAMEDIR%\\~mods" "%STASH%" >nul

"%REZEN%" --content-path "%CONTENT%" --compression-format {compression} ^
  --engine-version {engine} --game-dir "%GAMEDIR%" --output-path "%OUT%"
set RC=%ERRORLEVEL%

if exist "%STASH%" move "%STASH%" "%GAMEDIR%\\~mods" >nul
if not "%RC%"=="0" (echo. & echo UnrealReZen failed with %RC% & pause & exit /b %RC%)

echo.
echo Built %OUT%
echo Copy the _P.utoc / _P.ucas / _P.pak into your Paks\\~mods folder.
pause
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True)
    ap.add_argument('--usmap', required=True)
    ap.add_argument('--scene', required=True,
                    help='content-relative, e.g. Dialogue/Game/1300-JUNOA/PV_QST13_0030')
    ap.add_argument('--null-line', action='append', default=[])
    ap.add_argument('--repoint', action='append', default=[],
                    help='old=new, e.g. bgm_kaiho_003=bgm_silence')
    ap.add_argument('--out', required=True)
    ap.add_argument('--name', default='PVSpike')
    ap.add_argument('--game-dir', default='C:/Program Files (x86)/Steam/steamapps/common/FINAL FANTASY VII REBIRTH/End/Content/Paks')
    ap.add_argument('--rezen', default='UnrealReZen.exe')
    ap.add_argument('--engine-version', default='GAME_UE4_26')
    ap.add_argument('--compression', default='Zlib')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    usmap = Usmap(a.usmap)
    src = os.path.join(a.content, a.scene.replace('/', os.sep))
    if not os.path.isdir(src):
        raise SystemExit('no such scene folder: %s' % src)

    repoints = []
    for r in a.repoint:
        if '=' not in r:
            raise SystemExit('--repoint wants old=new, got %r' % r)
        old, new = r.split('=', 1)
        repoints.append((old.strip(), new.strip()))

    staged = os.path.join(a.out, 'staged', 'End', 'Content', a.scene.replace('/', os.sep))
    if not a.dry_run:
        # Overwrite rather than clear the folder first: this runs against a
        # mount where deletes are refused, and a stale patched file left in
        # place would be re-patched and the second edit would land on top of
        # the first. Copying every source file over guarantees a clean start.
        for dp, _, fns in os.walk(src):
            rel = os.path.relpath(dp, src)
            dst = os.path.join(staged, rel) if rel != '.' else staged
            os.makedirs(dst, exist_ok=True)
            for fn in fns:
                shutil.copy2(os.path.join(dp, fn), os.path.join(dst, fn))
    work = src if a.dry_run else staged

    root, rows, per_file = plan_scene(work, usmap, set(a.null_line), repoints)

    print('scene   %s' % a.scene)
    print('rows    %d (%d voiced)' % (
        len(rows), sum(1 for r in rows.values() if r.get('OutputType') == 1)))
    if not per_file:
        raise SystemExit('nothing to do — no matching line or music cue')
    print('\nplanned edits')
    for p, es in per_file.items():
        for e in es:
            print('  ', e)

    report = {'scene': a.scene, 'nullLines': a.null_line,
              'repoints': ['%s=%s' % r for r in repoints], 'files': {}}
    print('\napplying')
    for p, es in per_file.items():
        res = patch_file(p, usmap, es, dry=a.dry_run)
        rel = os.path.relpath(p, work)
        report['files'][rel] = res
        print('  %-34s %d field(s) + %d template copies, size stable: %s'
              % (rel, res['edits'], res['templateCopies'], res['sizeStable']))
        for i, what, v in res['afterValues']:
            print('      export %-3d %-24s %s' % (i, what, v))

    if a.dry_run:
        print('\ndry run — nothing written')
        return

    # %~dp0 keeps the output next to the .bat, so no host path has to be
    # translated into this script's view of the filesystem.
    bat = BAT.format(rezen=a.rezen, gamedir=a.game_dir, name=a.name,
                     compression=a.compression, engine=a.engine_version)
    open(os.path.join(a.out, 'build_pv_spike.bat'), 'w').write(bat)
    json.dump(report, open(os.path.join(a.out, 'pv_spike_report.json'), 'w'), indent=1)
    print('\nstaged   %s' % os.path.join(a.out, 'staged'))
    print('pack     %s' % os.path.join(a.out, 'build_pv_spike.bat'))


if __name__ == '__main__':
    main()
