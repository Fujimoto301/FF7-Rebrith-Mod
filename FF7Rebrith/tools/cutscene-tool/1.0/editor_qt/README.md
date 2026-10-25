# Cutscene editor — native (editor_qt)

The same editor as v3, as a desktop application instead of a web page.

```
StartEditorNative.bat          run it (installs PySide6 the first time)
py -3 -m editor_qt --ev EV_FOREE_8510
py -3 -m unittest discover -s editor_qt/tests -t .
```

**The browser builds are retired.** `StartEditor.bat`, `serve_editor.py`, the
v1 `browser/` folder, `editor_v3` and the generated `browser_v2` pages moved to
`Archive/browser-build/` on 2026-08-16; this editor replaced all of them. They
are moved, not deleted, and `Archive/README.md` says how to put any of them
back.

What did **not** move is `browser_v2/timelines` — the extracted JSON, the scene
audio and `manifest.json`. That is the data this editor reads, and the folder
only ever looked like part of the browser build. `make_viewer.py` still
regenerates a standalone viewer page from any of those JSONs if one is ever
wanted.

## Why not HTML

Four of the complaints about the browser build are not bugs in it. They are
properties of the platform:

| Wanted | In a browser |
|---|---|
| right-click → replace this dialogue, via the Windows file browser | a web page gets a `File` object with **no path**, ever |
| resize the sections | only if the page author builds a splitter for every seam |
| a tracker that cannot run off screen | the page lays out in document flow; the row labels scroll away from their rows |
| subtitles under the picture | possible, but the whole layout is one flow |

Add the two structural costs — the editor could only reach `patcher.py` through
a local HTTP helper that has to be running, and the page cached so hard that a
missing button was the usual tell — and the case for a window is made. Qt gives
all four for free, and the backend was already Python, so the helper disappears.

## Layout

```
editor_qt/
  core/          no Qt, no I/O except through library.py — the part worth testing
    units.py     TimeBase: ticks, frames, seconds, and the only way between them
    timeline.py  the shape of an extracted timeline; the Cutscene façade
    lanes.py     cutscene + edits -> rows of blocks
    cues.py      cue identity, and what can be switched off at all
    edits.py     EditState and its pure operations
    music.py     the BGM banks, their slices, and what a cue must be called
    collapse.py  carrying fades and level streaming back across a cut
    impact.py    what a cut would cost; make-safe; snapping
    plan.py      the edit plan — the contract with build_mod.py
    stage.py     camera projection and lip-sync blending
    library.py   the folder of timelines
  ui/            PySide6 only
    theme.py         palette: structural rows as v2/v3, cue rows by family
    timeline_view.py the tracker
    preview.py       camera view, top-down map, mouth, subtitle bar
    panels.py        scene list, details, actors, in-frame
    music_picker.py  choose a bank and a slice for one music trigger
    transport.py     preview audio and the playback clock
    main_window.py   docks, menus, toolbar, shortcuts
  tests/
```

Rules of thumb, carried over from v3 because they earned their keep:

- `core/` may not import from `ui/`. If a rule ends up in `main_window.py`, it
  is in the wrong place.
- editing logic lives in `core/`; the widgets read it and paint.
- a new track is a builder in `core/lanes.py` added to `LANE_BUILDERS`, and
  nothing in the painting code changes.

## The waveform

The top row of the timeline is the audio the editor is playing, drawn as an
amplitude envelope so you can see the frame a sound starts on rather than
scrubbing for it. It **follows the preview render**: the scene opens on the
offline `.ogg`, and every re-mix — a cue switched off, a line trimmed, a music
trigger repointed — redraws it from the file you are actually listening to.
Before that it stayed on the offline mix for the whole session, so the moment
an edit was made the picture of the sound and the sound itself were two
different recordings.

`core/waveform.py` shells out to ffmpeg (already required by the audio
pipeline), decodes to mono 22 kHz, and reduces to **100 peaks per second**. That
fixed rate is the design decision worth keeping: drawing from raw samples would
mean re-reading the file at every zoom level, whereas an envelope is a walk over
a small array. A 90-second scene is 9,000 bytes.

Peaks are reduced by **maximum**, never by sampling — at whole-scene zoom one
column covers half a second, and a transient that falls between samples would
vanish. A cut landing on a sound you cannot see is the failure this guards
against.

