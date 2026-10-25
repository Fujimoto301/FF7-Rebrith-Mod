"""batch_build.py — extract every cutscene and build the browser.

Usage: python3 batch_build.py <Content/Cut/Game dir> <Mappings.usmap> <outdir> [--limit N]
Then:  python3 batch_build.py ... --index-only   (rebuild index.html from manifest)

Resume
------
By default a cutscene is considered done when its timeline **HTML** exists,
which is right for the browser build. With `--no-html` the HTML is never
written, so resume keys on the timeline **JSON** instead - otherwise every run
would rebuild all 755 scenes from scratch.

--no-html
---------
The desktop editor (`editor_qt`) reads `<ev>.json`, `manifest.json` and the
audio, and no HTML at all. The 755 viewer pages are 182 MB and were archived
out of the working tree, so building them on a fresh install would recreate
something nobody asked for and break resume at the same time. `setup.py` always
passes this; the browser build does not.
"""
import sys, os, json, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if '--quiet' in sys.argv:
    # Before extract_timeline, so the import-time texture warning is caught too.
    import vendorpath
    vendorpath.quiet_expected_noise(False)
from extract_timeline import extract_cutscene
import make_viewer

INDEX_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>FF7 Rebirth — Cutscene Browser</title>
<style>
  :root { --bg:#14151a; --panel:#1e2028; --panel2:#262935; --text:#e8e9ed; --dim:#8b8fa3;
          --accent:#57b3ff; --grid:#2c2f3b; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--text); font:13px/1.5 "Segoe UI",system-ui,sans-serif; }
  header { padding:16px 24px; background:var(--panel); border-bottom:1px solid #000;
           display:flex; gap:20px; align-items:baseline; flex-wrap:wrap; }
  h1 { font-size:18px; }
  header .meta { color:var(--dim); font-size:12px; }
  #search { margin-left:auto; background:var(--panel2); color:var(--text); border:1px solid #4a4f63;
            border-radius:5px; padding:6px 12px; font-size:13px; width:300px; }
  #areas { padding:10px 24px; display:flex; gap:8px; flex-wrap:wrap; }
  #areas button { background:var(--panel2); color:var(--dim); border:1px solid #4a4f63;
                  border-radius:14px; padding:3px 12px; cursor:pointer; font-size:12px; }
  #areas button.on { background:var(--accent); color:#08131e; border-color:var(--accent); }
  table { width:100%; border-collapse:collapse; }
  th, td { text-align:left; padding:7px 12px; border-bottom:1px solid var(--grid); font-size:12px; }
  th { position:sticky; top:0; background:var(--panel); color:var(--dim); cursor:pointer; z-index:2; }
  tbody tr { cursor:pointer; }
  tbody tr:hover { background:#20242f; }
  td a { color:var(--accent); text-decoration:none; font-weight:600; }
  .dim { color:var(--dim); }
  .num { text-align:right; font-variant-numeric:tabular-nums; }
  .preview { max-width:520px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:var(--dim); }
</style>
</head>
<body>
<header>
  <h1>FF7 Rebirth — Cutscene Browser</h1>
  <span class="meta" id="stats"></span>
  <input id="search" placeholder="Search name, area, actor, dialogue…  ( / to focus )">
</header>
<div id="areas"></div>
<table>
  <thead><tr>
    <th data-k="ev">Cutscene</th><th data-k="area">Area</th>
    <th data-k="dur" class="num">Duration</th><th data-k="cuts" class="num">Cuts</th>
    <th data-k="lines" class="num">Lines</th><th data-k="cast" class="num">Cast</th><th>First line</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>
<script>
const M = __MANIFEST__;
let areaFilter = null, sortK = 'ev', sortAsc = true;
const rowsEl = document.getElementById('rows');
const fmtDur = s => { const m = Math.floor(s/60); return m + ':' + (s - m*60).toFixed(1).padStart(4,'0'); };
document.getElementById('stats').textContent =
  `${M.length} cutscenes · ${fmtDur(M.reduce((a,r)=>a+r.dur,0))} total · ${M.reduce((a,r)=>a+r.lines,0)} voiced lines`;
const areas = [...new Set(M.map(r => r.area))].sort();
const areasEl = document.getElementById('areas');
for (const a of ['All', ...areas]) {
  const b = document.createElement('button');
  b.textContent = a;
  b.onclick = () => { areaFilter = a === 'All' ? null : a;
    [...areasEl.children].forEach(x => x.classList.toggle('on', x === b)); render(); };
  if (a === 'All') b.classList.add('on');
  areasEl.appendChild(b);
}
document.querySelectorAll('th[data-k]').forEach(th => th.onclick = () => {
  const k = th.dataset.k;
  if (sortK === k) sortAsc = !sortAsc; else { sortK = k; sortAsc = true; }
  render();
});
const searchEl = document.getElementById('search');
searchEl.oninput = render;
window.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== searchEl) { e.preventDefault(); searchEl.focus(); }
});
function render() {
  const q = searchEl.value.toLowerCase();
  let list = M.filter(r => !areaFilter || r.area === areaFilter);
  if (q) list = list.filter(r => (r.ev + ' ' + r.area + ' ' + r.preview + ' ' + (r.search||'')).toLowerCase().includes(q));
  list.sort((a,b) => {
    const va = a[sortK], vb = b[sortK];
    const c = typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb));
    return sortAsc ? c : -c;
  });
  rowsEl.innerHTML = '';
  for (const r of list) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><a href="timelines/${r.ev}.html">${r.ev}</a></td><td class="dim">${r.area}</td>` +
      `<td class="num">${fmtDur(r.dur)}</td><td class="num">${r.cuts}</td><td class="num">${r.lines}</td>` +
      `<td class="num">${r.cast ? '👤'+r.cast : '<span class="dim">–</span>'}${r.audio?' 🔊':''}${r.music?'🎵':''}${r.sfx?'💥':''}${r.vfx?'✨':''}${r.lip?'👄':''}</td>` +
      `<td class="preview">${r.preview || ''}</td>`;
    tr.onclick = e => { if (e.target.tagName !== 'A') location.href = `timelines/${r.ev}.html`; };
    rowsEl.appendChild(tr);
  }
}
render();
</script>
</body>
</html>'''


def esc(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')


def save_manifest(path, manifest):
    """Atomic write — a killed process must not leave a truncated manifest."""
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(manifest, f)
    os.replace(tmp, path)


def row_from_data(data, ev):
    pb = (data['sequences'].get('Root', {}).get('meta', {}) or {}).get('playbackRange') or [0, 0]
    tick = ((data['sequences'].get('Root', {}).get('meta', {}) or {}).get('tickResolution') or {}).get('Numerator', 24000)
    cam = data['sequences'].get('Camera', {}).get('sections', [])
    cuts = sum(1 for s in cam if s.get('type') == 'MovieSceneCameraCutSection')
    ev_events = data.get('events', {})
    voice = [e for e in ev_events.get('Voice', []) if isinstance(e, dict) and e.get('tick') is not None]
    texted = [e for e in voice if e.get('text')]
    preview = ''
    if texted:
        e = texted[0]
        preview = (e.get('actor', '') + ': ' if e.get('actor') else '') + e['text']
    search = ' '.join(sorted({e.get('actor', '') for e in voice if e.get('actor')}))
    search += ' ' + ' '.join((e.get('text') or '')[:60] for e in texted[:20])
    scene = data.get('scene') or {}
    cast = [a['label'] for a in (scene.get('actors') or []) if a.get('kind') in ('pc', 'np')]
    return {'ev': ev, 'area': data['area'], 'dur': (pb[1]-pb[0])/tick if tick else 0,
            'cuts': cuts, 'lines': len(voice), 'preview': esc(preview[:140]),
            'cast': len(scene.get('actors') or []),
            'search': esc((search + ' ' + ' '.join(cast))[:1200])}


def build_one(ev_dir, usmap, outdir, with_audio=False, html=True):
    ev = os.path.basename(ev_dir.rstrip('/'))
    data = extract_cutscene(ev_dir, usmap, compact=True, verbose=False)
    # keep any audio track already built for this cutscene
    prev = os.path.join(outdir, 'timelines', ev + '.json')
    if os.path.exists(prev):
        try:
            old = json.load(open(prev)).get('audio')
            if old and os.path.exists(os.path.join(outdir, 'timelines', 'audio', ev + '.ogg')):
                data['audio'] = old
        except Exception:
            pass
    if with_audio:
        try:
            import audio_build
            ogg = os.path.join(outdir, 'timelines', 'audio', ev + '.ogg')
            info = audio_build.build(ev_dir, data, ogg)
            if info:
                info.pop('lines', None)
                info['file'] = 'audio/' + ev + '.ogg'
                data['audio'] = info
        except Exception as e:
            print('[audio fail]', ev, repr(e)[:80], flush=True)
    jpath = os.path.join(outdir, 'timelines', ev + '.json')
    tmp = jpath + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, default=str)
    os.replace(tmp, jpath)
    if html:
        make_viewer.build(jpath, os.path.join(outdir, 'timelines', ev + '.html'),
                          nav=True)
    row = row_from_data(data, ev)
    a = data.get('audio') or {}
    row['audio'] = bool(a); row['music'] = bool(a.get('bgm')); row['sfx'] = bool(a.get('se'))
    row['vfx'] = len(data.get('vfx') or [])
    return row


def write_index(outdir, manifest):
    rows = sorted(manifest.values(), key=lambda r: (r['area'], r['ev']))
    html = INDEX_TEMPLATE.replace('__MANIFEST__', json.dumps(rows))
    with open(os.path.join(outdir, 'index.html'), 'w') as f:
        f.write(html)


def main():
    global WITH_AUDIO
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    game_dir, usmap, outdir = args[0], args[1], args[2]
    limit = None
    WITH_AUDIO = '--audio' in sys.argv
    no_html = '--no-html' in sys.argv
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    os.makedirs(os.path.join(outdir, 'timelines'), exist_ok=True)
    man_path = os.path.join(outdir, 'manifest.json')
    manifest = {}
    if os.path.exists(man_path):
        try:
            manifest = json.load(open(man_path))
        except Exception:
            print('manifest unreadable — rebuilding from timelines/')

    if '--repair' in sys.argv or not manifest:
        tdir = os.path.join(outdir, 'timelines')
        for f in sorted(os.listdir(tdir)):
            if not f.endswith('.json'):
                continue
            ev = f[:-5]
            if ev in manifest:
                continue
            # The JSON in hand is the evidence the scene was extracted; the
            # HTML is only evidence when we are building HTML.
            if not no_html and not os.path.exists(os.path.join(tdir, ev + '.html')):
                continue
            try:
                manifest[ev] = row_from_data(json.load(open(os.path.join(tdir, f))), ev)
            except Exception:
                pass
        save_manifest(man_path, manifest)
        print('manifest repaired:', len(manifest), 'entries')

    if '--index-only' in sys.argv:
        write_index(outdir, manifest)
        print('index rebuilt with', len(manifest), 'entries')
        return

    evs = []
    for area in sorted(os.listdir(game_dir)):
        adir = os.path.join(game_dir, area)
        if not os.path.isdir(adir):
            continue
        for ev in sorted(os.listdir(adir)):
            if ev.startswith('EV_') and os.path.isdir(os.path.join(adir, ev)):
                evs.append(os.path.join(adir, ev))
    def needs(p):
        ev = os.path.basename(p)
        if ev not in manifest:
            return True
        artefact = ev + ('.json' if no_html else '.html')
        if not os.path.exists(os.path.join(outdir, 'timelines', artefact)):
            return True
        return 'vfx' not in manifest[ev]        # rebuilt for the new cue types
    pending = [p for p in evs if needs(p)]
    print('total %d cutscenes, %d pending' % (len(evs), len(pending)))
    done = 0
    t0 = time.time()
    for p in pending:
        ev = os.path.basename(p)
        try:
            row = build_one(p, usmap, outdir, with_audio=WITH_AUDIO,
                            html=not no_html)
            manifest[ev] = row
            done += 1
            if done % 10 == 0:
                save_manifest(man_path, manifest)
                el = time.time() - t0
                print('  %d/%d done (%.1fs/ea)' % (done, len(pending), el/done), flush=True)
        except Exception as e:
            print('[FAIL]', ev, repr(e)[:120], flush=True)
            manifest[ev] = manifest.get(ev) or {'ev': ev, 'area': os.path.basename(os.path.dirname(p)),
                                                'dur': 0, 'cuts': 0, 'lines': 0,
                                                'preview': 'extract failed', 'search': ''}
        if limit and done >= limit:
            break
    json.dump(manifest, open(man_path, 'w'))
    if not no_html:
        write_index(outdir, manifest)
    print('done: %d built this run, %d total in manifest' % (done, len(manifest)))


if __name__ == '__main__':
    main()
