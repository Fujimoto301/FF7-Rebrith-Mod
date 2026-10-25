"""
build_mod.py — turn edit plans into a ready-to-pack UnrealReZen mod.

Steps
  1. patch each cutscene's .uasset files in place (patcher.py)
  2. stage them in archive-relative layout:  End/Content/Cut/Game/<AREA>/<EV>/
  3. verify by re-extracting the *patched* assets and checking the timing moved
     exactly as the plan intended
  4. emit build_mod.bat with the UnrealReZen command (and run it if asked)

Usage
  python3 build_mod.py --plan A.json [--plan B.json] \
      --content <...>/End/Content --usmap <...>/Mappings.usmap \
      --out <mod folder> --name MyCutsceneMod \
      --game-dir "C:/.../End/Content/Paks" [--rezen "C:/tools/UnrealReZen.exe"]
      [--engine-version GAME_UE4_26] [--compression Zlib] [--run]
"""
import os, sys, json, shutil, argparse, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zenasset import Usmap
import patcher
import audio_ripple
import evalfield


def utoc_cutscenes(path):
    """Which EV_* cutscenes a built .utoc actually contains."""
    import re as _re
    try:
        d = open(path, 'rb').read()
    except OSError:
        return None
    return sorted({m.group().decode() for m in _re.finditer(rb'EV_[A-Z]+_\d+', d)})


def audit_mods(mods_dir, expected=None):
    """Report any pak that carries cutscenes other than its own."""
    import re as _re
    bad = []
    if not os.path.isdir(mods_dir):
        return bad
    for f in sorted(os.listdir(mods_dir)):
        if not f.lower().endswith('.utoc'):
            continue
        m = _re.search(r'EV_[A-Z]+_\d+', f)          # tolerate _P and any -hash suffix
        own = m.group() if m else (f[:-len('_P.utoc')] if f.endswith('_P.utoc') else f[:-5])
        inside = utoc_cutscenes(os.path.join(mods_dir, f))
        if inside is None:
            continue
        extra = [e for e in inside if e != own]
        if extra:
            bad.append((f, extra))
    return bad


def plan_problem(plan):
    """Reasons a plan cannot produce a loadable cutscene, in plain words."""
    pr = plan.get('playbackRange') or [0, 0]
    total = pr[1] - pr[0]
    rem = sum(b - a for a, b in (plan.get('removeRanges') or []))
    left = total - rem
    if total <= 0:
        return 'the cutscene has no length to edit'
    if left <= 0:
        return ('the cuts remove the whole cutscene (%.1fs of %.1fs) — a sequence '
                'with no length crashes the game when it tries to play. Keep at '
                'least a moment of it, or delete the mod instead.'
                % (rem / 24000.0, total / 24000.0))
    if left < 12000:
        return ('only %.2fs would be left of %.1fs — that is too short to play '
                'safely. Keep at least half a second.'
                % (left / 24000.0, total / 24000.0))
    return None


def have_ffmpeg():
    try:
        return subprocess.run(['ffmpeg', '-version'], capture_output=True).returncode == 0
    except OSError:
        return False


def conflicting_mods(mods_dir, evs, ours):
    """Other installed mods that also contain one of the cutscenes we just built.

    Two paks supplying the same cutscene is the problem, not a pak holding many
    cutscenes — voice mods legitimately cover hundreds. When both are installed
    the engine takes each file from whichever container wins, so a scene can end
    up with our retimed camera track beside somebody else's untouched voice
    track. The halves disagree about when everything happens, and it crashes.
    """
    out = []
    if not os.path.isdir(mods_dir) or not evs:
        return out
    want = set(evs)
    for f in sorted(os.listdir(mods_dir)):
        if not f.lower().endswith('.utoc') or f in ours:
            continue
        inside = utoc_cutscenes(os.path.join(mods_dir, f)) or []
        clash = sorted(want.intersection(inside))
        if clash:
            out.append((f, clash, len(inside)))
    return out


def has_work(plan):
    """A plan is worth building if it cuts time, deletes a cue, shortens a line
    or moves a cue.

    `cueMoves` counts on its own. Sliding a sound effect a few frames is a
    complete edit that touches no range at all, and without this the build
    would have called that plan empty and done nothing. `repointMusic` counts
    for the same reason: giving a scene different music is a mod even when not
    a frame of it has been cut.
    """
    return bool(plan.get('removeRanges') or plan.get('disableCues')
                or plan.get('trimLines') or plan.get('cueMoves')
                or plan.get('repointMusic'))