Caching is keyed on the audio file's mtime and written to
`browser_v2/timelines/audio/.peaks/` (already gitignored, ~18 KB per scene).
Re-rendering a mix invalidates it automatically. First decode of a 50-second
scene is about a third of a second and happens on a worker thread; every visit
after that is instant.

If ffmpeg is missing or a file will not decode, the row simply does not appear.
A missing waveform is a missing row, not an error.

## Cue colours

The structural rows keep the colours they had in v2 and v3. The cue rows used
to all be the same amber, which made a dozen rows of identical orange ticks you
could only tell apart by reading the label.

They are now coloured by **family**, not one hue per clip type — a scene can
show a dozen cue rows, and a dozen unique hues would collide both with each
other and with the structural rows. Seven families are distinguishable at a
glance and mean something:

| Family | Colour | Rows |
|---|---|---|
| audio | amber | SE |
| rumble | rust | vibration |
| music | rose | BGM |
| fade | indigo | fades |
| actor | cyan | show/hide, crowd, game speed |
| light | yellow | directional and environment light |
| flow | crimson | state triggers, jumps — what the game needs to progress |
| rig | violet | constraints, bindings |
| system | slate | streaming volumes |
| — | olive | anything unrecognised |

The mapping is `CLIP_FAMILY` in `core/lanes.py`; the colours are `LANE_COLOR` in
`ui/theme.py`. An unknown clip gets its own muted olive rather than borrowing a
family's colour, so a clip type we have never seen is visibly new rather than
quietly mislabelled. The gutter swatch beside each row label is the legend.

## Character colours

Pins in the camera view and the top-down map, the "In frame" list, and the
swatches in the Actors panel all take their colour from who the actor *is*:

| | | | |
|---|---|---|---|
| Cloud | baby teal | Vincent | deep red |
| Barret | brown | Cid | dark blue |
| Tifa | yellow | Sephiroth | light silver |
| Aerith | baby pink | Feelers | near-white, slightly yellow |
| Red XIII | orange | Extras, doubles, props | grey |
| Yuffie | green | Everyone else | magenta |
| Cait Sith | violet *(placeholder)* | Zack | steel blue *(placeholder)* |

Cait Sith and Zack were not specified; those two are guesses and easy to change.

The colours live in `CHARACTER_COLOR` in `ui/theme.py`. *Which character an
actor is* is a separate question, answered by `core/characters.py`, because the
same person arrives under many names: `Cloud`, `CloudAge14`, `Cloud_Weapon`,
`cut_PC0000_00b` and `EV_COMON_0010_PC0000_00` are all Cloud.

Three rules in there are worth not undoing:

- **Event-scoped names are unwrapped, not guessed at.** `EV_COMON_0010_FA0052_00a`
  has its scene prefix stripped and the remainder identified on its own. If the
  remainder still cannot be placed it is grey dressing rather than a magenta
  NPC — those names only ever exist for one event.
- **A relative is not the character.** `TifaAge13` is Tifa; `TifaPapa` and
  `ZackFather` are not. Without that guard the prefix match hands a relative the
  character's colour, which is the exact confusion the colours exist to prevent.
- **Doubles are only mapped where confirmed.** `PC_IDS` holds PC0000 → Cloud and
  PC0003 → Aerith because `SESSION_NOTES_2026-08-08.md` establishes both by
  observation. The others are deliberately left unmapped: a double wearing the
  wrong character's colour is worse than a neutral one, since telling two copies
  of the same character apart is the whole reason for colouring pins.

Across all 755 scenes every actor label resolves to a key that has a colour;
`test_core.py::Characters` pins the classification down.

## Dialogue split by speaker

**Split dialogue by speaker** — in the toolbar, under **View**, or `Ctrl+D` —
gives every character who speaks their own row. On unless you turn it off; the
choice is remembered between sessions like the window layout, and it changes
nothing about what gets built.

It exists because one dialogue row is unusable in a busy scene. Lines overlap
constantly — a reaction lands under the tail of the line it answers, and a
three-way exchange buries the middle one entirely. A buried block cannot be
clicked, so it cannot be trimmed, dragged or switched off. Across the 678 scenes
that have voice, 977 lines are completely covered by another on the combined
row; split by speaker, 81 are, and those are one character talking over
themselves.

Who is speaking is answered in order of how much the answer is worth:

1. **The scene's own label.** `actor` on the voice event, which the extraction
   fills in wherever it could match a subtitle. Roughly a third of the lines in
   a scene arrive without one: grunts, reactions, anything said off-screen.
