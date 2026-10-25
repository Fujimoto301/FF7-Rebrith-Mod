"""make_viewer.py — bundle extracted timeline JSON into a standalone HTML editor/viewer.

Features: scrubber/playhead with realtime preview, live subtitle window,
camera-cut delete editing (click + DEL), Ctrl+Z/Ctrl+Shift+Z undo/redo,
Ctrl+S exports an edit-plan JSON for the (future) write-back patcher.

Usage: python3 make_viewer.py <timeline.json> <out.html> [--nav]
"""
import sys, json, os, shutil

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__ — FF7R Cutscene Editor</title>
<style>
  :root {
    --bg:#14151a; --panel:#1e2028; --panel2:#262935; --text:#e8e9ed; --dim:#8b8fa3;
    --accent:#57b3ff; --shot:#3d6fa8; --cut:#5a8f5c; --evt:#a8783d; --sel:#ffd257;
    --vo:#7a3b6e; --subt:#3b6e7a; --del:#8f3a3a; --grid:#2c2f3b; --play:#ff5757;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { height:100%; }
  body { background:var(--bg); color:var(--text); font:13px/1.5 "Segoe UI",system-ui,sans-serif;
         display:flex; flex-direction:column; }
  header { padding:10px 20px; background:var(--panel); border-bottom:1px solid #000;
           display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }
  header h1 { font-size:16px; font-weight:600; }
  header a { color:var(--accent); text-decoration:none; font-size:12px; }
  header .meta { color:var(--dim); font-size:11px; }
  #subwin { background:#101116; border-bottom:1px solid #000; padding:10px 20px 12px;
            text-align:center; min-height:74px; }
  #subActor { color:var(--accent); font-size:12px; font-weight:600; letter-spacing:.5px; }
  #subText { font-size:17px; margin-top:2px; min-height:24px; }
  #subText .idle { color:#3c3f4d; font-size:13px; }
  #infoline { color:var(--dim); font-size:11px; margin-top:6px; display:flex; gap:18px; justify-content:center; flex-wrap:wrap; }
  #infoline b { color:var(--text); font-weight:600; }
  #toolbar { padding:7px 20px; display:flex; gap:8px; align-items:center; background:var(--panel2);
             border-bottom:1px solid #000; flex-wrap:wrap; }
  #toolbar button { background:#333748; color:var(--text); border:1px solid #4a4f63; border-radius:4px;
                    padding:4px 11px; cursor:pointer; font-size:12px; }
  #toolbar button:hover { background:#3e4356; }
  #toolbar button:disabled { opacity:.4; cursor:default; }
  #toolbar .sep { width:1px; height:20px; background:#4a4f63; margin:0 4px; }
  #toolbar .hint { color:var(--dim); font-size:11px; }
  #editInfo { color:var(--sel); font-size:12px; }
  #warnbar { padding:4px 20px; background:#181a21; border-bottom:1px solid #000; min-height:22px;
             font-size:11px; color:var(--dim); }
  #warnbar .warn { color:#ffb3b3; font-weight:600; }
  #buildLine { margin-left:14px; }
  #buildLine.busy { color:var(--accent); } #buildLine.good { color:#8fe28f; }
  #buildLine.bad { color:#ffb3b3; font-weight:600; }
  #buildlog { display:none; position:relative; max-height:230px; overflow:auto;
              background:#0d0f14; border-bottom:1px solid #000; padding:8px 20px 10px; }
  #buildlog pre { font:11px/1.5 ui-monospace,Consolas,monospace; color:#b9bed0; white-space:pre-wrap; }
  #logClose { position:absolute; top:6px; right:14px; background:#333748; color:var(--text);
              border:1px solid #4a4f63; border-radius:4px; font-size:11px; padding:2px 8px; cursor:pointer; }
  #timeline { position:relative; overflow:auto; flex:1; user-select:none; }
  #scrub { position:sticky; top:0; z-index:8; height:40px; background:var(--panel);
           border-bottom:1px solid var(--grid); cursor:crosshair; }
  .rt { position:absolute; top:0; font-size:10px; color:var(--dim); border-left:1px solid var(--grid);
        padding:2px 0 0 4px; height:40px; white-space:nowrap; pointer-events:none; }
  #rows { position:relative; }
  .trackrow { position:relative; height:34px; min-height:34px; border-bottom:1px solid var(--grid); }
  .tracklabel { position:sticky; left:0; z-index:5; display:inline-block; width:150px; height:100%;
                background:var(--panel); border-right:1px solid var(--grid); padding:8px 10px;
                font-size:11px; color:var(--dim); font-weight:600; overflow:hidden; white-space:nowrap; }
  .lane { position:absolute; left:150px; top:0; right:0; height:100%; }
  .sec { position:absolute; top:5px; height:24px; border-radius:3px; font-size:10px; line-height:24px;
         padding:0 5px; overflow:hidden; white-space:nowrap; cursor:pointer; color:#fff;
         border:1px solid rgba(0,0,0,.45); }
  .sec:hover { filter:brightness(1.25); z-index:4; overflow:visible; }
  .sec.selected { outline:2px solid var(--sel); z-index:4; }
  /* stacked (overlapping) cues get a hairline so the pile is readable */
  .sec.stacked { box-shadow:0 1px 0 rgba(0,0,0,.5); }
  .tracklabel .stackcount { color:var(--accent); font-weight:600; cursor:pointer; }
  .tracklabel .stackcount:hover { text-decoration:underline; }
  .sec.deleted { background:repeating-linear-gradient(45deg, var(--del) 0 6px, #582525 6px 12px) !important;
                 color:#f8bcbc; text-decoration:line-through; }
  .shotsec { background:var(--shot); } .cutsec { background:var(--cut); }
  .evtsec { background:var(--evt); }  .othersec { background:#555b70; }
  .vosec { background:var(--vo); }    .subtsec { background:var(--subt); }
  #overlay { position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none; z-index:6; }
  .delband { position:absolute; top:0; bottom:0;
             background:repeating-linear-gradient(45deg, rgba(143,58,58,.42) 0 7px, rgba(88,37,37,.42) 7px 14px);
             border-left:1px solid #ff6b6b; border-right:1px solid #ff6b6b; }
  .delband span { position:absolute; top:2px; left:3px; font-size:9px; color:#ffc9c9;
                  background:rgba(0,0,0,.55); padding:0 3px; border-radius:2px; white-space:nowrap; }
  .selband { position:absolute; top:0; bottom:0; background:rgba(255,210,87,.13);
             border-left:2px solid var(--sel); border-right:2px solid var(--sel); }
  .selband .grip { position:absolute; top:0; bottom:0; width:9px; cursor:ew-resize;
                   pointer-events:auto; background:rgba(255,210,87,.35); }
  .selband .grip.l { left:-5px; } .selband .grip.r { right:-5px; }
  .vgrip { position:absolute; top:0; right:0; width:7px; height:100%; cursor:ew-resize;
           background:rgba(255,255,255,.35); opacity:0; }
  .sec:hover .vgrip { opacity:1; }
  .vtail { position:absolute; top:5px; height:24px; border-radius:0 3px 3px 0; pointer-events:none;
           background:repeating-linear-gradient(45deg, rgba(122,59,110,.5) 0 5px, rgba(60,30,55,.5) 5px 10px);
           border:1px dashed rgba(255,255,255,.35); }
  .selband b { position:absolute; top:2px; left:50%; transform:translateX(-50%); font-size:10px;
               color:#141519; background:var(--sel); padding:0 5px; border-radius:2px; white-space:nowrap; }
  #playhead { position:absolute; top:0; bottom:0; width:1px; background:var(--play); z-index:7;
              pointer-events:none; }
  #playhead::before { content:''; position:absolute; top:0; left:-6px; border:6px solid transparent;
                      border-top-color:var(--play); }
  #details { padding:8px 20px; background:var(--panel); border-top:1px solid #000; max-height:150px;
             overflow:auto; font-size:11px; }
  #details h3 { font-size:12px; color:var(--accent); margin-bottom:4px; }
  #details pre { color:var(--dim); white-space:pre-wrap; }
  .legend { display:flex; gap:12px; margin-left:auto; font-size:11px; color:var(--dim); }
  .swatch { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:4px; }
  #stagewrap { display:flex; gap:14px; padding:10px 20px 12px; background:#101116;
               border-bottom:1px solid #000; align-items:flex-start; }
  #stagewrap.hidden { display:none; }
  .stagebox { position:relative; }
  .stagebox h4 { font-size:10px; color:var(--dim); font-weight:600; letter-spacing:.6px;
                 text-transform:uppercase; margin-bottom:4px; }
  canvas { background:#0a0b0f; border:1px solid #2c2f3b; border-radius:4px; display:block; }
  #stageInfo { font-size:11px; color:var(--dim); flex:1; align-self:stretch;
               display:flex; flex-direction:column; gap:3px; padding-top:16px; }
  #stageInfo .on { color:var(--text); }
  #stageInfo .dimmed { color:#575c70; }
  #stageInfo b { color:var(--accent); }
</style>
</head>
<body>
<header>
  __NAV__
  <h1>__TITLE__</h1>
  <span class="meta" id="metaLine"></span>
  <span class="legend">
    <span><span class="swatch" style="background:var(--cut)"></span>Camera cut</span>
    <span><span class="swatch" style="background:var(--vo)"></span>Voice</span>
    <span><span class="swatch" style="background:var(--subt)"></span>Subtitle</span>
    <span><span class="swatch" style="background:#2f7a6a"></span>VFX</span>
    <span><span class="swatch" style="background:#8a5a2b"></span>Phoneme</span>
    <span><span class="swatch" style="background:var(--evt)"></span>Event</span>
    <span><span class="swatch" style="background:repeating-linear-gradient(45deg,var(--del) 0 4px,#582525 4px 8px)"></span>Deleted</span>
  </span>
</header>
<div id="subwin">
  <div id="subActor">&nbsp;</div>
  <div id="subText"><span class="idle">— subtitle window · press Space to play, drag the ruler to scrub —</span></div>
  <div id="infoline"></div>
</div>
<div id="stagewrap">
  <div class="stagebox"><h4>Camera view (rough)</h4><canvas id="camview" width="426" height="240"></canvas></div>
  <div class="stagebox"><h4>Top-down</h4><canvas id="mapview" width="240" height="240"></canvas></div>
  <div class="stagebox" id="lipbox"><h4>Lip sync</h4><canvas id="mouthview" width="150" height="120"></canvas></div>
  <div id="stageInfo"></div>
</div>
<div id="toolbar">
  <button id="playBtn" title="Space">⏵ Play</button>
  <button id="stageBtn" title="Toggle stage">👤 Stage</button>
  <button data-z="0.5">−</button><button data-z="2">+</button>
  <button id="fitBtn">Fit</button>
  <button id="stackBtn" title="Stack overlapping cues into sub-lanes so buried ones stay clickable (V)">⇕ Unstack overlaps</button>
  <span class="sep"></span>
  <button id="muteBtn" title="Mute (M)">🔊</button>
  <input id="vol" type="range" min="0" max="100" value="90" style="width:70px;vertical-align:middle">
  <span class="hint" id="audioState"></span>
  <span class="sep"></span>
  <button id="undoBtn" title="Ctrl+Z">↶ Undo</button>
  <button id="redoBtn" title="Ctrl+Shift+Z">↷ Redo</button>
  <button id="resetBtn">Reset edits</button>
  <button id="safeBtn" title="Shrink selection to a clean cut (S)">🛡 Make safe</button>
  <button id="cutBtn" title="Delete selection (DEL)">✂ Cut selection</button>
  <button id="keepBtn" title="Pick a show/hide cue, then keep that actor visible for the whole scene (K)">👁 Keep actor visible</button>
  <button id="hideBtn" title="Pick a show/hide cue, then keep that actor hidden for the whole scene (Shift+K)">🚫 Keep actor hidden</button>
  <button id="musicBtn" title="Pick a music cue, then ship your replacement for that track (M)">🎵 Replace this music</button>
  <button id="loadBtn" title="Load an edit plan (Ctrl+O)">📂 Load plan</button>
  <button id="saveBtn" title="Ctrl+S">💾 Export edit plan</button>
  <input id="planFile" type="file" accept=".json" style="display:none">
  <button id="installBtn" title="Patch, pack and install to the game (Ctrl+B)">🎮 Build &amp; install</button>
  <span class="sep"></span>
  <span id="editInfo"></span>
  <span class="hint" style="margin-left:auto">drag across tracks to select · DEL cuts · I/O marks · [ picks shot · S makes it safe · drag a voice bar's right edge to shorten it · click any cue + DEL removes it · dbl-click/R restores · overlapping cues stack into sub-lanes (V toggles)</span>
</div>
<div id="warnbar"><span id="warnLine"></span><span id="buildLine"></span></div>
<div id="buildlog"><button id="logClose">close</button><pre id="buildLogText"></pre></div>
<div id="timeline">
  <div id="scrub"></div>
  <div id="rows"></div>
  <div id="overlay"></div>
  <div id="playhead"></div>
</div>
<div id="details"><h3>Details</h3><pre id="detailBody">Click any block…</pre>
<h3 style="margin-top:14px">Actors</h3>
<div class="dimmed" style="margin:0 0 6px">Every actor the scene shows or hides. Set one to <b>Show</b> or <b>Hide</b> to pin it for the whole scene — no need to find its cues, which may sit inside a cut.</div>
<div id="actorList"></div></div>
<script>
const DATA = __DATA__;
const seqs = DATA.sequences;
const root = seqs.Root;
const TICK = (root.meta.tickResolution && root.meta.tickResolution.Numerator) || 24000;
const FPS  = (root.meta.displayRate && root.meta.displayRate.Numerator) || 30;
const TPF  = TICK / FPS;
const PB   = root.meta.playbackRange || [0, 0];
const TOTAL = PB[1] - PB[0];
const EV = DATA.events || {};

const cuts = (seqs.Camera ? seqs.Camera.sections : [])
  .filter(s => s.type === 'MovieSceneCameraCutSection')
  .sort((a,b) => a.range[0]-b.range[0])
  .map((s,i) => ({...s, name:'C'+String(i+1).padStart(2,'0'), id:i}));
const voice = (EV.Voice || []).filter(e => e.tick !== null);
const subs  = (EV.SubtitleRanges || []).slice().sort((a,b)=>a.start-b.start);

let pxPerTick = 1100 / TOTAL;
let playhead = 0, playing = false, lastTs = null;

// ---- overlap stacking -----------------------------------------------------
// Cues on the same track can share (or fully contain) each other's time range:
// two SE cues on the same frame, a voice line that runs under another, a short
// cue swallowed by a long one. Drawn flat they hide each other and the buried
// one is simply unclickable. So each track packs its cues into sub-lanes — the
// classic greedy interval packing — and the row grows to fit however many
// lanes it needs. Packing is done in *pixels*, not ticks, so bars that are
// only visually touching separate again as you zoom in, and a track with no
// overlaps stays exactly one lane tall like before.
const BAR_GAP = 3, ROW_PAD = 5, MAX_LANES = 12;
let stackOverlaps = true;
const collapsedRows = {};               // row label -> true when manually flattened

// Two bars need separate lanes when they overlap in *time*, or when they don't
// but are drawn so close that one visually swallows the other (short cues get a
// 3px floor, so at low zoom two cues a tick apart land on the same pixels).
// Cuts and shots that merely touch end-to-start stay on one lane.
function barsClash(a, b) {
  if (b.t0 < a.t1 && a.t0 < b.t1) return true;             // real time overlap
  const cover = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0);
  return cover >= 0.55 * Math.min(a.x1 - a.x0, b.x1 - b.x0);
}

function packRow(secs, label) {
  const laneOf = new Map();
  const last = [];                      // last bar placed in each sub-lane
  const stack = stackOverlaps && !collapsedRows[label];
  const items = secs.filter(s => s.range)
                    .map((s, i) => ({s, i}))
                    .sort((a, b) => (a.s.range[0] - b.s.range[0]) || (a.i - b.i));
  for (const {s} of items) {
    const x0 = s.range[0] * pxPerTick;
    const bar = {t0:s.range[0], t1:s.range[1], x0,
                 x1: x0 + Math.max(3, (s.range[1] - s.range[0]) * pxPerTick - 1)};
    let k = 0;
    if (stack) {
      while (k < last.length && barsClash(last[k], bar)) k++;
      if (k >= MAX_LANES) k = MAX_LANES - 1;   // stop growing; pile up in the last lane
    }
    last[k] = bar;
    laneOf.set(s, k);
  }
  const lanes = Math.max(1, last.length);
  // keep tall stacks from eating the screen: slimmer bars once we're deep
  const barH = lanes <= 1 ? 24 : lanes <= 4 ? 20 : 15;
  const height = Math.max(34, ROW_PAD * 2 + lanes * barH + (lanes - 1) * BAR_GAP);
  return {laneOf, lanes, barH, height, collapsed: !stack,
          topOf: s => ROW_PAD + (laneOf.get(s) || 0) * (barH + BAR_GAP)};
}
const undoStack = [], redoStack = [];

const $ = id => document.getElementById(id);
const rowsEl = $('rows'), scrubEl = $('scrub'), tlEl = $('timeline'), phEl = $('playhead');

document.getElementById('metaLine').textContent =
  `${TICK} ticks/s · ${FPS} fps · ${(TOTAL/TICK).toFixed(2)}s · ${Math.round(TOTAL/TPF)} frames · ${cuts.length} cuts · ${voice.length} voice lines`;

function fmt(t) {
  const s = Math.max(0, t) / TICK, m = Math.floor(s/60);
  return `${m}:${(s - m*60).toFixed(2).padStart(5,'0')}`;
}
const frameOf = t => Math.round(t / TPF);

function laneRows() {
  const rows = [];
  rows.push({label:`Camera cuts (${cuts.length})`, cls:'cutsec', cutRow:true, rangeRow:true, secs:cuts});
  if (voice.length) rows.push({label:`Voice (${voice.length})`, cls:'vosec', voiceRow:true,
    secs: voice.map(e => ({type:'Voice', props:e.props, actor:e.actor, text:e.text,
      seq:'Voice', voiceName:e.props.VoiceName, tickStart:e.tick,
      full:fullDur(e), kept:keptDur(e),
      range:[e.tick, e.tick + keptDur(e)*TICK],
      name:(e.actor ? e.actor+': ' : '') + (e.text || e.props.VoiceName)}))});
  if (subs.length) rows.push({label:`Subtitles (${subs.length})`, cls:'subtsec',
    secs: subs.map(r => ({type:'Subtitle', props:r, range:[r.start, trimmedSubEnd(r)],
      name:(r.actor ? r.actor+': ' : '') + (r.text || r.label)}))});
  // lip sync — one block per phoneme keyframe
  if (LIP.length) {
    const secs = [];
    for (const ln of LIP)
      for (const f of ln.frames)
        secs.push({type:'Phoneme', props:{phoneme:f[2], shapes:f[3], line:ln.voice, actor:ln.actor},
                   range:[f[0], f[1]], name:f[2]});
    rows.push({label:`Lip sync (${secs.length})`, cls:'lipsec', secs});
  }
  // VFX activation windows (Niagara particle systems)
  const VFX = DATA.vfx || [];
  if (VFX.length) {
    rows.push({label:`VFX (${VFX.length})`, cls:'fxsec',
      secs: VFX.map(x => ({type:'VFX', props:x,
        range:[x.start, x.end != null ? x.end : TOTAL],
        name:x.name}))});
  }
  function cueName(e) {
    const p = e.props || {};
    if (p.SeName) return p.SeName;
    if (p.MusicName) return p.MusicName;
    if (p.VoiceName) return p.VoiceName;
    if (p.From !== undefined) return `fade ${p.From}→${p.To}${p.White ? ' (white)' : ''}`;
    if (p.ActorName) return (e.clip === 'ActorDraw')
      ? `${p.ActorName} ${p.Hidden ? 'hide' : 'show'}` : p.ActorName;
    if (p.TriggerID) return [].concat(p.TriggerID).join(', ');
    if (p.ActorNames) return [].concat(p.ActorNames).slice(0,2).join(', ');
    if (p.VolumeLabel) return `${p.VolumeLabel} → ${p.SwitchLabel || ''}`;
    if (p.TargetName) return p.TargetName;
    return e.clip || '';
  }
  // group every remaining cue by its Clip_* type so each gets its own labelled row
  const groups = new Map();
  for (const [key, label] of [['Sound','SE'], ['ManualSE','SE'], ['CutEvent','Event'],
                              ['PlannerEvent','Planner'], ['Constraint','Constraint'],
                              ['Light','Lighting'], ['Character','Character']]) {
    for (const e of (Array.isArray(EV[key]) ? EV[key] : [])) {
      if (e.tick === null || e.tick === undefined) continue;
      const g = e.clip || label;
      if (!groups.has(g)) groups.set(g, []);
      groups.get(g).push({...e, __seq: key});
    }
  }
  const CLIP_ROW = {Se:'SE', BGM:'Music cues', VibrationSe:'Rumble', Fade:'Fades',
                    ActorDraw:'Actor show/hide', SendStateTrigger:'State triggers',
                    DirLightModify:'Lighting (dir)', EnvLightModify:'Lighting (env)',
                    SwitchStreamingVolume:'Streaming', Constraint:'Constraints',
                    Bind:'Bindings', SubTitle:'Subtitle cues', Voice:'Voice cues'};
  const order = ['Fade','ActorDraw','Se','VibrationSe','BGM','DirLightModify','EnvLightModify',
                 'SwitchStreamingVolume','SendStateTrigger','Constraint','Bind'];
  const keys = [...groups.keys()].sort((a,b) => {
    const ia = order.indexOf(a), ib = order.indexOf(b);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || a.localeCompare(b);
  });
  for (const g of keys) {
    if (g === 'Voice' || g === 'SubTitle') continue;   // already have dedicated rows
    const list = groups.get(g);
    rows.push({label:`${CLIP_ROW[g] || g} (${list.length})`, cls:'evtsec',
      secs:list.map(e => ({type:g, clip:e.clip, props:e.props, seq:e.__seq,
        tickStart:e.tick, range:[e.tick, e.tick+TICK*0.25], name:cueName(e)}))});
  }
  const shots = root.sections.filter(s => s.type==='MovieSceneCinematicShotSection' || s.type==='MovieSceneSubSection');
  rows.push({label:`Shots (root)`, cls:'shotsec', rangeRow:true,
    secs:shots.map(s => ({...s, name:s.name || s.type}))});
  return rows;
}

function render() {
  renderActors();
  const width = Math.max(1200, TOTAL*pxPerTick + 180);
  rowsEl.innerHTML = ''; scrubEl.innerHTML = '';
  scrubEl.style.width = width+'px';
  const step = TOTAL*pxPerTick > 4200 ? TICK : TICK*5;
  for (let t = 0; t <= TOTAL; t += step) {
    const d = document.createElement('div');
    d.className = 'rt';
    d.style.left = (150 + t*pxPerTick) + 'px';
    d.textContent = fmt(t) + ' · f' + frameOf(t);
    scrubEl.appendChild(d);
  }
  for (const row of laneRows()) {
    const pack = packRow(row.secs, row.label);
    const tr = document.createElement('div');
    tr.className = 'trackrow'; tr.style.width = width+'px';
    tr.style.height = pack.height + 'px';
    const lb = document.createElement('div');
    lb.className = 'tracklabel'; lb.textContent = row.label;
    if (pack.lanes > 1 || collapsedRows[row.label]) {
      const c = document.createElement('span');
      c.className = 'stackcount';
      c.textContent = collapsedRows[row.label] ? ' ⇕flat' : ` ⇕${pack.lanes}`;
      c.title = collapsedRows[row.label]
        ? 'This track is flattened — click to stack its overlapping cues again'
        : `${pack.lanes} cues overlap here — stacked so each stays clickable. Click to flatten this track.`;
      c.onclick = ev => {
        ev.stopPropagation();
        if (collapsedRows[row.label]) delete collapsedRows[row.label];
        else collapsedRows[row.label] = true;
        render();
      };
      lb.appendChild(c);
    }
    tr.appendChild(lb);
    const lane = document.createElement('div'); lane.className = 'lane';
    for (const s of row.secs) {
      if (!s.range) continue;
      const el = document.createElement('div');
      el.className = 'sec ' + row.cls + (pack.lanes > 1 ? ' stacked' : '');
      el.style.left = (s.range[0]*pxPerTick) + 'px';
      el.style.width = Math.max(3, (s.range[1]-s.range[0])*pxPerTick - 1) + 'px';
      el.style.top = pack.topOf(s) + 'px';
      el.style.height = pack.barH + 'px';
      el.style.lineHeight = pack.barH + 'px';
      el.textContent = s.name || '';
      el.title = `${s.name || s.type}  [${s.range[0]}, ${s.range[1]})  ${fmt(s.range[0])}–${fmt(s.range[1])}`;
      el.onclick = ev => {
        ev.stopPropagation();
        showDetails(s);
        pickedCue = s;
        if (row.rangeRow) { sel = {a:s.range[0], b:s.range[1]}; }
        else { sel = null; }
        render();
      };
      { const d = cueDescriptor(s); const k = cueKey(d);
        if (k && killed[k]) el.classList.add('deleted');
        { const an = actorOf(s); if (an && forced[an]) el.classList.add('pinned');
          if (an && hiddenA[an]) el.classList.add('pinnedoff');
          const mn = (s.props||{}).MusicName; if (mn && music[mn]) el.classList.add('pinned'); }
        if (pickedCue === s) el.classList.add('selected'); }
      if (row.voiceRow) {
        if (s.kept < s.full - 0.01) {          // ghost of the silenced tail
          const t = document.createElement('div');
          t.className = 'vtail';
          t.style.left = (s.tickStart + s.kept*TICK)*pxPerTick + 'px';
          t.style.width = Math.max(2, (s.full - s.kept)*TICK*pxPerTick) + 'px';
          t.style.top = pack.topOf(s) + 'px';
          t.style.height = pack.barH + 'px';
          lane.appendChild(t);
        }
        const g = document.createElement('div');
        g.className = 'vgrip';
        g.title = 'drag to shorten this line';
        g.onmousedown = ev => {
          ev.stopPropagation(); ev.preventDefault();
          pushUndo(); dragMode = 'trim-voice'; trimTarget = s;
        };
        el.appendChild(g);
      }
      lane.appendChild(el);
    }
    tr.appendChild(lane);
    rowsEl.appendChild(tr);
  }
  positionPlayhead();
  updateEditInfo();
}

function positionPlayhead() {
  phEl.style.left = (150 + playhead*pxPerTick) + 'px';
}

function showDetails(s) {
  $('detailBody').textContent = JSON.stringify(s, null, 1);
}

// ---- editing: arbitrary ranges, ripple delete ----
// `edits` = sorted, non-overlapping [start,end) ranges removed from the timeline.
let edits = [];
let sel = null;                       // {a,b} current selection in original ticks
let trims = {};                       // VoiceName -> seconds of audio to keep
let killed = {};                      // cueKey -> descriptor of a deleted cue
let forced = {};                      // actor name -> keep it visible throughout
let hiddenA = {};                     // actor name -> keep it hidden throughout
let music = {};                       // MusicName -> ship a replaced BGM asset
// Nothing music-related happens unless a track is named here. BGM assets are
// shared between scenes, so shipping one you did not choose silently overrides
// whatever else supplies it.
// The game deliberately flickers some actors on and off — a bloodied double
// swapped in and out, say. Naming one here pins every Hidden flag it owns to
// false, so it stays on screen for the whole scene. Purely a creative choice.
let pickedCue = null;                 // the block currently clicked

function normalise(list) {
  const r = list.filter(x => x.b > x.a).map(x => ({a:x.a, b:x.b}))
                .sort((p,q) => p.a - q.a);
  const out = [];
  for (const x of r) {
    const last = out[out.length-1];
    if (last && x.a <= last.b) last.b = Math.max(last.b, x.b);
    else out.push(x);
  }
  return out;
}
const snapshot = () => JSON.stringify({e: edits, t: trims, k: killed, f: forced, h: hiddenA, m: music});
function restore(js) { const o = JSON.parse(js); edits = o.e || []; trims = o.t || {}; killed = o.k || {}; forced = o.f || {}; hiddenA = o.h || {}; music = o.m || {}; }
function pushUndo() {
  undoStack.push(snapshot());
  if (undoStack.length > 200) undoStack.shift();
  redoStack.length = 0;
}
function undo() {
  if (!undoStack.length) return;
  redoStack.push(snapshot());
  restore(undoStack.pop());
  render();
}
function redo() {
  if (!redoStack.length) return;
  undoStack.push(snapshot());
  restore(redoStack.pop());
  render();
}
function resetEdits() {
  if (edits.length || Object.keys(trims).length || Object.keys(killed).length
      || Object.keys(forced).length || Object.keys(hiddenA).length || Object.keys(music).length) pushUndo();
  edits = []; trims = {}; killed = {}; forced = {}; hiddenA = {}; music = {}; sel = null; pickedCue = null; render();
}

// ---- deleting one cue on any track --------------------------------------
// Identify a cue by which subsequence it lives in, its tick, and the name the
// game looks up. Deleting = breaking that name so the lookup misses.
const CUE_FIELDS = ['VoiceName','SeName','MusicName','TextLabel','ActorName'];
function cueDescriptor(s) {
  if (s.type === 'VFX') {
    return {kind:'vfx', name:s.props.name, raw:s.props.raw,
            start:s.props.start, end:s.props.end,
            label:'VFX ' + (s.props.name || '')};
  }
  const p = s.props || {};
  if (s.type === 'Subtitle') {
    return {seq:'Text', tick:p.start, field:'TextLabel', value:p.label,
            label:'subtitle ' + (p.actor || p.label || '')};
  }
  const seq = s.seq;
  if (!seq) return null;
  for (const f of CUE_FIELDS) {
    if (p[f]) return {seq, tick:s.tickStart ?? s.range[0], field:f, value:p[f],
                      clip:s.clip || s.type,
                      label:(s.clip || seq) + ' ' + p[f]};
  }
  return null;
}
const cueKey = d => d ? (d.kind === 'vfx'
    ? 'vfx|' + d.raw + '|' + d.start
    : d.seq + '|' + d.tick + '|' + d.field + '|' + d.value) : null;
function deleteCue() {
  if (!pickedCue) return false;
  const d = cueDescriptor(pickedCue);
  const k = cueKey(d);
  if (!k) {
    // nothing to rename (fades, lighting, shots...) — offer the time-range cut instead
    const r = pickedCue.range;
    const what = pickedCue.clip || pickedCue.type || 'that block';
    if (r && r[1] > r[0]) {
      sel = {a:r[0], b:r[1]};
      renderOverlay(); updateEditInfo();
      setBuild('busy', what + ' can\'t be switched off individually — selected its time range, press DEL again to cut it');
    } else {
      setBuild('bad', what + ' has no name the game looks up, so it can\'t be removed on its own');
    }
    return true;
  }
  if (d.clip === 'SendStateTrigger' || d.clip === 'Jump' || d.clip === 'StoryJump') {
    setBuild('bad', 'refusing to delete a ' + d.clip + ' — the game needs it to progress');
    return true;
  }
  pushUndo();
  if (killed[k]) delete killed[k]; else killed[k] = d;
  render();
  return true;
}
// Every actor the scene shows or hides, gathered from the show/hide payloads.
function sceneActors() {
  const out = new Set();
  for (const g of Object.values(DATA.events || {}))
    for (const e of (g || [])) {
      const p = e.props || {};
      if ('Hidden' in p && p.ActorName && p.ActorName !== 'None') out.add(p.ActorName);
    }
  return [...out].sort();
}
function setActorState(a, how) {
  pushUndo();
  delete forced[a]; delete hiddenA[a];
  if (how === 'show') forced[a] = true;
  else if (how === 'hide') hiddenA[a] = true;
  render();
}
function renderActors() {
  const box = $('actorList');
  if (!box) return;
  box.innerHTML = '';
  for (const a of sceneActors()) {
    const row = document.createElement('div'); row.className = 'arow';
    const nm = document.createElement('span'); nm.className = 'an';
    nm.textContent = a; nm.title = a; row.appendChild(nm);
    for (const [how, label] of [['normal','Normal'],['show','Show'],['hide','Hide']]) {
      const b = document.createElement('button');
      b.textContent = label;
      const cur = forced[a] ? 'show' : (hiddenA[a] ? 'hide' : 'normal');
      if (cur === how) b.className = how === 'hide' ? 'off' : 'on';
      b.onclick = () => setActorState(a, how);
      row.appendChild(b);
    }
    box.appendChild(row);
  }
}
function toggleMusic() {
  const m = ((pickedCue && pickedCue.props) || {}).MusicName;
  if (!m) { setBuild('bad', 'Pick a music cue first, then press M.'); return false; }
  pushUndo();
  if (music[m]) { delete music[m]; setBuild('', m + ' left as the game has it'); }
  else { music[m] = true;
         setBuild('', m + ' will be rebuilt from its _Project folder and shipped — '
                      + 'replace the matching .wav in there first'); }
  render();
  return true;
}
function actorOf(s) {
  const p = (s && s.props) || {};
  return (p.ActorName && p.ActorName !== 'None') ? p.ActorName : null;
}
function toggleForceVisible(hide) {
  const a = actorOf(pickedCue);
  if (!a) {
    setBuild('bad', 'Pick one of that actor\'s show/hide cues first, then press K.');
    return false;
  }
  // A swap is two actors, not one: a clean model and a bloodied one taking
  // turns. Pinning one visible only does half the job — the other has to be
  // pinned hidden or it keeps coming back over the top.
  const mine = hide ? hiddenA : forced, other = hide ? forced : hiddenA;
  pushUndo();
  delete other[a];
  if (mine[a]) { delete mine[a]; setBuild('', a + ' back to its normal show/hide'); }
  else { mine[a] = true;
         setBuild('', a + (hide ? ' will stay hidden' : ' will stay visible') + ' for the whole scene'); }
  render();
  return true;
}
const fullDur = v => Math.max(0.35, v.duration || 1);
const keptDur = v => Math.min(trims[v.props.VoiceName] ?? fullDur(v), fullDur(v));
function trimmedTail(t) {          // is this tick inside a silenced tail?
  for (const v of voice) {
    const k = trims[v.props.VoiceName];
    if (k === undefined) continue;
    if (t >= v.tick + k*TICK && t < v.tick + fullDur(v)*TICK) return true;
  }
  return false;
}

const removedTicks = () => edits.reduce((a,x) => a + (x.b - x.a), 0);
const editedTicks  = () => TOTAL - removedTicks();
function inEdit(t) { for (const x of edits) if (t >= x.a && t < x.b) return x; return null; }
function keepRanges() {
  const out = []; let c = 0;
  for (const x of edits) { if (x.a > c) out.push([c, x.a]); c = Math.max(c, x.b); }
  if (c < TOTAL) out.push([c, TOTAL]);
  return out;
}
// original tick -> position on the edited timeline
function toEdited(t) {
  let d = 0;
  for (const x of edits) { if (x.b <= t) d += x.b - x.a; else if (x.a < t) return null; }
  return t - d;
}

// what a proposed cut would remove — used for the warning line
//
// Voice is fired by Clip_Voice, an *instantaneous* event with no duration and no
// stop cue, so the clip always plays to its natural end. Cutting into a line does
// not shorten it — the audio simply runs on over whatever follows.
function impactOf(a, b) {
  const hit = {lines:[], triggers:[], jumps:[], cuts:0, midLine:null,
               overrun:0, stranded:[], lipSplit:0};
  for (const v of voice) {
    const s = v.tick, e = v.tick + (v.duration || 1) * TICK;
    if (e > a && s < b) {
      hit.lines.push(v.actor || v.props.VoiceName);
      if (s < a) {                       // line starts before the cut and runs into it
        hit.midLine = v.actor || v.props.VoiceName;
        hit.overrun = Math.max(hit.overrun, Math.min(e, b) - a);
      } else if (e > b) {                // cut starts mid-line
        hit.midLine = v.actor || v.props.VoiceName;
      }
    }
  }
  // subtitle left on screen: its "off" event is inside the cut but "on" is before it
  for (const r of subs) {
    if (r.end > a && r.end <= b && r.start < a) hit.stranded.push(r.actor || r.label);
  }
  for (const ln of LIP) {
    const s = ln.frames[0][0], e = ln.frames[ln.frames.length-1][1];
    if (e > a && s < b && (s < a || e > b)) hit.lipSplit++;
  }
  for (const key of ['PlannerEvent','CutEvent']) {
    for (const e of (Array.isArray(EV[key]) ? EV[key] : [])) {
      if (e.tick == null || e.tick < a || e.tick >= b) continue;
      if (e.clip === 'SendStateTrigger') hit.triggers.push([].concat(e.props.TriggerID || []).join(','));
      if (e.clip === 'Jump' || e.clip === 'StoryJump') hit.jumps.push(e.clip);
    }
  }
  hit.cuts = cuts.filter(c => c.range[0] >= a && c.range[1] <= b).length;
  return hit;
}

// pull the selection edges inward until it splits no voice line and strands no subtitle
function makeSafe() {
  if (!sel) return;
  // snap to the frame grid first (inward); doing it afterwards could clip a line
  // that the shrink pass had already cleared
  let a = Math.ceil(sel.a / TPF) * TPF, b = Math.floor(sel.b / TPF) * TPF;
  for (let pass = 0; pass < 8; pass++) {
    let moved = false;
    for (const v of voice) {
      const s = v.tick, e = v.tick + (v.duration || 1) * TICK;
      if (e > a && s < b) {
        if (s < a && e > a && e <= b) { a = e; moved = true; }        // trailing audio
        else if (s >= a && s < b && e > b) { b = s; moved = true; }   // leading audio
        else if (s < a && e > b) { a = b = 0; moved = true; }         // cut sits inside a line
      }
    }
    for (const r of subs) {
      if (r.end > a && r.end <= b && r.start < a) { a = r.end; moved = true; }
    }
    if (!moved) break;
  }
  sel = (b > a) ? {a, b} : null;
  renderOverlay(); updateEditInfo();
}

function deleteSelection() {
  if (!sel || sel.b <= sel.a) return;
  pushUndo();
  edits = normalise(edits.concat([{a:sel.a, b:sel.b}]));
  sel = null;
  render();
}
function restoreAt(t) {
  const x = inEdit(t);
  if (!x) return false;
  pushUndo();
  edits = edits.filter(e => e !== x);
  render();
  return true;
}

function updateEditInfo() {
  const n = edits.length, rem = removedTicks(), nt = Object.keys(trims).length;
  const bits = [];
  if (n) bits.push(`${n} cut${n>1?'s':''} · −${(rem/TICK).toFixed(2)}s → ${(editedTicks()/TICK).toFixed(2)}s (was ${(TOTAL/TICK).toFixed(2)}s)`);
  if (nt) bits.push(`${nt} line${nt>1?'s':''} shortened`);
  const nk = Object.keys(killed).length;
  if (nk) bits.push(`${nk} cue${nk>1?'s':''} deleted`);
  $('editInfo').textContent = bits.join(' · ');
  $('undoBtn').disabled = !undoStack.length;
  $('redoBtn').disabled = !redoStack.length;
  const w = $('warnLine');
  if (sel) {
    const h = impactOf(sel.a, sel.b);
    const bits = [`selection ${fmt(sel.a)}–${fmt(sel.b)} (${((sel.b-sel.a)/TICK).toFixed(2)}s, ${Math.round((sel.b-sel.a)/TPF)}f)`];
    if (h.cuts) bits.push(`${h.cuts} whole shot${h.cuts>1?'s':''}`);
    if (h.lines.length) bits.push(`${h.lines.length} voice line${h.lines.length>1?'s':''}`);
    if (h.midLine) bits.push(`<span class="warn">⚠ splits ${h.midLine}'s line — audio plays on${h.overrun ? ' ~' + (h.overrun/TICK).toFixed(1) + 's' : ''}</span>`);
    if (h.stranded.length) bits.push(`<span class="warn">⚠ subtitle stays on screen (${h.stranded[0]})</span>`);
    if (h.lipSplit) bits.push(`<span class="warn">⚠ ${h.lipSplit} lipsync line(s) desync</span>`);
    if (h.triggers.length) bits.push(`<span class="warn">⚠ ${h.triggers.length} state trigger(s)</span>`);
    if (h.jumps.length) bits.push(`<span class="warn">⚠ ${h.jumps.length} jump(s)</span>`);
    w.innerHTML = bits.join(' · ');
  } else w.innerHTML = '';
}

function exportPlan() {
  const blob = new Blob([JSON.stringify(planObject(), null, 1)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = DATA.cutscene + '_editplan.json';
  a.click();
  URL.revokeObjectURL(a.href);
}

// ---- audio ----
const AUDIO_INFO = DATA.audio || null;
let audioEl = null, audioReady = false;
if (AUDIO_INFO) {
  audioEl = new Audio(AUDIO_INFO.file);
  audioEl.preload = 'auto';
  audioEl.volume = 0.9;
  audioEl.addEventListener('canplaythrough', () => {
    audioReady = true;
    $('audioState').textContent = `VO ${AUDIO_INFO.placed} lines`;
  });
  audioEl.addEventListener('error', () => {
    $('audioState').textContent = 'audio failed to load';
  });
  $('audioState').textContent = 'loading VO…';
} else {
  $('audioState').textContent = 'no VO track';
  $('muteBtn').disabled = true; $('vol').disabled = true;
}
const audioTime = () => playhead / TICK;

// preview trims by ducking the shared VO track during silenced tails
let actx = null, gainNode = null;
function ensureGraph() {
  if (actx || !audioEl) return;
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    actx = new AC();
    const src = actx.createMediaElementSource(audioEl);
    gainNode = actx.createGain();
    src.connect(gainNode); gainNode.connect(actx.destination);
  } catch (e) { actx = null; }
}
function applyTrimGain() {
  if (!gainNode) return;
  const want = trimmedTail(playhead) ? 0 : 1;
  if (Math.abs(gainNode.gain.value - want) > 0.01) gainNode.gain.value = want;
}

// ---- playback / scrubbing ----
// Seeking an <audio> element is asynchronous: for a frame or two afterwards it
// still reports the OLD currentTime. Using it as the clock in that window sends
// the playhead back where it came from — at a cut that means seeking past the
// gap, being told we are still inside it, and seeking again forever, which
// stalls playback on the first cut. It also made Play jump to the audio's
// position instead of the one you scrubbed to. So ignore the audio clock until
// the seek has actually landed, and run off the wall clock in the meantime.
let seekUntil = 0;
function seekAudio(t) {
  if (!audioEl) return;
  try { audioEl.currentTime = t / TICK; } catch (e) {}
  seekUntil = performance.now() + 150;
}
function audioIsClock() {
  if (!audioEl || audioEl.paused || audioEl.seeking) return false;
  if (performance.now() < seekUntil) return false;
  // and only while it actually agrees with us — a failed seek must not drag
  // the playhead somewhere else
  return Math.abs(audioEl.currentTime * TICK - playhead) < TICK * 0.5;
}

function setPlayhead(t, fromPlay) {
  playhead = Math.min(Math.max(t, 0), TOTAL);
  if (audioEl && !fromPlay) {
    // via seekAudio so a scrub made while playing isn't immediately undone by
    // the audio element still reporting its pre-seek position
    seekAudio(playhead);
  }
  if (!fromPlay) { // keep playhead visible when scrubbing manually
    const x = 150 + playhead*pxPerTick;
    if (x < tlEl.scrollLeft + 160 || x > tlEl.scrollLeft + tlEl.clientWidth - 40)
      tlEl.scrollLeft = x - tlEl.clientWidth/2;
  }
  renderOverlay();
  positionPlayhead();
  updateSubtitleWindow();
  drawStage();
}

function renderOverlay() {
  const ov = $('overlay');
  ov.innerHTML = '';
  ov.style.height = rowsEl.offsetHeight + 'px';
  ov.style.top = scrubEl.offsetHeight + 'px';
  const X = t => 150 + t * pxPerTick;
  for (const x of edits) {
    const d = document.createElement('div');
    d.className = 'delband';
    d.style.left = X(x.a) + 'px';
    d.style.width = Math.max(2, (x.b - x.a) * pxPerTick) + 'px';
    d.innerHTML = `<span>−${((x.b-x.a)/TICK).toFixed(2)}s</span>`;
    ov.appendChild(d);
  }
  if (sel && sel.b > sel.a) {
    const d = document.createElement('div');
    d.className = 'selband';
    d.style.left = X(sel.a) + 'px';
    d.style.width = Math.max(2, (sel.b - sel.a) * pxPerTick) + 'px';
    d.innerHTML = `<b>${((sel.b-sel.a)/TICK).toFixed(2)}s · ${Math.round((sel.b-sel.a)/TPF)}f</b>`;
    for (const side of ['l','r']) {
      const g = document.createElement('div');
      g.className = 'grip ' + side;
      g.onmousedown = ev => { ev.stopPropagation(); ev.preventDefault(); dragMode = 'trim-' + side; };
      d.appendChild(g);
    }
    ov.appendChild(d);
  }
}

// snap to meaningful boundaries: shot edges, voice starts/ends, then the frame grid
function snapTick(t, enable) {
  t = Math.min(Math.max(t, 0), TOTAL);
  if (!enable) return Math.round(t / TPF) * TPF;
  const tol = 8 / pxPerTick;              // 8px of slack
  let best = null, bd = tol;
  const consider = v => { const d = Math.abs(v - t); if (d < bd) { bd = d; best = v; } };
  for (const c of cuts) { consider(c.range[0]); consider(c.range[1]); }
  for (const v of voice) { consider(v.tick); consider(v.tick + (v.duration||1)*TICK); }
  for (const x of edits) { consider(x.a); consider(x.b); }
  if (best !== null) return best;
  return Math.round(t / TPF) * TPF;
}

function activeIn(list, t, s='start', e='end') {
  return list.filter(r => r[s] <= t && t < r[e]);
}

function trimmedSubEnd(r) {
  // a shortened line pulls its subtitle in to match
  const v = voice.find(x => ('$' + x.props.VoiceName) === r.label || x.props.VoiceName === r.label);
  if (v) { const k = trims[v.props.VoiceName]; if (k !== undefined) return Math.min(r.end, v.tick + k*TICK); }
  return r.end;
}
function updateSubtitleWindow() {
  const t = playhead;
  const sub = subs.find(r => r.start <= t && t < trimmedSubEnd(r) && (r.text||'').length);
  $('subActor').textContent = sub && sub.actor ? sub.actor : ' ';
  $('subText').innerHTML = '';
  if (sub) $('subText').textContent = sub.text;
  else $('subText').innerHTML = '<span class="idle">…</span>';
  const cut = cuts.find(c => c.range[0] <= t && t < c.range[1]);
  const vo = voice.find(v => v.tick <= t && t < v.tick + keptDur(v)*TICK);
  const bits = [`<b>${fmt(t)}</b> / frame <b>${frameOf(t)}</b>`];
  if (cut) bits.push(`cut <b>${cut.name}</b>${inEdit(t) ? ' <span style="color:#ff8a8a">(cut)</span>' : ''}`);
  const ed = toEdited(t);
  if (ed !== null && edits.length) bits.push(`edited <b>${fmt(ed)}</b>`);
  if (vo)  bits.push(`VO <b>${vo.props.VoiceName}</b>`);
  $('infoline').innerHTML = bits.join(' · ');
}

// ---- lip sync ----
const LIP = DATA.lipsync || [];
// mouth shape targets: [width, height, upperLipCurl, teeth]
const VISEME = {
  bmp: [0.62, 0.04, 0,   0],
  fv:  [0.58, 0.16, 0.5, 1],
  aa:  [0.60, 0.92, 0,   0],
  ee:  [1.00, 0.30, 0,   1],
  oo:  [0.34, 0.62, 0,   0],
  ln:  [0.52, 0.36, 0,   1],
  sh:  [0.46, 0.48, 0,   0],
};
function lipAt(t) {
  for (const ln of LIP) {
    if (t < ln.frames[0][0] || t > ln.frames[ln.frames.length-1][1]) continue;
    for (const f of ln.frames)
      if (f[0] <= t && t < f[1])
        return {phoneme:f[2], shapes:f[3], actor:ln.actor, voice:ln.voice};
  }
  return null;
}
function drawMouth(cx, state) {
  const c = cx.canvas;
  cx.clearRect(0, 0, c.width, c.height);
  cx.fillStyle = '#0a0b0f'; cx.fillRect(0, 0, c.width, c.height);
  let w = 0.55, h = 0.10, curl = 0, teeth = 0, tot = 0;
  if (state && state.shapes) {
    let W = 0, H = 0, C = 0, T = 0;
    for (const [k, v] of Object.entries(state.shapes)) {
      const p = VISEME[k]; if (!p || !v) continue;
      W += p[0]*v; H += p[1]*v; C += p[2]*v; T += p[3]*v; tot += v;
    }
    if (tot > 0) { w = W/tot; h = H/tot; curl = C/tot; teeth = T/tot; }
  }
  const midX = c.width/2, midY = c.height/2 + 4;
  const rx = w * c.width * 0.36, ry = Math.max(1.2, h * c.height * 0.34);
  // lips
  cx.fillStyle = tot > 0 ? '#c76b7a' : '#3a3f4d';
  cx.beginPath(); cx.ellipse(midX, midY, rx + 5, ry + 5, 0, 0, 7); cx.fill();
  // mouth cavity
  cx.fillStyle = '#2a1016';
  cx.beginPath(); cx.ellipse(midX, midY, rx, ry, 0, 0, 7); cx.fill();
  // teeth
  if (teeth > 0.15 && ry > 3) {
    cx.fillStyle = 'rgba(238,240,245,' + Math.min(1, teeth) + ')';
    cx.beginPath();
    cx.rect(midX - rx*0.8, midY - ry, rx*1.6, Math.min(ry*0.55, 5));
    cx.fill();
  }
  if (curl > 0.2 && ry > 2) {
    cx.strokeStyle = 'rgba(238,240,245,' + curl + ')'; cx.lineWidth = 1.5;
    cx.beginPath(); cx.moveTo(midX - rx*0.7, midY + ry*0.4);
    cx.lineTo(midX + rx*0.7, midY + ry*0.4); cx.stroke();
  }
  // label
  cx.fillStyle = state ? '#e8e9ed' : '#3c3f4d';
  cx.font = 'bold 15px system-ui'; cx.textAlign = 'center';
  cx.fillText(state ? state.phoneme : '–', midX, 20);
  if (state) {
    cx.fillStyle = '#57b3ff'; cx.font = '10px system-ui';
    cx.fillText(state.actor || '', midX, c.height - 16);
    cx.fillStyle = '#767b8f'; cx.font = '9px system-ui';
    const top = Object.entries(state.shapes).sort((a,b) => b[1]-a[1])
                      .slice(0,3).map(([k,v]) => k+' '+v.toFixed(1)).join('  ');
    cx.fillText(top, midX, c.height - 5);
  }
  cx.textAlign = 'left';
}

// ---- stage preview (rough 3D) ----
const SCENE = DATA.scene || null;
const AIM_Z = 50;      // calibrated: cameras frame ~50cm above the actor root
const ASPECT = 16/9;
const KIND_COLOR = {pc:'#57b3ff', np:'#c98cff', en:'#ff7a7a', bg:'#7f8699', we:'#c9a227', other:'#8b8fa3'};

// Party members are drawn as their 1997 field models instead of pins. The atlas
// is baked by render_sprites.py and sits next to this file; anyone without a
// sprite (enemies, NPCs, Sephiroth) still gets the pin, and if chars.png is
// missing the whole panel silently falls back to pins.
const SPRITES = __SPRITES__;
let sprSheet = null;
if (SPRITES) {
  sprSheet = new Image();
  sprSheet.onload = () => drawStage();
  sprSheet.onerror = () => { sprSheet = null; };
  sprSheet.src = SPRITES.sheet || 'chars.png';
}
const sprReady = () => !!(sprSheet && sprSheet.complete && sprSheet.naturalWidth);
// the atlas is keyed by character, not by actor: `RedXIII` and `Red XIII` are
// the same person, and so is a double called `Cloud_01`
const sprKey = (label) => (label || '').toLowerCase().replace(/[^a-z0-9]+/g, '');
// Most actors are turned by their animation, not by the transform track, so
// their sampled yaw is a constant zero — a model drawn from that would face
// one arbitrary way all scene. Only actors the track actually rotates get a
// model; everyone else keeps the pin, which claims nothing about facing.
function actorTurns(a) {
  if (a._turns === undefined) a._turns = (a.p || []).some(p => p && p[3]);
  return a._turns;
}
function sprFor(a) {
  return sprReady() && actorTurns(a) ? (SPRITES.chars[sprKey(a.label)] || null) : null;
}
// Which column of the strip faces the camera. Column 0 is the model looking
// straight down the lens, columns advance anticlockwise, so the index is just
// where the camera stands relative to the way the actor is facing.
function sprCol(camYaw, actorYaw) {
  const step = 360 / SPRITES.angles;
  const rel = (((camYaw + 180 - actorYaw) % 360) + 360) % 360;
  return Math.round(rel / step) % SPRITES.angles;
}
let stageOn = !!(SCENE || LIP.length);
if (!stageOn) document.getElementById('stagewrap').classList.add('hidden');
if (!LIP.length) { const lb = document.getElementById('lipbox'); if (lb) lb.style.display = 'none'; }

function ueAxes(roll, pitch, yaw) {
  const r = roll*Math.PI/180, p = pitch*Math.PI/180, y = yaw*Math.PI/180;
  const SR=Math.sin(r), CR=Math.cos(r), SP=Math.sin(p), CP=Math.cos(p), SY=Math.sin(y), CY=Math.cos(y);
  return {F:[CP*CY, CP*SY, SP],
          R:[SR*SP*CY-CR*SY, SR*SP*SY+CR*CY, -SR*CP],
          U:[-(CR*SP*CY+SR*SY), CY*SR-CR*SP*SY, CR*CP]};
}
const dot3 = (a,b) => a[0]*b[0]+a[1]*b[1]+a[2]*b[2];

function project(cam, p, dz) {
  const ax = ueAxes(cam[3], cam[4], cam[5]);
  const d = [p[0]-cam[0], p[1]-cam[1], p[2]+dz-cam[2]];
  const fwd = dot3(d, ax.F);
  if (fwd <= 1) return null;
  const th = Math.tan(cam[6]*Math.PI/360);
  return {x: (dot3(d, ax.R)/fwd)/th, y: (dot3(d, ax.U)/fwd)/(th/ASPECT), d: fwd};
}

function sceneIndex(t) {
  const ticks = SCENE.ticks;
  let lo = 0, hi = ticks.length-1;
  while (lo < hi) { const m = (lo+hi)>>1; if (ticks[m] < t) lo = m+1; else hi = m; }
  if (lo > 0 && Math.abs(ticks[lo-1]-t) < Math.abs(ticks[lo]-t)) lo--;
  return lo;
}

function drawStage() {
  if (stageOn) {
    const mc = document.getElementById('mouthview');
    if (mc) drawMouth(mc.getContext('2d'), lipAt(playhead));
  }
  if (!SCENE || !stageOn) return;
  const i = sceneIndex(playhead);
  const cam = SCENE.cam[i];
  const cv = document.getElementById('camview'), cx = cv.getContext('2d');
  const mv = document.getElementById('mapview'), mx = mv.getContext('2d');
  cx.clearRect(0,0,cv.width,cv.height); mx.clearRect(0,0,mv.width,mv.height);
  cx.imageSmoothingEnabled = true; cx.imageSmoothingQuality = 'high';

  // gather actor samples
  const pts = [];
  for (const a of SCENE.actors) {
    const p = a.p[i];
    if (!p) continue;
    pts.push({a, p, pr: cam ? project(cam, p, AIM_Z) : null});
  }

  // ---- camera view ----
  cx.strokeStyle = '#2c2f3b'; cx.lineWidth = 1;
  cx.strokeRect(.5,.5,cv.width-1,cv.height-1);
  // thirds
  cx.strokeStyle = '#1b1e27';
  for (let k=1;k<3;k++){
    cx.beginPath(); cx.moveTo(cv.width*k/3,0); cx.lineTo(cv.width*k/3,cv.height); cx.stroke();
    cx.beginPath(); cx.moveTo(0,cv.height*k/3); cx.lineTo(cv.width,cv.height*k/3); cx.stroke();
  }
  if (!cam) {
    cx.fillStyle = '#575c70'; cx.font = '12px system-ui';
    cx.fillText('no camera data', 12, 20);
  }
  const onscreen = [];
  pts.filter(q => q.pr).sort((p,q) => q.pr.d - p.pr.d).forEach(q => {
    const sx = (q.pr.x*0.5+0.5)*cv.width, sy = (0.5 - q.pr.y*0.5)*cv.height;
    const inFrame = Math.abs(q.pr.x) < 1 && Math.abs(q.pr.y) < 1.6;
    // apparent height of a ~170cm figure
    const th = Math.tan(cam[6]*Math.PI/360);
    const pxPerCm = (1/q.pr.d)/(th/ASPECT) * cv.height/2;
    const hpx = 170*pxPerCm;
    const col = KIND_COLOR[q.a.kind] || KIND_COLOR.other;
    cx.globalAlpha = inFrame ? 1 : 0.25;
    const sp = sprFor(q.a);
    let topY;
    if (sp) {
      // the root is pelvis height, not the feet — drop to the floor and project
      // that, which stays right when the camera pitches
      const fp = project(cam, q.p, -sp.root) || q.pr;
      const feet = (0.5 - fp.y*0.5)*cv.height;
      const footX = (fp.x*0.5+0.5)*cv.width;
      const sc = Math.max(SPRITES.cmPerPx * pxPerCm, 7/sp.ch);   // stay visible when far off
      const w = sp.cw*sc, h = sp.ch*sc;
      const x0 = footX - sp.ox*sc, y0 = feet - sp.oy*sc;
      cx.drawImage(sprSheet, sprCol(cam[5], q.p[3]||0)*sp.cw, sp.y, sp.cw, sp.ch,
                   x0, y0, w, h);
      topY = feet - (sp.cm/SPRITES.cmPerPx)*sc;                  // crown, not cell edge
    } else {
      cx.strokeStyle = col; cx.fillStyle = col; cx.lineWidth = Math.max(2, hpx*0.10);
      // body line + head
      cx.beginPath(); cx.moveTo(sx, sy + hpx*0.12); cx.lineTo(sx, sy + hpx*0.75); cx.stroke();
      cx.beginPath(); cx.arc(sx, sy, Math.max(2.5, hpx*0.13), 0, 7); cx.fill();
      topY = sy;
    }
    if (inFrame || Math.abs(q.pr.x) < 1.6) {
      cx.globalAlpha = inFrame ? 1 : 0.4;
      cx.fillStyle = '#fff'; cx.font = '10px system-ui'; cx.textAlign = 'center';
      cx.fillText(q.a.label, sx, topY - Math.max(5, hpx*0.16));
      cx.textAlign = 'left';
    }
    if (inFrame) onscreen.push({label:q.a.label, d:q.pr.d, x:q.pr.x});
  });
  cx.globalAlpha = 1;

  // ---- top-down ----
  let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
  const all = pts.map(q => q.p);
  if (cam) all.push(cam);
  for (const p of all) { minX=Math.min(minX,p[0]); maxX=Math.max(maxX,p[0]);
                         minY=Math.min(minY,p[1]); maxY=Math.max(maxY,p[1]); }
  if (all.length) {
    const pad = 120;
    const span = Math.max(maxX-minX, maxY-minY, 300) + pad*2;
    const ccx = (minX+maxX)/2, ccy = (minY+maxY)/2;
    // world X = up on the map, world Y = right
    const toPx = (p) => [mv.width/2 + (p[1]-ccy)/span*mv.width,
                         mv.height/2 - (p[0]-ccx)/span*mv.height];
    if (cam) {
      const [px,py] = toPx(cam);
      const yaw = cam[5]*Math.PI/180, half = cam[6]*Math.PI/360;
      const len = 70;
      const dir = a => [Math.sin(a)*len, -Math.cos(a)*len];
      // map angle: world yaw 0 = +X = up
      const a1 = yaw - half, a2 = yaw + half;
      const p1 = dir(a1), p2 = dir(a2);
      const g = cx.createLinearGradient ? null : null;
      mx.fillStyle = 'rgba(255,87,87,.16)';
      mx.beginPath(); mx.moveTo(px,py);
      mx.lineTo(px+p1[0], py+p1[1]); mx.lineTo(px+p2[0], py+p2[1]); mx.closePath(); mx.fill();
      mx.strokeStyle = '#ff5757'; mx.lineWidth = 1; mx.stroke();
      mx.fillStyle = '#ff5757';
      mx.beginPath(); mx.arc(px,py,3.5,0,7); mx.fill();
    }
    for (const q of pts) {
      const [px,py] = toPx(q.p);
      const col = KIND_COLOR[q.a.kind] || KIND_COLOR.other;
      const lit = q.pr && Math.abs(q.pr.x)<1 && Math.abs(q.pr.y)<1.6;
      mx.globalAlpha = lit ? 1 : 0.42;
      mx.fillStyle = col;
      mx.beginPath(); mx.arc(px,py,4,0,7); mx.fill();
      // facing
      const ya = (q.p[3]||0)*Math.PI/180;
      mx.strokeStyle = col; mx.lineWidth = 1.5;
      mx.beginPath(); mx.moveTo(px,py);
      mx.lineTo(px + Math.sin(ya)*11, py - Math.cos(ya)*11); mx.stroke();
      mx.fillStyle = lit ? '#e8e9ed' : '#767b8f';
      mx.font = '9px system-ui'; mx.textAlign = 'center';
      mx.fillText(q.a.label, px, py-7);
      mx.textAlign = 'left';
    }
    mx.globalAlpha = 1;
  }

  // ---- side info ----
  const info = document.getElementById('stageInfo');
  onscreen.sort((a,b) => a.d-b.d);
  let html = '';
  if (cam) html += `<div><b>FOV</b> ${cam[6].toFixed(0)}° · cam (${cam[0]|0}, ${cam[1]|0}, ${cam[2]|0})</div>`;
  html += `<div style="margin-top:4px"><b>In frame (${onscreen.length})</b></div>`;
  for (const o of onscreen)
    html += `<div class="on">• ${o.label} <span class="dimmed">${(o.d/100).toFixed(1)}m${Math.abs(o.x)<0.33?' · centre':''}</span></div>`;
  const off = pts.filter(q => !onscreen.find(o => o.label===q.a.label));
  if (off.length) html += `<div class="dimmed" style="margin-top:4px">off: ${off.map(q=>q.a.label).join(', ')}</div>`;
  html += `<div class="dimmed" style="margin-top:6px">positions are actor roots; framing aim ≈ +${AIM_Z}cm</div>`;
  info.innerHTML = html;
}

function tickPlayback(ts) {
  if (!playing) return;
  // when audio is running it is the clock — keeps VO and playhead locked together
  let t = audioIsClock() ? audioEl.currentTime * TICK
        : (lastTs !== null ? playhead + (ts - lastTs)/1000 * TICK : playhead);
  // skip removed ranges — this is what the edit will look like
  const gap = inEdit(t);
  if (gap) {
    t = gap.b;
    if (t >= TOTAL) { playhead = TOTAL; positionPlayhead(); togglePlay(false); return; }
    seekAudio(t);
  }
  if (t >= TOTAL) { t = TOTAL; togglePlay(false); }
  playhead = Math.min(Math.max(t, 0), TOTAL);
  applyTrimGain();
  positionPlayhead(); updateSubtitleWindow(); drawStage();
  const x = 150 + playhead*pxPerTick;
  if (x > tlEl.scrollLeft + tlEl.clientWidth - 120) tlEl.scrollLeft = x - 200;
  lastTs = ts;
  if (playing) requestAnimationFrame(tickPlayback);
}
function togglePlay(force) {
  playing = force !== undefined ? force : !playing;
  $('playBtn').textContent = playing ? '⏸ Pause' : '⏵ Play';
  lastTs = null;
  if (audioEl) {
    if (playing) {
      ensureGraph();
      if (actx && actx.state === 'suspended') actx.resume();
      // start from where the playhead actually is, and don't let the audio
      // clock override it until the seek has landed
      seekAudio(playhead);
      audioEl.play().catch(() => { $('audioState').textContent = 'click page to enable audio'; });
    } else audioEl.pause();
  }
  if (playing) requestAnimationFrame(tickPlayback);
}

// scrub on the ruler; drag in the track area to select a range
let dragMode = null, dragAnchor = 0, dragMoved = false, trimTarget = null;
const tickAtX = (clientX, el) =>
  (clientX - el.getBoundingClientRect().left - 150) / pxPerTick;

scrubEl.addEventListener('mousedown', ev => {
  dragMode = 'scrub'; setPlayhead(tickAtX(ev.clientX, scrubEl));
});
rowsEl.addEventListener('mousedown', ev => {
  if (ev.target.classList.contains('sec')) return;      // clicking a block selects it
  const t = snapTick(tickAtX(ev.clientX, rowsEl), !ev.shiftKey);
  dragAnchor = t; dragMoved = false;
  dragMode = 'select';
  sel = {a:t, b:t};
  renderOverlay();
});
window.addEventListener('mousemove', ev => {
  if (!dragMode) return;
  if (dragMode === 'scrub') { setPlayhead(tickAtX(ev.clientX, scrubEl)); return; }
  const t = snapTick(tickAtX(ev.clientX, rowsEl), !ev.shiftKey);
  if (dragMode === 'select') {
    dragMoved = true;
    sel = {a: Math.min(dragAnchor, t), b: Math.max(dragAnchor, t)};
  } else if (dragMode === 'trim-l' && sel) {
    sel = {a: Math.min(t, sel.b - TPF), b: sel.b};
  } else if (dragMode === 'trim-r' && sel) {
    sel = {a: sel.a, b: Math.max(t, sel.a + TPF)};
  } else if (dragMode === 'trim-voice' && trimTarget) {
    const keep = Math.max(0.1, Math.min((t - trimTarget.tickStart)/TICK, trimTarget.full));
    if (keep >= trimTarget.full - 0.02) delete trims[trimTarget.voiceName];
    else trims[trimTarget.voiceName] = Math.round(keep*100)/100;
    render();
    return;
  }
  renderOverlay(); updateEditInfo();
});
window.addEventListener('mouseup', ev => {
  if (dragMode === 'select' && !dragMoved) {
    // a plain click: seek there, and clear any selection
    const t = tickAtX(ev.clientX, rowsEl);
    sel = null; setPlayhead(t); renderOverlay(); updateEditInfo();
  }
  dragMode = null;
});
rowsEl.addEventListener('dblclick', ev => {
  // double-click a struck-through region to restore it
  const t = tickAtX(ev.clientX, rowsEl);
  if (restoreAt(t)) { sel = null; }
});

// ---- keyboard ----
window.addEventListener('keydown', ev => {
  if (ev.target.tagName === 'INPUT') return;
  const k = ev.key;
  if (k === ' ') { ev.preventDefault(); togglePlay(); }
  else if (k === 'Delete' || k === 'Backspace') {
    ev.preventDefault();
    // A cue that can be switched off on its own wins over the time range it
    // happens to occupy. Clicking an SE also selects its span, and deleting
    // that span would ripple the whole timeline — when all you wanted was to
    // lose one sound and leave every cut exactly where it is.
    // Shift+Delete still cuts the range, and Escape clears the selection.
    if (!ev.shiftKey && pickedCue && cueKey(cueDescriptor(pickedCue))) deleteCue();
    else if (sel && sel.b > sel.a) deleteSelection();
    else deleteCue();
  }
  else if (k.toLowerCase() === 'i') { ev.preventDefault();
    sel = {a: snapTick(playhead, !ev.shiftKey), b: sel ? Math.max(sel.b, snapTick(playhead,!ev.shiftKey)+TPF) : snapTick(playhead,!ev.shiftKey)+TPF};
    renderOverlay(); updateEditInfo(); }
  else if (k.toLowerCase() === 'o') { ev.preventDefault();
    const t = snapTick(playhead, !ev.shiftKey);
    sel = {a: sel ? Math.min(sel.a, t-TPF) : t-TPF, b: t};
    renderOverlay(); updateEditInfo(); }
  else if (k.toLowerCase() === 'k') { ev.preventDefault(); toggleForceVisible(ev.shiftKey); }
  else if (k.toLowerCase() === 'm') { ev.preventDefault(); toggleMusic(); }
  else if (k === 'Escape') { sel = null; renderOverlay(); updateEditInfo(); }
  else if (k.toLowerCase() === 's' && !ev.ctrlKey && !ev.metaKey) { ev.preventDefault(); makeSafe(); }
  else if (k.toLowerCase() === 'r') { ev.preventDefault(); restoreAt(playhead); }
  else if (k.toLowerCase() === 'v' && !ev.ctrlKey && !ev.metaKey) { ev.preventDefault(); toggleStack(); }
  else if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === 'z') {
    ev.preventDefault(); ev.shiftKey ? redo() : undo();
  }
  else if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === 'y') { ev.preventDefault(); redo(); }
  else if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === 's') { ev.preventDefault(); exportPlan(); }
  else if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === 'b') { ev.preventDefault(); buildAndInstall(); }
  else if ((ev.ctrlKey || ev.metaKey) && k.toLowerCase() === 'o') { ev.preventDefault(); $('loadBtn').onclick(); }
  else if (k === 'ArrowRight') { ev.preventDefault(); setPlayhead(playhead + TPF*(ev.shiftKey?10:1)); }
  else if (k === 'ArrowLeft')  { ev.preventDefault(); setPlayhead(playhead - TPF*(ev.shiftKey?10:1)); }
  else if (k === '[') { ev.preventDefault();
    const c = cuts.find(c => c.range[0] <= playhead && playhead < c.range[1]);
    if (c) { sel = {a:c.range[0], b:c.range[1]}; renderOverlay(); updateEditInfo(); } }
  else if (k === 'Home') { ev.preventDefault(); setPlayhead(0); }
  else if (k === 'End')  { ev.preventDefault(); setPlayhead(TOTAL); }
  else if (k.toLowerCase() === 'm' && !ev.ctrlKey && !ev.metaKey) { ev.preventDefault(); toggleMute(); }
});