def stage_scene_audio(content_root, area, ev, plan, staged):
    """Apply the cut to the scene's own sound stems and stage them.

    Each SE stem is one stream as long as the whole cutscene, started at t=0, so
    without this the sound plays straight through the edit. Only assets under
    Sound/SE/Cut/<area>/<EV>/ are touched — those belong to this cutscene alone.
    Music is deliberately left out: BGM tracks are shared between scenes, and
    editing one here would change it everywhere it is used.
    """
    src_dir = os.path.join(content_root, 'Sound', 'SE', 'Cut', area, ev)
    if not os.path.isdir(src_dir):
        return []
    total = plan['playbackRange'][1] - plan['playbackRange'][0]
    tr = int(plan.get('tickResolution') or 24000)
    out_dir = os.path.join(staged, 'End', 'Content', 'Sound', 'SE', 'Cut', area, ev)
    scene_sec = total / float(tr)
    done = []
    cues = se_cue_ticks(content_root, area, ev, total)
    for f in sorted(os.listdir(src_dir)):
        if not f.endswith('.uasset'):
            continue
        src = os.path.join(src_dir, f)
        try:
            ss = audio_ripple.streams(open(src, 'rb').read())
        except OSError:
            continue
        if not ss:
            continue
        dur = max(x['dur'] for x in ss)
        # A stem that runs the length of the scene is laid out on scene time and
        # starts at 0. A shorter one is triggered by a cue and plays from its own
        # start, so the cut has to be expressed in ITS clock, not the scene's —
        # otherwise we would silence the wrong part of it. Skipping those
        # outright was why a 15s effect cued just before a cut kept playing over
        # the footage that followed.
        if dur >= 0.8 * scene_sec:
            start, span = 0, total         # laid out on scene time, as proven
        else:
            start = cues.get(f[:-len('.uasset')])
            if start is None:
                continue                   # never cued — nothing to place it on
            span = int(round(dur * tr))
        rel = []
        for a, b in (plan.get('removeRanges') or []):
            x, y = max(a - start, 0), min(b - start, span)
            if y > x:
                rel.append([x, y])
        if not rel:
            continue                       # the cuts miss this sound entirely
        try:
            rep = audio_ripple.ripple_asset(src, os.path.join(out_dir, f),
                                            rel, span, tr)
        except Exception as e:
            done.append((f, 'failed: %r' % e))
            continue
        if rep is None:
            continue                      # no audio in it (asset packs etc.)
        done.append((f, '%d stream(s), %d frames moved, %d silenced'
                     % (len(rep), sum(r['moved'] for r in rep),
                        sum(r['silenced'] for r in rep))))
    return done


SUBSEQ_FILES = patcher.SUBSEQ


def music_names(content_root, area, ev, total):
    """Every BGM track the cutscene calls, by MusicName."""
    out = set()
    d = find_ev_dir(content_root, area, ev)
    for suf in SUBSEQ_FILES:
        p = os.path.join(d, ev + suf + '.uasset')
        if not os.path.exists(p):
            continue
        try:
            data = open(p, 'rb').read()
            for _toff, _tick, pos, size in patcher.compiled_event_blocks(data, total):
                for k, typ, v, _off in patcher.payload_all_fields(data, pos, size):
                    if k == 'MusicName' and typ != 'BoolProperty' and v:
                        out.add(v)
        except Exception:
            continue
    return sorted(out)


def stage_music(content_root, wanted, staged, audiomog=None):
    """Rebuild and stage ONLY the BGM tracks explicitly chosen in the plan.

    Nothing here is automatic. A track is touched only if its cue was selected
    in the editor, because BGM assets are shared between scenes and shipping one
    you did not mean to change silently overrides whatever else supplies it.

    AudioMog decides what to do from the file it is handed: the .uasset means
    EXTRACT, which overwrites the .wav you just replaced. RebuildSettings.json
    is what rebuilds, writing the new binary into the project folder.
    """
    done = []
    if not wanted:
        return done
    bgm = os.path.join(content_root, 'Sound', 'BGM')
    if not os.path.isdir(bgm):
        return done
    for base in sorted({re.sub(r'_\d+$', '', w) for w in wanted}):
        src = os.path.join(bgm, base + '.uasset')
        proj = os.path.join(bgm, base + '_Project')
        settings = os.path.join(proj, 'RebuildSettings.json')
        if not os.path.exists(src):
            done.append((base, 'no such BGM asset')); continue
        if not os.path.exists(settings):
            done.append((base, 'no %s_Project/RebuildSettings.json — extract it '
                               'with AudioMog first' % base)); continue
        if not (audiomog and os.path.exists(audiomog)):
            done.append((base, 'AudioMog.exe not found — drag '
                               'RebuildSettings.json onto it yourself, then build again'))
            continue
        before = {f: os.path.getmtime(os.path.join(proj, f))
                  for f in os.listdir(proj) if f.lower().endswith('.uasset')}
        try:
            subprocess.run([audiomog, settings], input=b'', cwd=proj,
                           capture_output=True, timeout=1800)
        except Exception as e:
            done.append((base, 'AudioMog failed: %r' % e)); continue
        built = None
        for f in sorted(os.listdir(proj)):
            if not f.lower().endswith('.uasset'):
                continue
            p = os.path.join(proj, f)
            if f not in before or os.path.getmtime(p) > before[f]:
                built = p
        if not built:
            done.append((base, 'AudioMog produced no .uasset in %s_Project' % base)); continue
        dst = os.path.join(staged, 'End', 'Content', 'Sound', 'BGM', base + '.uasset')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(built, dst)
        note = 'rebuilt and staged (%.1f MB)' % (os.path.getsize(built) / 1e6)
        if os.path.getsize(built) != os.path.getsize(src):
            note += '  [size differs from the original]'
        done.append((base, note))
    return done


def se_cue_ticks(content_root, area, ev, total):
    """When each SE asset is first triggered, by name.

    A short sound plays from its own beginning, so to cut anything out of it we
    have to know where on the timeline it starts. The cues live in the scene's
    own _Sound and _ManualSE event payloads.
    """
    out = {}
    d = find_ev_dir(content_root, area, ev)
    for suf in ('_Sound', '_ManualSE'):
        p = os.path.join(d, ev + suf + '.uasset')
        if not os.path.exists(p):
            continue
        try:
            data = open(p, 'rb').read()
            for _toff, tick, pos, size in patcher.compiled_event_blocks(data, total):
                for k, typ, v, _off in patcher.payload_all_fields(data, pos, size):
                    if k == 'SeName' and typ != 'BoolProperty' and v:
                        if v not in out or tick < out[v]:
                            out[v] = tick
        except Exception:
            continue
    return out