2. **What this scene proves its codes mean.** A VoiceName ends in a speaker
   code — `C1910_MAIN_8000_0100_00_cld` is Cloud — and the labelled lines in the
   same scene say what each code means *here*. A code whose labelled lines
   disagree is dropped rather than settled by majority.
3. **`characters.VOICE_CODE_SPEAKER`.** Counted, not guessed: every labelled
   line in all 678 voiced scenes votes for its code, and a code is in the table
   only where at least six lines agree and at least three quarters name the same
   person. The generic codes are absent by that rule — `mma`, `skm` and `mfa`
   are shared by every guard, trooper and tannoy in the game.
4. **The raw code.** `snk` is a poor row heading but an honest one, and it still
   separates that speaker's lines from everyone else's, which is what the row is
   for.

A row belonging to one of the named cast wears that character's colour, the same
key the stage pins use, so the row and the pin above it agree about who is
talking. Rows keep `kind='voice'`, so trimming, dragging and the lip-sync follow
behave exactly as they do on the combined row.

## Panels, and getting them back

Everything except the picture and its subtitles is a dock: **Timeline**,
Cutscenes, Details, Actors, In frame, Top-down, Lip sync, Build log. Any of them
can be dragged somewhere else, floated, or closed with the × on its title bar.

The tracker used to be the bottom half of a fixed vertical splitter — the one
arrangement in the window you could not change. It is now a dock like the rest,
starting in the bottom area with both bottom corners assigned to it, so it runs
the full width of the window instead of being squeezed between the left and
right columns. Move it wherever it reads best.

Closing one used to be a one-way door. A hidden dock has no affordance of its
own — the title bar you would click to bring it back went with it — the
toolbar's own right-click menu is no help once the toolbar itself is hidden, and
because the layout is saved on exit the panel stays gone across restarts with
nothing on screen to say it ever existed. Hence the menu bar, which cannot be
dismissed:

- **View ▸ Panels** — one entry per dock, ticked when it is showing.
- **View ▸ Transport** — the toolbar.
- **View ▸ Show every panel** — unhide everything and leave the arrangement
  alone, for when one was closed by accident.
- **View ▸ Reset window layout** — every dock back in its starting area, the
  toolbar back, the tracker back to a usable height. `_apply_default_layout`
  re-adds only what is out of place, rather than restoring a `saveState` blob:
  `restoreState` over an already-tabified layout leaves the old tab bar behind,
  so resetting twice grew a second row of Details/Actors tabs.

The **In frame** panel scrolls rather than growing. Its list changes on every
scrubbed frame, and a word-wrapped label asks for whatever height its text
needs; left in a plain layout that became the dock's minimum, so scrubbing into
a crowded shot pushed everything stacked with it off the bottom of the screen.

The three toolbar toggles — split dialogue, carry fades, restore preload lead —
are tick boxes. A checkable toolbar button says it is on by looking very
slightly pressed, which is unreadable with three of them in a row. The QAction
behind each one is still what the menu, the shortcut and the code talk to; the
box is a second view of the same state.

## The plan format is still the contract

`patcher.py` and `build_mod.py` read `removeRanges`, `trimLines`, `disableCues`,
`forceVisible`, `forceHidden`, `replaceMusic`, `repointMusic`, `playbackRange`,
`tickResolution`, `displayRate` and `ticksPerFrame` **by name**, and a plan
saved by an earlier build has to load again unchanged.

`tests/test_core.py::PlanParity` loads every plan in `../plans` — including the
ones confirmed working in game — reads each into edit state, writes it back out
and asserts the fields are byte-identical. It also re-derives the `impact`
analysis and checks it against what was saved, because the warnings are the only
thing standing between a plausible selection and a softlock.

Two details in `plan.py` exist purely for that parity, and are easy to undo by
accident:

- `_num` writes an integral tick as `96000`, not `96000.0`. Snapping produces
  floats in Python because `ticks_per_frame` is a float, and JSON would carry
  that straight into the file.
- `_fixed` rounds half-up like JavaScript's `toFixed`, not half-to-even like
  Python's `round`. The same reason `units.round_half_up` exists: a tick landing
  exactly between two frames has to snap the way it always did.

## Finding a cutscene

The scene list shows each scene's **opening line** under its name, and the
search box matches **names, areas, cast and dialogue** — typing `wake up` finds
the five scenes where somebody says it.

