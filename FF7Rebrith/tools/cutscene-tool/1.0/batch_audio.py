"""batch_audio.py — build VO tracks for every cutscene and refresh its viewer.

Resumable: skips cutscenes whose .ogg already exists.
Usage: python3 batch_audio.py <Content/Cut/Game> <browserdir> [--workers N] [--limit N]
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ProcessPoolExecutor

import audio_build
import make_viewer

WITH_BGM = '--bgm' in sys.argv
WITH_SE = '--se' in sys.argv


def find_ev_dir(game_dir, area, ev):
    return os.path.join(game_dir, area, ev)


def work(job):
    game_dir, outdir, ev = job
    tj = os.path.join(outdir, 'timelines', ev + '.json')
    try:
        data = json.load(open(tj))
    except Exception as e:
        return ev, None, 'json: %r' % e
    ev_dir = find_ev_dir(game_dir, data.get('area', ''), ev)
    if not os.path.isdir(ev_dir):
        return ev, None, 'missing dir'
    ogg = os.path.join(outdir, 'timelines', 'audio', ev + '.ogg')
    try:
        info = audio_build.build(ev_dir, data, ogg, with_bgm=WITH_BGM, with_se=WITH_SE)
    except Exception as e:
        return ev, None, repr(e)[:80]
    if not info:
        return ev, None, 'no voice'
    info.pop('lines', None)
    info['file'] = 'audio/' + ev + '.ogg'
    data['audio'] = info
    tmp = tj + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, default=str)
    os.replace(tmp, tj)
    make_viewer.build(tj, os.path.join(outdir, 'timelines', ev + '.html'), nav=True)
    return ev, info, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    game_dir, outdir = args[0], args[1]
    workers = int(sys.argv[sys.argv.index('--workers')+1]) if '--workers' in sys.argv else 2
    limit = int(sys.argv[sys.argv.index('--limit')+1]) if '--limit' in sys.argv else None

    os.makedirs(os.path.join(outdir, 'timelines', 'audio'), exist_ok=True)
    man_path = os.path.join(outdir, 'manifest.json')
    manifest = json.load(open(man_path))

    todo = []
    for ev, row in sorted(manifest.items()):
        if not row.get('lines'):
            continue
        ogg = os.path.join(outdir, 'timelines', 'audio', ev + '.ogg')
        if os.path.exists(ogg):
            # already built; when adding BGM, skip only those already mixed with it
            if not (WITH_BGM or WITH_SE):
                row['audio'] = True
                continue
            try:
                a = json.load(open(os.path.join(outdir, 'timelines', ev + '.json'))).get('audio') or {}
                want = 'vo' + ('+bgm' if WITH_BGM else '') + ('+se' if WITH_SE else '')
                if a.get('mix') == want:
                    row['audio'] = True
                    continue
            except Exception:
                pass
        todo.append((game_dir, outdir, ev))
    if limit:
        todo = todo[:limit]
    print('voiced cutscenes pending: %d (workers=%d)' % (len(todo), workers), flush=True)

    done = fail = 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for ev, info, err in ex.map(work, todo):
            if info:
                manifest.setdefault(ev, {})['audio'] = True
                done += 1
            else:
                fail += 1
                if fail <= 8:
                    print('  [skip]', ev, err, flush=True)
            if (done + fail) % 20 == 0:
                tmp = man_path + '.tmp'
                json.dump(manifest, open(tmp, 'w')); os.replace(tmp, man_path)
                el = time.time() - t0
                print('  %d ok / %d skip  (%.2fs each)' % (done, fail, el/max(1, done+fail)), flush=True)
    tmp = man_path + '.tmp'
    json.dump(manifest, open(tmp, 'w')); os.replace(tmp, man_path)
    print('audio built: %d ok, %d skipped' % (done, fail))


if __name__ == '__main__':
    main()