def find_ev_dir(content_root, area, ev):
    return os.path.join(content_root, 'Cut', 'Game', area, ev)


def expected_match(plan, seq, match):
    """The payload identity a relocated cue carries AFTER the build.

    A move is matched on the name the file still has when `patch_file` runs,
    and a repoint renames it afterwards - it has to be that order, or the move
    would be looking for a name that is no longer there. So by the time
    `verify` reads the staged bytes back, a repointed music cue does not answer
    to the name its own `relocateCues` entry names.

    Without this, repointing a cue you had also dragged turned a correct build
    into `relocatedCues: 0 placed, 1 missing` and refused to pack it.
    """
    want = dict(match or {})
    name = want.get('MusicName')
    if not name:
        return want
    for r in (plan.get('repointMusic') or []):
        if r.get('from') == name and r.get('to') \
                and str(r.get('seq') or '') == str(seq or ''):
            want['MusicName'] = r['to']
            break
    return want


def verify(staged_root, area, ev, plan, usmap, only=None, skip=None, patched=None):
    """Re-read the patched assets and confirm the edit landed as planned.

    Uses only our own parser (standard library) — no third-party packages, so
    this runs anywhere Python does.

    `only`/`skip` are the bisect selections. A file the build DELIBERATELY
    shipped unpatched must not be held to the patched expectations — demanding
    remapped voice cues from an untouched _Voice.uasset fails every bisect
    variant that excludes it, and the variant can then never be packed at all.
    Such checks are recorded as skipped instead.

    `patched` is this cutscene's entry in the patch report. It is read for one
    thing: which relocations `patcher.check_relocation_order` refused. A refused
    move is not a missed one — the cue is remapped onto the join instead, which
    is a worse place for it but a real one — and failing the build over it left
    a correct pak unshipped while the actual complaint (the plan asked for
    something the array could not take) went unsaid.
    """
    import transforms as T
    from payload_events import extract_events

    def untouched(label):
        return (only is not None and label not in only) or \
               (skip is not None and label in skip)

    d = os.path.join(staged_root, 'End', 'Content', 'Cut', 'Game', area, ev)
    out = {'cutscene': ev, 'ok': False, 'checks': []}
    rem = sum(b - a for a, b in (plan.get('removeRanges') or []))
    want = (plan['playbackRange'][1] - plan['playbackRange'][0]) - rem

    def remapped(t):
        d_ = 0
        for a, b in (plan.get('removeRanges') or []):
            if b <= t: d_ += b - a
            elif a <= t < b: return a - d_
        return t - d_

    # 1. playback range of the master sequence
    if untouched('Root'):
        out['checks'].append(['playbackRange', True, 'skipped — Root unpatched'])
    else:
        try:
            a_ = T.Reader2(os.path.join(d, ev + '.uasset'), usmap)
            ms = a_.read_export(a_.find('MovieScene')[0]) or {}
            pr = ms.get('PlaybackRange') or {}
            got_len = (pr.get('upper', 0) - pr.get('lower', 0))
            out['checks'].append(['playbackRange', got_len == want, '%d (want %d)' % (got_len, want)])
        except Exception as e:
            out['checks'].append(['playbackRange', False, repr(e)[:90]])
            return out

    # 2. camera cuts land exactly where the plan says
    if untouched('Camera'):
        out['checks'].append(['cameraCuts', True, 'skipped — Camera unpatched'])
    else:
      try:
        cam = T.Reader2(os.path.join(d, ev + '_Camera.uasset'), usmap)
        got = []
        for i in cam.find('MovieSceneCameraCutSection'):
            sr = (cam.read_export(i) or {}).get('SectionRange') or {}
            if sr.get('lower') is not None:
                got.append((sr['lower'], sr['upper']))
        got.sort()
        src_tl = plan.get('_sourceTimeline')
        if src_tl and os.path.exists(src_tl):
            old = json.load(open(src_tl))
            oc = sorted(tuple(s['range'][:2]) for s in old['sequences']['Camera']['sections']
                        if s.get('type') == 'MovieSceneCameraCutSection')
            # shots are squared up into a partition after remapping, so compare
            # against that same rule rather than the raw remap
            exp = [[remapped(x), remapped(y)] for x, y in oc]
            if patcher.OPTS.get('shots', True):
                exp = evalfield.enforce_partition(exp, want)
                exp = evalfield.park_empty(exp, want)
            exp = sorted(tuple(e) for e in exp)
            good = sum(1 for p, q in zip(got, exp) if p == q)
            out['checks'].append(['cameraCuts', good == len(exp), '%d/%d' % (good, len(exp))])
        ok_end = all(hi <= want for _, hi in got)
        out['checks'].append(['cutsWithinNewEnd', ok_end,
                              'max %d' % (max([h for _, h in got]) if got else 0)])
      except Exception as e:
        out['checks'].append(['cameraCuts', False, repr(e)[:90]])

    # 3. voice cues (read straight out of the compiled templates)
    if untouched('Voice'):
        out['checks'].append(['voiceCues', True, 'skipped — Voice unpatched'])
    else:
      try:
        vf = os.path.join(d, ev + '_Voice.uasset')
        if os.path.exists(vf):
            evs = extract_events(vf, max_tick=want + 1)
            nv = sorted({e['tick'] for e in evs if e.get('tick') is not None})
            src_tl = plan.get('_sourceTimeline')
            if src_tl and os.path.exists(src_tl):
                old = json.load(open(src_tl))
                ov = sorted({e['tick'] for e in old['events']['Voice']
                             if e.get('tick') is not None})
                exp = sorted({remapped(t) for t in ov})
                good = sum(1 for p, q in zip(nv, exp) if p == q)
                out['checks'].append(['voiceCues', good == len(exp) and len(nv) == len(exp),
                                      '%d/%d' % (good, len(exp))])
            out['checks'].append(['noCuesPastEnd', all(t <= want for t in nv),
                                  '%d cues' % len(nv)])
      except Exception as e:
        out['checks'].append(['voiceCues', False, repr(e)[:90]])

    # 4. the fades and streaming commands carried back across a join
    #
    # The whole point of moving a cue is that it still happens, so "it is at the
    # tick the plan named" is the check that matters — a missed match would
    # otherwise leave it collapsed on the join with nothing saying so. Read back
    # out of the patched bytes, not out of the report.
    moves = plan.get('relocateCues') or []
    if moves and patcher.OPTS.get('relocatecues', True):
        try:
            by_seq = {}
            for m in moves:
                by_seq.setdefault(str(m.get('seq') or ''), []).append(m)
            #: moves the patcher declined because they would unsort a Times
            #: array. It said so at the time; this is the same fact as ints.
            refused = set((patched or {}).get('relocateRefusedTicks') or [])
            found = missed = late = held = 0
            for seq, items in by_seq.items():
                if untouched(seq):
                    continue
                for suffix in ('_' + seq, '_' + seq + '_Low'):
                    f = os.path.join(d, ev + suffix + '.uasset')
                    if not os.path.exists(f):
                        continue
                    raw = open(f, 'rb').read()
                    blocks = patcher.compiled_event_blocks(raw, want + 1)
                    for m in items:
                        want_match = expected_match(plan, seq, m.get('match'))

                        def at(tick):
                            return [t for _o, t, pos, size in blocks
                                    if t == int(tick)
                                    and patcher._block_matches(
                                        patcher.payload_all_fields(raw, pos, size),
                                        want_match)]

                        if at(m['newTick']):
                            found += 1
                            if int(m['newTick']) > want:
                                late += 1
                        elif int(m['tick']) in refused and at(remapped(m['tick'])):
                            # Declined and landed on the join, as designed. The
                            # cue still fires, so the pak is shippable; the plan
                            # asking for a tick the array could not take is a
                            # planner bug, reported here and fixed in
                            # `collapse._array_floor`.
                            held += 1
                        else:
                            missed += 1
            note = '%d placed, %d missing, %d past the new end' % (found, missed, late)
            if held:
                note += ', %d held at the join (array order)' % held
            out['checks'].append(['relocatedCues', missed == 0 and late == 0, note])
        except Exception as e:
            out['checks'].append(['relocatedCues', False, repr(e)[:90]])

    # 5. music triggers pointed at a different track
    #
    # Read the name back out of the patched bytes rather than believing the
    # report. The name IS the edit here — there is no timing to inspect and no
    # second symptom — so a repoint that quietly failed to match is a scene
    # that still plays its old music and says nothing about it.
    repoints = plan.get('repointMusic') or []
    if repoints:
        try:
            by_seq = {}
            for r in repoints:
                by_seq.setdefault(str(r.get('seq') or 'ManualSE'), []).append(r)
            done = missing = stale = 0
            for seq, items in by_seq.items():
                if untouched(seq):
                    continue
                f = os.path.join(d, ev + patcher.SEQ_SUFFIX.get(seq, '_' + seq) + '.uasset')
                names = set()
                if os.path.exists(f):
                    for e in extract_events(f, max_tick=want + 1):
                        m = (e.get('props') or {}).get('MusicName')
                        if m:
                            names.add(m)
                for r in items:
                    if r.get('to') in names:
                        done += 1
                        # the old name surviving somewhere else in the same file
                        # is fine (another cue may share it); the old name still
                        # being the ONLY one is the failure, and `to` being
                        # present rules that out
                    elif r.get('from') in names:
                        stale += 1
                    else:
                        missing += 1
            out['checks'].append(['musicRepointed', stale == 0 and missing == 0,
                                  '%d repointed, %d unchanged, %d not found'
                                  % (done, stale, missing)])
        except Exception as e:
            out['checks'].append(['musicRepointed', False, repr(e)[:90]])

    out['ok'] = all(c[1] for c in out['checks'])
    return out