function toggleMute() {
  if (!audioEl) return;
  audioEl.muted = !audioEl.muted;
  $('muteBtn').textContent = audioEl.muted ? '🔇' : '🔊';
}
$('muteBtn').onclick = toggleMute;
$('vol').oninput = e => { if (audioEl) audioEl.volume = e.target.value/100; };

$('playBtn').onclick = () => togglePlay();
$('stageBtn').onclick = () => {
  if (!SCENE && !LIP.length) return;
  stageOn = !stageOn;
  document.getElementById('stagewrap').classList.toggle('hidden', !stageOn);
  drawStage();
};
document.querySelectorAll('#toolbar button[data-z]').forEach(b =>
  b.onclick = () => { pxPerTick *= parseFloat(b.dataset.z); render(); });
$('fitBtn').onclick = () => { pxPerTick = (tlEl.clientWidth - 200)/TOTAL; render(); };
function toggleStack() {
  stackOverlaps = !stackOverlaps;
  $('stackBtn').textContent = stackOverlaps ? '⇕ Unstack overlaps' : '⇕ Stack overlaps';
  render();
}
$('stackBtn').onclick = toggleStack;
$('undoBtn').onclick = undo;
$('redoBtn').onclick = redo;
$('resetBtn').onclick = resetEdits;
$('saveBtn').onclick = exportPlan;
$('loadBtn').onclick = async () => {
  // with the helper: offer the saved plan for this cutscene first
  if (helper) {
    try {
      const r = await fetch('/plan?ev=' + encodeURIComponent(DATA.cutscene));
      if (r.ok) {
        const j = await r.json();
        if (j.ok && applyPlan(j.plan, 'saved plan')) return;
      }
    } catch (e) {}
  }
  $('planFile').click();
};
$('planFile').onchange = ev => {
  const f = ev.target.files && ev.target.files[0];
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => {
    try { applyPlan(JSON.parse(rd.result), f.name); }
    catch (e) { setBuild('bad', 'could not read that file: ' + e.message); }
  };
  rd.readAsText(f);
  ev.target.value = '';
};