Both come out of `manifest.json`, which already carried a `preview` (first line)
and a `search` blob (cast plus every line) for 631 of the 755 scenes. No index
is built and nothing is cached to disk.

Searching is two-stage, and the reason is worth knowing before touching
`SceneLibrary.search`. The manifest blob runs cast names and dialogue together
with spaces, so a snippet cut straight out of it can splice a name onto a line
and read as though the wrong character said it — `Barret Myrna! Wake up` is
Barret *saying* "Myrna! Wake up". So the blob decides **which** scenes match,
and then each matching scene's own subtitle records decide **what** to quote:
a real actor, a real line. Timelines parse in about 7ms and the lines are
cached, so this is instant for anything a person actually types. Past
`RESOLVE_LIMIT` matches, scenes fall back to their opening line rather than
paying for a file read nobody is reading the result of.

## Editing

| | |
|---|---|
| drag a block | move that cue to a new time (SE, dialogue, music) |
| `Shift`+drag | sweep out a range — what a plain drag used to do |
| `Alt`+drag | move without snapping |
| right-click | what can be done to the block under the pointer |
| `R` | put the selected cue back where the scene authored it |
| `Del` | switch off the selected cue — or cut the selected range if no cue is selected |
| `Shift+Del` | always cut the selected range |
| `Ctrl+M` | point the selected music trigger at a different track |
| `Ctrl+Z` / `Ctrl+Y` | undo / redo |
| `Ctrl+S` | save the edit plan |
| `Ctrl+B` | save, build and install |

### Pointing a music trigger somewhere else

Right-click a block on the Music cues row and pick another track.
`MUSIC_REPOINTING.md` has the full account; the three things worth knowing at
the keyboard are:

The preview follows: the mix is rebuilt from cue names, so the track you hear
— and the waveform on the top row — become the one you picked. Pointing a cue
at `bgm_silence` stops the music there, which is what the game does with it.

**It changes this cue, not the music.** The bank is not an import — the game
resolves `MusicName` at runtime — so the edit is one string inside this
cutscene and has no effect anywhere else. That is the difference from
`replaceMusic`, which rebuilds a BGM bank and therefore changes that track in
every scene that plays it.

**A bank is a folder.** `bgm_Corle_005` holds four streams; the picker's right
column is those streams, captioned with the sections that use them, and each
one auditions from the `.wav` AudioMog extracted. Slice 0 is the bare bank
name, slice 1 is `bgm_Corle_005_01`.

**The new name can be shorter than the old one but never longer**, because the
patch is in place: the name is written into the bytes the old one occupied and
padded with NULs. A 13-character cue can reach about half the library. Banks
that will not fit are listed anyway, dim, with the reason — and they still
play, because knowing the track exists is worth more than a tidier list.

### Dragging a cue

`CUE_DRAGGING.md` has the full account; the two things worth knowing at the
keyboard are:

**A cue stops at its neighbours.** SE, voice and subtitle cues share sorted
Times arrays — 19 SE cues in one array on EV_FOREE_8510 — and the patcher
refuses any move that would unsort one. So a cue slides freely in the gap
between the cues either side of it and cannot cross them. The block stops
under the pointer and the status bar names what stopped it, rather than the
move being accepted and then dropped during the build. Gaps are usually
seconds wide, not frames.

**A line of dialogue moves as a line.** Dragging a Voice block takes its
subtitle on/off pair with it, by the same delta, so the caption stays with the
audio. Lip sync follows on its own — phoneme times are relative to the clip
start.

Moves are stored in original ticks, so a cut made afterwards does not drag the
cue somewhere else; it keeps its place in the surviving footage. A cue dragged
onto footage a later cut removes is reported in the plan's `lostCues`, never
silently forgotten.

Dragging a cue **out of a cut** is the case the feature was really built for,
and it needed a fix on the other side: `patch_file` breaks the name of any cue
the cut swallowed, which was silently undoing the rescue. A cue being
relocated now keeps its name.

**Per-cue priority is deliberate**, and matches v2 and v3: clicking an SE and
pressing `Del` removes that sound, not the half-second of scene it happens to
occupy. A disabled cue is drawn struck through rather than removed — nothing is
deleted from the asset, the name is broken, and pressing `Del` again puts it
back.

Two refusals are worth recognising:

- **Protected clips** (`SendStateTrigger`, `Jump`, `StoryJump`) are never
  switched off, because the game uses them to progress. In practice a state
  trigger refuses as *unnamed* rather than *protected* — it carries only a
  `TriggerID`, none of `CUE_NAME_FIELDS`, so there is no name to break and the
  protected check is never reached. Either way the editor will not do it. This
  is the behaviour v2 and v3 had, and `test_a_state_trigger_is_always_refused`
  pins it down.
- **Unnamed blocks** cannot be disabled individually at all, because in-place
  patching cannot delete anything — a cue is switched off by breaking the name
  the game looks up, and a block with no name has nothing to break. The status
  bar says so and points at `Shift+Del`.

Cuts snap outward to frame boundaries before being applied, because the
patcher's key correction wants cuts on frames. The status bar names what a cut
costs — a split line, a stranded subtitle, a removed state trigger — using the
same `impact_of` analysis that goes into the plan.

### Playing an edit is a preview, not a recording

`Space` plays *the cut*, not the footage. When the playhead walks into a range
marked for deletion it steps straight out the far side, so what you watch is
what the built mod will play: a ten-second scene with three seconds cut takes
seven seconds to play through.

The skip itself is `core.edits.skip_over`, and it is one pass because
`normalise_cuts` merges touching spans — landing on a span's far edge can never
be inside another. `PlaybackClock` applies it before emitting `tick`, so no
frame is ever drawn from removed footage, and emits `jumped` on the way out so
the window can re-seek the audio; without that the picture skips and the sound
plays on through the gap. Seeking marks the player untrusted for `SEEK_SETTLE`,
which is what stops the stale position it reports meanwhile from dragging the
playhead back into the gap it just left.

**Scrubbing into a cut is still allowed** — it is how you check an edge — but
pressing `Space` from inside one starts on the far side rather than on footage
that is going away.

*This was a regression.* v2 and v3 both skipped; the Qt port's clock did not
consult the edit at all. `SkipOverCuts` in the tests pins the behaviour down.

### Reading a range marked for deletion

The band is drawn **over** the rows, not under them. Painting it first was the
whole reason it read as faint: every row then drew back over it at full
strength, so the wash had to compete with the tracker instead of sitting on top
of it.

Four things stack, each carrying a different piece of the meaning: the footage
inside is knocked back so it reads as already gone, a red tint says why, 45°
stripes make the band unmistakable at any zoom even across a busy row, and hard
2px edges mark exactly which frames the join will land between. A plate in the
band gives the cost (`−7.90s · 237f`) wherever there is room for it, and the
foot of the ruler carries a solid strip for every cut — zoomed in far enough to
work on a join, the band itself can fill the screen or sit entirely off it, and
the ruler is the one place the whole edit stays visible.

The stripes are drawn by hand rather than with `Qt.BDiagPattern`. Qt's hatch
brushes are 8×8 device-pixel tiles pinned to the *widget*, so they crawl across
the band as you scroll and go to mush at any real stripe weight. These are
anchored to content coordinates, so a stripe stays on the same frame of the
scene while the view moves under it. Weight and pitch (`HATCH_WIDTH`,
`HATCH_PITCH`) are tuned against a wide band at high zoom, which is the hard
case: heavier there and you can no longer read the cues you are deleting.

### Saving and building

`Ctrl+S` writes `plans/<EV>_editplan.json` in the contract format, and opening a
scene loads its saved plan back if there is one. `Build & install` saves, then
runs `build_mod.py` with the same flags and defaults the browser helper used —
`--audio --run`, engine `GAME_UE4_26` — and streams its output into the Build
log dock. It is the same build; only the button moved.

Building needs `--content`, `--usmap`, `--game-dir` and `--rezen`.
`StartEditorNative.bat` passes all four. Without them the button explains itself
rather than failing.

## Animation and lighting rows

`_Character` and `_Light` are read **straight from the game assets** when a
scene opens — no re-extraction, and the 139 MB of timeline JSON is untouched.

That is possible because the editor is in the same language as the parsers:
`core/keyframes.py` uses `transforms.Reader2`, the same zenasset reader the
patcher trusts. It costs about 0.1s a scene, writes nothing, and needs only
`--content` and `--usmap`. Without them, there are simply no such rows.

What lands on the timeline:

- **one row per animated actor**, holding its skeletal animation clips as named
  blocks, with every transform and float key on that actor drawn as a tick along
  the bottom of the row;
- **one lighting row**, the union of every float, bool and colour key across all
  the scene's lighting bindings — one scene has 69 bindings and 370 float
  sections, and 69 rows would drown everything else.