BAT = """@echo off
REM Built by the FF7 Rebirth cutscene tool.
REM Repacks the staged assets into a loadable mod using UnrealReZen.

set REZEN={rezen}
set GAMEDIR={gamedir}
set CONTENT=%~dp0staged
set OUT={outfile}

"%REZEN%" --content-path "%CONTENT%" --compression-format {compression} ^
  --engine-version {engine} --game-dir "%GAMEDIR%" --output-path "%OUT%"

echo.
echo Done. Copy the resulting _P.utoc / _P.ucas / _P.pak into your Paks folder
echo (or point --output-path straight at it) and launch the game.
pause
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', action='append', default=[],
                    help='an edit plan; repeatable')
    ap.add_argument('--plan-dir',
                    help='folder of *_editplan.json / *.json plans — all are built together')
    ap.add_argument('--content', help='.../End/Content')
    ap.add_argument('--usmap')
    ap.add_argument('--out')
    ap.add_argument('--name', default='CutsceneEdit')
    ap.add_argument('--auto-name', metavar='PREFIX',
                    help='fallback sequential name if the cutscene names are unusable')
    ap.add_argument('--mods-subdir', default='~mods',
                    help="subfolder of Paks to write into (default '~mods'; '' = Paks itself)")
    ap.add_argument('--game-dir', default='C:/Program Files (x86)/Steam/steamapps/common/FINAL FANTASY VII REBIRTH/End/Content/Paks')
    ap.add_argument('--rezen', default='UnrealReZen.exe')
    ap.add_argument('--engine-version', default='GAME_UE4_26')
    ap.add_argument('--compression', default='Zlib')
    ap.add_argument('--timelines', default=None, help='browser timelines dir, for verification')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--only-seq', action='append',
                    help='patch only these subsequences (Root, Camera, Character, ...)')
    ap.add_argument('--skip-seq', action='append',
                    help='copy these subsequences through unpatched (for bisecting)')
    ap.add_argument('--identity', action='store_true',
                    help='CONTROL TEST: change nothing, just repack the original assets')
    ap.add_argument('--recompile', action='store_true',
                    help='invalidate cached compiled sequence data so the engine '
                         'rebuilds it from the patched tracks (try this if a mod crashes)')
    # Audio staging adds assets from a different part of the game to the pak.
    # That is a bigger change than patching the cutscene alone, and it has not
    # been proven in-game yet, so it is opt-in.
    ap.add_argument('--priority', action='store_true',
                    help='name the pak so it loads after other mods and wins '
                         '(needed when another mod also contains this cutscene)')
    ap.add_argument('--v1', action='store_true',
                    help='patch exactly as the V1 build did (the one that cut cleanly)')
    ap.add_argument('--no-evalfield', action='store_true',
                    help="don't rewrite the baked evaluation field")
    ap.add_argument('--no-shot-partition', action='store_true',
                    help="don't square camera cuts into a partition")
    ap.add_argument('--shift-durations', action='store_true',
                    help='shift duration fields as timeline positions, as V1 did')
    ap.add_argument('--park-empty', choices=('camera', 'all', 'none'), default='camera',
                    help="where collapsed sections go: 'camera' (default) moves "
                         "only camera cuts, 'all' moves every section class, "
                         "'none' leaves them on the join")
    ap.add_argument('--no-park-empty', action='store_true',
                    help="same as --park-empty none")
    ap.add_argument('--allow-empty', action='store_true',
                    help='build a plan that removes the whole cutscene (or nearly '
                         'all of it) anyway. Refused by default because a sequence '
                         'with no length crashed the game when this was last tried')
    ap.add_argument('--strict', action='store_true',
                    help='refuse to pack when verification fails. Off by default '
                         'because most failures are about what the plan asked '
                         'for rather than about the staged bytes, and refusing '
                         'silently left the previous build installed under the '
                         'new one\'s name')
    ap.add_argument('--no-relocate-cues', action='store_true',
                    help="ignore the plan's relocateCues: let fades and level "
                         "streaming commands collapse onto the join with "
                         "everything else, instead of keeping their distance "
                         "from the end")
    ap.add_argument('--no-collapse-state', action='store_true',
                    help="don't reconcile actor state triggers that collapse onto "
                         "a join (they then fire in whatever order the engine picks)")
    ap.add_argument('--audiomog', default=None,
                    help='AudioMog.exe, used to rebuild a BGM asset whose project '
                         'folder has a replaced .wav in it')
    ap.add_argument('--drop-actor-events', action='store_true',
                    help='neutralise actor show/hide commands that fall inside a '
                         'cut, so the state before the cut carries across the join '
                         '(try this if a character double stays on screen)')
    ap.add_argument('--no-templates', action='store_true',
                    help="don't remap the section times baked into the compiled "
                         "evaluation templates (character animation depends on them)")
    ap.add_argument('--no-hold-values', action='store_true',
                    help="don't correct the values of keys that collapse onto a "
                         "cut (leave the deleted pose showing in the last frames)")
    ap.add_argument('--audio', action='store_true',
                    help="EXPERIMENTAL: also make the scene's sound follow the cut")
    ap.add_argument('--no-audio', action='store_true',
                    help='(default) leave the sound assets alone')
    ap.add_argument('--audit-only', action='store_true',
                    help='just check the installed mods and exit')
    a = ap.parse_args()

    if a.v1:
        a.no_evalfield = a.no_shot_partition = a.shift_durations = True
        a.no_hold_values = a.no_park_empty = a.no_templates = True
        a.no_collapse_state = True
        a.no_relocate_cues = True
    patcher.OPTS['evalfield'] = not a.no_evalfield
    patcher.OPTS['shots'] = not a.no_shot_partition
    patcher.OPTS['durations'] = a.shift_durations
    patcher.OPTS['holdvalues'] = not a.no_hold_values
    patcher.OPTS['parkempty'] = 'none' if a.no_park_empty else 'camera'
    patcher.OPTS['templates'] = not a.no_templates
    patcher.OPTS['dropactorevents'] = a.drop_actor_events
    patcher.OPTS['collapsestate'] = not a.no_collapse_state
    patcher.OPTS['relocatecues'] = not a.no_relocate_cues
    if a.no_evalfield or a.no_shot_partition or a.shift_durations:
        print('patching mode: evalfield=%s shots=%s durations-shifted=%s'
              % (patcher.OPTS['evalfield'], patcher.OPTS['shots'], patcher.OPTS['durations']))

    if a.audit_only:
        mods = os.path.join(a.game_dir.rstrip('/\\'), a.mods_subdir or '')
        print('auditing %s' % mods)
        bad = audit_mods(mods)
        n = len([f for f in os.listdir(mods) if f.lower().endswith('.utoc')]) \
            if os.path.isdir(mods) else 0
        for f, extra in bad:
            print('  [BAD]  %-30s also contains %s' % (f, ', '.join(extra)))
        print('%d mod(s): %d clean, %d contaminated' % (n, n - len(bad), len(bad)))
        if bad:
            print('\nDelete the contaminated ones and rebuild them.')
        return

    for req in ('content', 'usmap', 'out'):
        if not getattr(a, req):
            raise SystemExit('--%s is required' % req)

    plans = list(a.plan)
    if a.plan_dir:
        import glob
        found = sorted(glob.glob(os.path.join(a.plan_dir, '*_editplan.json')))
        if not found:
            found = sorted(glob.glob(os.path.join(a.plan_dir, '*.json')))
        plans += [p for p in found if p not in plans]
    if not plans:
        raise SystemExit('no plans: pass --plan FILE and/or --plan-dir FOLDER')
    print('%d edit plan(s) found' % len(plans))

    # where the pak goes: Paks\~mods by default (loose mods folder)
    paks_dir = a.game_dir.rstrip('/\\')
    out_dir = os.path.join(paks_dir, a.mods_subdir) if a.mods_subdir else paks_dir

    # name the mod after the cutscene(s) it edits
    evs = []
    for pf in plans:
        try:
            j = json.load(open(pf))
            if j.get('cutscene') and has_work(j):
                evs.append(j['cutscene'])
        except Exception:
            pass
    evs = sorted(set(evs))
    if evs and not a.auto_name:
        a.name = evs[0] if len(evs) == 1 else '%s_plus%d' % (evs[0], len(evs) - 1)
    elif evs and a.auto_name:
        a.name = evs[0] if len(evs) == 1 else '%s_plus%d' % (evs[0], len(evs) - 1)
        a.auto_name = None            # cutscene names win over the counter

    # Mods in ~mods load in name order and the last one wins. If another mod
    # also ships this cutscene and sorts after ours, its copy replaces ours and
    # the edit simply never appears — or worse, we win for some files and it
    # wins for others, and the scene disagrees with itself.
    if a.priority:
        a.name = 'zzz_' + a.name

    # sequential mod name: look at what already exists so we never overwrite a build
    if a.auto_name:
        import re as _re
        used = set()
        for d in (out_dir, paks_dir, os.path.dirname(os.path.abspath(a.out)) or '.'):
            try:
                for f in os.listdir(d):
                    m = _re.match(r'^%s(\d+)(_P)?(\.|$)' % _re.escape(a.auto_name), f, _re.I)
                    if m:
                        used.add(int(m.group(1)))
            except OSError:
                pass
        n = 1
        while n in used:
            n += 1
        a.name = '%s%02d' % (a.auto_name, n)
        a.out = os.path.join(os.path.dirname(os.path.abspath(a.out)) or '.', a.name) \
                if os.path.basename(os.path.abspath(a.out)).lower().startswith(a.auto_name.lower()) \
                else a.out
        print('mod name: %s' % a.name)

    staged = os.path.join(a.out, 'staged')
    # A pak must contain exactly what this build's plans specify — nothing more.
    # Leftover files from earlier builds end up in every later pak, and two mods
    # carrying different versions of the same package crash the game.
    if os.path.isdir(staged):
        shutil.rmtree(staged)
    os.makedirs(staged, exist_ok=True)
    usmap = Usmap(a.usmap)
    only = set(a.only_seq) if a.only_seq else None
    skip = set(a.skip_seq) if a.skip_seq else None
    report = {'mod': a.name, 'cutscenes': [], 'verification': [],
              # identify the variant this report came from — reports overwrite
              # each other, so a surviving one must say what produced it
              'options': {'evalfield': patcher.OPTS['evalfield'],
                          'shots': patcher.OPTS['shots'],
                          'durations': patcher.OPTS['durations'],
                          'holdvalues': patcher.OPTS['holdvalues'],
                          'parkempty': patcher.OPTS['parkempty'],
                          'templates': patcher.OPTS['templates'],
                          'dropActorEvents': patcher.OPTS['dropactorevents'],
                          'collapseState': patcher.OPTS['collapsestate'],
                          'relocateCues': patcher.OPTS['relocatecues'],
                          'recompile': a.recompile, 'identity': a.identity,
                          'onlySeq': sorted(only) if only else None,
                          'skipSeq': sorted(skip) if skip else None}}

    for pf in plans:
        try:
            plan = json.load(open(pf))
        except Exception as e:
            print('[skip] %s: unreadable (%r)' % (os.path.basename(pf), e)); continue
        if 'cutscene' not in plan or not ('removeRanges' in plan or 'disableCues' in plan
                                          or 'trimLines' in plan or 'repointMusic' in plan):
            print('[skip] %s: not an edit plan' % os.path.basename(pf)); continue
        bad = plan_problem(plan)
        if bad and not a.allow_empty:
            raise SystemExit('\n  %s cannot be built:\n    %s\n'
                             '\n  Pass --allow-empty to build it anyway.\n'
                             % (plan.get('cutscene', pf), bad))
        if bad:
            print('   [!] %s: %s' % (plan.get('cutscene', pf), bad))
            print('   [!] building it anyway because --allow-empty was passed.')
        ev = plan['cutscene']; area = plan.get('area')
        if not area:
            raise SystemExit('plan %s has no "area"' % pf)
        if not has_work(plan):
            print('[skip] %s: plan changes nothing' % ev); continue
        ev_dir = find_ev_dir(a.content, area, ev)
        if not os.path.isdir(ev_dir):
            raise SystemExit('cutscene folder not found: %s' % ev_dir)
        print('[patch] %s (%d cut(s))' % (ev, len(plan['removeRanges'])), flush=True)
        rep = patcher.apply_plan(ev_dir, plan, staged, usmap, recompile=a.recompile,
                                 only={'__none__'} if a.identity else only,
                                 skip=skip)
        report['cutscenes'].append(rep)

        if a.identity:
            print('   identity build — assets are byte-identical to the game originals')
            report['verification'].append({'cutscene': ev, 'ok': True,
                                           'checks': [['identity', True, 'unmodified']]})
            continue
        a.no_audio = a.no_audio or not a.audio
        # Rippling a scene's own SE streams rewrites HCA frames in place and
        # needs nothing external. Only shortening a spoken line goes through
        # ffmpeg, so only that should be gated on it — requiring ffmpeg for all
        # audio work turned the common case off for no reason.
        if not a.no_audio and (plan.get('trimLines') or []) and not have_ffmpeg():
            print('   [audio] dialogue trimming SKIPPED — ffmpeg is not installed.',
                  flush=True)
        if not a.no_audio:
            for f, note in stage_scene_audio(a.content, area, ev, plan, staged):
                print('   [audio] %-34s %s' % (f, note), flush=True)
            # A repointed trigger needs nothing staged at all: the bank it now
            # names is already in the game, and the cutscene asks for it by
            # name at runtime. That is the difference from `replaceMusic`
            # below, which rebuilds a bank and therefore changes it everywhere.
            #
            # a replaced music track, if its AudioMog project has newer audio
            for f, note in stage_music(a.content, plan.get('replaceMusic') or [],
                                       staged, a.audiomog):
                print('   [music] %-34s %s' % (f, note), flush=True)
            # (music staging does nothing unless a track is explicitly selected)

        if a.timelines:
            plan['_sourceTimeline'] = os.path.join(a.timelines, ev + '.json')
        v = verify(staged, area, ev, plan, usmap, only=only, skip=skip,
                   patched=rep)
        report['verification'].append(v)
        print('   verify: %s' % ('PASS' if v['ok'] else 'FAIL'),
              ' '.join('%s=%s' % (c[0], c[2]) for c in v['checks']), flush=True)

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        print('[!] could not create %s (%s)' % (out_dir, e))
    outfile = os.path.join(out_dir, a.name + '_P.utoc')
    print('output: %s' % outfile)
    bat = BAT.format(rezen=a.rezen, gamedir=paks_dir, outfile=outfile,
                     engine=a.engine_version, compression=a.compression)
    open(os.path.join(a.out, 'build_mod.bat'), 'w').write(bat)
    cmd = ['--content-path', staged, '--compression-format', a.compression,
           '--engine-version', a.engine_version, '--game-dir', paks_dir,
           '--output-path', outfile]
    report['rezenCommand'] = '"%s" %s' % (a.rezen, ' '.join('"%s"' % c if ' ' in c else c for c in cmd))
    json.dump(report, open(os.path.join(a.out, 'patch_report.json'), 'w'), indent=1)

    files = sum(len(c['files']) for c in report['cutscenes'])
    allok = all(v['ok'] for v in report['verification']) if report['verification'] else None
    print('\nstaged %d file(s) for %d cutscene(s) -> %s' % (files, len(report['cutscenes']), staged))
    print('verification: %s' % ('all passed' if allok else 'SEE patch_report.json'))
    print('\nReZen command:\n  %s' % report['rezenCommand'])

    # The message here has to match what the next twenty lines actually do.
    # It used to say "not packing" above a commented-out `sys.exit(1)`, and
    # then pack: a build that installed fine read as a build that had not
    # happened, and the stale-pak warning below it was untrue as well. Say
    # which it is, once, from the same condition that decides it.
    if report['verification'] and not all(v['ok'] for v in report['verification']):
        for v in report['verification']:
            for name, ok, note in v['checks']:
                if not ok:
                    print('\n[!] %s: %s — %s' % (v['cutscene'], name, note))
        print('    See patch_report.json.')
        if a.strict:
            raise SystemExit('[!] not packing (--strict).')
        if a.run:
            print('    Packing anyway — pass --strict to refuse instead.')
        else:
            print('    NOTE: any pak already in %s is from an EARLIER build —' % out_dir)
            print('    if you launch the game now you are testing THAT build, not this one.')

    if a.run:
        rezen = os.path.abspath(a.rezen) if os.path.exists(a.rezen) else shutil.which(a.rezen)
        if not rezen:
            print('\n[!] UnrealReZen not found (%s) — run build_mod.bat on Windows.' % a.rezen)
            return
        rezen_dir = os.path.dirname(rezen)
        # ReZen resolves oo2core_9_win64.dll relative to its working directory, so run
        # it from its own folder and make sure the DLL is actually there.
        oodle = 'oo2core_9_win64.dll'
        if not os.path.exists(os.path.join(rezen_dir, oodle)):
            here = os.path.dirname(os.path.abspath(__file__))
            for cand in (os.path.join(os.getcwd(), oodle), os.path.join(here, oodle)):
                if os.path.exists(cand):
                    try:
                        shutil.copy2(cand, os.path.join(rezen_dir, oodle))
                        print('copied %s next to UnrealReZen.exe' % oodle)
                    except OSError as e:
                        print('[!] could not copy %s: %s' % (oodle, e))
                    break
        if not os.path.exists(os.path.join(rezen_dir, oodle)):
            print('\n[!] %s is missing from %s' % (oodle, rezen_dir))
            print('    ReZen needs it there to read the game archives.')
            return
        # UnrealReZen indexes EVERY .utoc under --game-dir to build its asset table.
        # Our own installed mods live in Paks\~mods, i.e. inside that tree, so their
        # contents get folded into each new pak — every mod ends up containing all the
        # others, and duplicate packages across containers crash the game.
        # Hide them for the duration of the pack, then put them back.
        stash = os.path.join(os.path.abspath(a.out), '_mods_stash')
        hidden = False
        if os.path.isdir(out_dir) and os.path.abspath(out_dir).startswith(
                os.path.abspath(paks_dir) + os.sep):
            try:
                if os.path.isdir(stash):
                    shutil.rmtree(stash)
                shutil.move(out_dir, stash)
                hidden = True
                print('temporarily moved %d existing mod file(s) out of the way'
                      % len(os.listdir(stash)))
            except OSError as e:
                print('[!] could not move existing mods aside (%s) — the new pak may '
                      'pick up their contents' % e)
        os.makedirs(out_dir, exist_ok=True)
        # If the stash failed the old pak may still be sitting on the output
        # name. Clear it now: if ReZen then fails, the game must NOT be left
        # silently playing the previous build under this run's name.
        for stale in (outfile, outfile[:-5] + '.ucas', outfile[:-5] + '.pak'):
            try:
                if os.path.exists(stale):
                    os.remove(stale)
            except OSError as e:
                raise SystemExit('\n[!] cannot replace %s (%s) — is the game '
                                 'running? Close it and rebuild.'
                                 % (os.path.basename(stale), e))
        rc = 1
        try:
            print('\nrunning UnrealReZen (cwd=%s)...' % rezen_dir)
            rc = subprocess.run([rezen] + cmd, check=False, cwd=rezen_dir).returncode
        finally:
            if hidden:
                import re as _re
                # An older build of a cutscene we just rebuilt — under ANY of our
                # names (with/without the zzz_ priority prefix) — must not come
                # back: two of our paks for one scene either shadow the new build
                # or split its files, and either way the test lies.
                stale_pat = _re.compile(
                    r'^(zzz_)?(%s)(_plus\d+)?_P\.(utoc|ucas|pak)$'
                    % '|'.join(_re.escape(e) for e in evs)) if evs else None
                ours = {os.path.basename(outfile),
                        os.path.basename(outfile)[:-5] + '.ucas',
                        os.path.basename(outfile)[:-5] + '.pak'}
                dropped = []
                for f in os.listdir(stash):
                    src_f, dst_f = os.path.join(stash, f), os.path.join(out_dir, f)
                    if stale_pat and f not in ours and stale_pat.match(f):
                        dropped.append(f)
                        continue                         # left in the stash, deleted below
                    if not os.path.exists(dst_f):        # never clobber what we just built
                        shutil.move(src_f, dst_f)
                shutil.rmtree(stash, ignore_errors=True)
                print('restored previously installed mods')
                if dropped:
                    print('removed stale earlier build(s) of this cutscene: %s'
                          % ', '.join(sorted(dropped)))
        if rc != 0 or not os.path.exists(outfile):
            print('\n[!] UnrealReZen FAILED (exit %s)%s' % (
                rc, '' if os.path.exists(outfile) else ' — no pak was written'))
            print('    Nothing (or a stale pak) is installed for this run. Do not test.')
            sys.exit(1)

        # did the pak come out containing only what we asked for?
        inside = utoc_cutscenes(outfile)
        if inside is not None:
            extra = [e for e in inside if e not in evs]
            if extra:
                print('\n[!] %s also contains %s' % (os.path.basename(outfile), ', '.join(extra)))
                print('    A pak must hold only its own cutscene. Delete every mod from')
                print('    %s and rebuild them.' % out_dir)
            else:
                print('pak audit: contains only %s' % ', '.join(inside or evs))

        # the thing that actually breaks a build: two mods supplying one cutscene
        clashes = conflicting_mods(out_dir, evs, {os.path.basename(outfile)})
        if clashes:
            print('\n[!] CONFLICT — another installed mod already contains the '
                  'cutscene(s) you just built:')
            for f, clash, total in clashes:
                print('      %-40s %s  (that mod covers %d cutscene(s))'
                      % (f, ', '.join(clash), total))
            print('\n    Both paks supply the same scene, so the game takes some files')
            print('    from one and some from the other. Half the scene gets the new')
            print('    timing and half keeps the old, and it crashes.')
            print('\n    Move the mod(s) above out of ~mods, test again, and put them')
            print('    back afterwards if you want them.')


if __name__ == '__main__':
    main()