// ---- one-click build & install (needs the local helper) ----
let helper = null;
function applyPlan(plan, sourceLabel) {
  if (!plan || typeof plan !== 'object') { setBuild('bad', 'not an edit plan'); return false; }
  if (plan.cutscene && plan.cutscene !== DATA.cutscene) {
    setBuild('bad', 'that plan is for ' + plan.cutscene + ', this page is ' + DATA.cutscene);
    return false;
  }
  pushUndo();
  edits = normalise((plan.removeRanges || []).map(([a, b]) => ({a, b})));
  trims = {};
  for (const t of (plan.trimLines || []))
    if (t.voice && t.keepSeconds) trims[t.voice] = t.keepSeconds;
  killed = {}; forced = {};
  for (const a of (plan.forceVisible || [])) forced[a] = true;
  hiddenA = {};
  for (const a of (plan.forceHidden || [])) hiddenA[a] = true;
  music = {};
  for (const a of (plan.replaceMusic || [])) music[a] = true;
  for (const d of (plan.disableCues || [])) {
    const k = cueKey(d);
    if (k) killed[k] = d;
  }
  sel = null; pickedCue = null;
  render();
  const n = edits.length, nt = Object.keys(trims).length, nk = Object.keys(killed).length;
  setBuild('good', 'loaded ' + (sourceLabel || 'plan') + ' — ' +
    [n && (n + ' cut' + (n>1?'s':'')), nt && (nt + ' trim' + (nt>1?'s':'')),
     nk && (nk + ' deleted cue' + (nk>1?'s':''))].filter(Boolean).join(', '));
  return true;
}