Ticks are data on the `Lane`, not `LaneItem`s: a single transform track can
carry 1,300 keys, and blocks nobody clicks would cost hit-testing and memory for
nothing. They cull by binary search and merge when denser than a pixel, so a
fully-baked track reads as a solid strip — which is itself the information, since
there is no gap in it for a join to land in.

One trap, already paid for: **skeletal tracks list their sections under
`AnimationSections`, not `Sections`.** The first version of this read only
`Sections` and every animation clip came back unowned, in a row belonging to
nobody. `test_every_clip_belongs_to_an_actor` exists to keep that fixed.

## Keys

| | |
|---|---|
| `Space` | play / pause |
| `←` `→` | one frame |
| `Shift+←` `→` | one second |
| `Home` `End` | start / end |
| `F` | zoom to fit |
| `+` `−`, `Ctrl+wheel` | zoom (anchored on the pointer) |
| `Shift+wheel` | pan |
| `M` | mute |
| `R` | send the selected cue back to its authored time |
| `Ctrl+D` | split the dialogue row by speaker, and back |

## Where the deferred work lands

The backend items from the brief, and the seam each one attaches to:

- **Flash frame at a join.** Not a UI problem — it is `patcher.py` state
  reconciliation. What changes is the loop: the editor is now in the same
  process as the patcher, so a candidate fix can be tried without a rebuild.
- **Waveforms.** `transport.py` decodes through Qt's FFmpeg backend already.
  Peaks belong in `core/` as a cached array per file; the lane gets a paint
  branch in `timeline_view.py`. The "music continues into the next scene" arrow
  is one more painted glyph at the lane's right edge.
- ~~**Right-click to replace dialogue or music.**~~ **Done for music** —
  `core/music.py`, `ui/music_picker.py`, `patcher.repoint_music` and
  `MUSIC_REPOINTING.md`. It turned out not to want a file dialog at all: the
  trigger names a bank the game already ships and resolves at runtime, so the
  useful gesture is choosing from the 815 banks already there rather than
  importing a file. Dialogue is still the file-dialog case, and
  `QFileDialog.getOpenFileName` — the real Windows shell dialog, returning a
  real path — remains the thing a browser could not do at all.
- **Click a subtitle to edit it.** The subtitle bar is a widget; an inline
  `QLineEdit` over it is small. The constraint is downstream, not here: see
  "the one thing we structurally cannot do" in `WHATS_LEFT.md`.
- ~~**Drag and drop on every track.**~~ **Done for SE, dialogue and music** —
  `core/drag.py`, `core/arrays.py`, and `CUE_DRAGGING.md`. It did turn out to
  be more than a press/move/release on `snap_tick`: those cues share sorted
  Times arrays, so the drag has to be clamped to its neighbours, and the
  silencing pass had to stop breaking the name of a cue being rescued out of a
  cut. The rows deliberately still *not* draggable are the ones where timing
  means something the editor cannot reason about — state triggers and jumps
  (the game progresses through them), streaming volumes (`collapse.py` already
  moves those against a rule it can explain), and bindings and constraints (an
  actor attached to nothing for a few frames). **Reordering** cues within one
  array is not possible yet; the layout suggests it could be, and
  `CUE_DRAGGING.md` records what would have to be measured first.
- **Cut the start or end of a scene, carrying triggers.** Pure `core/edits.py`
  work — a new state transition plus a field on the plan. It does not touch the
  UI beyond a command.
- **Fades, the static overlay, retargeting the next cutscene's trigger.** These
  are investigations into game data, not editor features. Unchanged by this
  port; `SESSION_NOTES_2026-08-08.md` holds what is known.

## Known, carried over deliberately

- **Make safe can leave a non-frame-aligned edge.** It pulls a selection edge
  onto the end of a voice line, which is where the audio actually stops, and
  that is not always a frame boundary. v2 and v3 both did this. The test
  documents the current behaviour rather than the behaviour we might prefer.
- **`lang` is never written to the plan**, so `patcher.py` falls back to `US`.
  The timeline knows it (`audio.lang`); wiring it through is additive and was
  left out so nothing changes behaviour in a port.
- **Preview audio depends on system codecs.** PySide6 ships an FFmpeg backend,
  so the `.ogg` mixes play as-is; if a machine reports "format not supported",
  that is the backend talking and the rest of the editor is unaffected.