function planObject() {
  const warn = edits.map(x => {
    const h = impactOf(x.a, x.b);
    return {range:[x.a, x.b], seconds:+((x.b-x.a)/TICK).toFixed(3),
            frames:Math.round((x.b-x.a)/TPF), wholeShots:h.cuts, voiceLines:h.lines.length,
            splitsVoiceLine:h.midLine || null, audioOverrunSeconds:+(h.overrun/TICK).toFixed(2),
            strandedSubtitles:h.stranded, lipsyncDesync:h.lipSplit,
            stateTriggers:h.triggers, jumps:h.jumps.length};
  });
  return {tool:'ff7r-cutscene-editor v0.4 (ripple)',
          cutscene:DATA.cutscene, area:DATA.area || null,
          tickResolution:TICK, displayRate:FPS, ticksPerFrame:TPF,
          playbackRange:[PB[0], PB[1]], mode:'ripple-delete',
          removeRanges:edits.map(x => [x.a, x.b]), keepRanges:keepRanges(),
          disableCues: Object.values(killed),
          forceVisible: Object.keys(forced),
          forceHidden: Object.keys(hiddenA),
          replaceMusic: Object.keys(music),
          trimLines: Object.entries(trims).map(([v, k]) => {
            const e = voice.find(x => x.props.VoiceName === v) || {};
            return {voice:v, keepSeconds:k, originalSeconds:e.duration || null,
                    actor:e.actor || null, tick:e.tick ?? null};
          }),
          originalTicks:TOTAL, editedTicks:editedTicks(),
          originalSeconds:+(TOTAL/TICK).toFixed(3), editedSeconds:+(editedTicks()/TICK).toFixed(3),
          impact:warn};
}
function setBuild(cls, msg) {
  const el = $('buildLine');
  el.className = cls || '';
  el.textContent = msg || '';
}
fetch('/ping').then(r => r.ok ? r.json() : null).then(j => {
  if (!j || !j.ok) throw 0;
  helper = j;
  $('installBtn').title = 'Build and install to ' + j.game;
  // resume where you left off: load this cutscene's saved plan if the page is untouched
  fetch('/plan?ev=' + encodeURIComponent(DATA.cutscene)).then(r => r.ok ? r.json() : null)
    .then(p => {
      if (p && p.ok && !edits.length && !Object.keys(trims).length && !Object.keys(killed).length)
        applyPlan(p.plan, 'saved plan');
    }).catch(() => {});
}).catch(() => {
  helper = null;
  $('installBtn').disabled = true;
  $('installBtn').title = 'Start StartEditor.bat and open the editor from there to enable this';
});
async function buildAndInstall() {
  if (!helper) {
    setBuild('bad', 'run StartEditor.bat and open the editor from there');
    return;
  }
  if (!edits.length) { setBuild('bad', 'nothing to build — make a cut first'); return; }
  $('installBtn').disabled = true;
  setBuild('busy', 'building ' + DATA.cutscene + '…');
  try {
    const r = await fetch('/build', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(planObject())});
    const j = await r.json();
    setBuild(j.ok ? 'good' : 'bad',
             j.ok ? ('installed ' + DATA.cutscene + '_P — restart the cutscene to test')
                  : 'build failed — see log');
    $('buildLogText').textContent = j.log || '';
    $('buildlog').style.display = 'block';
  } catch (e) {
    setBuild('bad', 'helper not responding (' + e + ')');
  } finally {
    $('installBtn').disabled = false;
  }
}
$('installBtn').onclick = buildAndInstall;
$('logClose').onclick = () => { $('buildlog').style.display = 'none'; };
$('cutBtn').onclick = deleteSelection;
$('safeBtn').onclick = makeSafe;
$('keepBtn').onclick = () => toggleForceVisible(false);
$('hideBtn').onclick = () => toggleForceVisible(true);
$('musicBtn').onclick = toggleMusic;

render();
setPlayhead(0);
</script>
</body>
</html>'''


HERE = os.path.dirname(os.path.abspath(__file__))
SPRITE_PNG = os.path.join(HERE, 'chars.png')
SPRITE_META = os.path.join(HERE, 'chars.json')


def sprite_meta(out_dir):
    """Atlas metadata for the template, and the atlas copied beside the page.

    Returns 'null' when render_sprites.py has not been run, which makes the
    stage panel fall back to the old pins.
    """
    if not (os.path.exists(SPRITE_META) and os.path.exists(SPRITE_PNG)):
        return 'null'
    dst = os.path.join(out_dir, 'chars.png')
    try:
        if (not os.path.exists(dst)
                or os.path.getmtime(dst) < os.path.getmtime(SPRITE_PNG)
                or os.path.getsize(dst) != os.path.getsize(SPRITE_PNG)):
            shutil.copyfile(SPRITE_PNG, dst)
    except OSError:
        return 'null'
    return json.dumps(json.load(open(SPRITE_META)))


def build(src, out, nav=False):
    data = json.load(open(src))
    nav_html = '<a href="../index.html">◀ All cutscenes</a>' if nav else ''
    html = (TEMPLATE
            .replace('__TITLE__', data['cutscene'])
            .replace('__NAV__', nav_html)
            .replace('__SPRITES__', sprite_meta(os.path.dirname(os.path.abspath(out))))
            .replace('__DATA__', json.dumps(data)))
    with open(out, 'w') as f:
        f.write(html)
    return os.path.getsize(out)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    size = build(args[0], args[1], nav='--nav' in sys.argv)
    print('wrote', args[1], size//1024, 'KB')
