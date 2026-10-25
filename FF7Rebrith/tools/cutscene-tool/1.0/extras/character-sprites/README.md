# Character sprites (off by default)

The stage preview draws each actor as a **pin** — a vertical line with a head
dot. That is the default and, for most work, the clearer read: pins never
occlude each other and never imply a facing the data does not have.

These two files are the alternative: a sprite atlas of the party rendered from
the 1997 field models, 16 yaw steps each, so the preview can blit the right
facing instead of a dot.

## Turning them on

Copy both files into the folder above this one, beside `CutsceneEditor.bat`:

```
copy chars.png  ..\..
copy chars.json ..\..
```

Restart the editor. `editor_qt/ui/sprites.py` looks for `chars.json` in the tool
root and nowhere else, which is the whole reason they sit in here — present, but
inert until you move them.

## Turning them off again

Delete `chars.png` and `chars.json` from the tool root. The preview falls back
to pins on the next start; `sprites.py` is written to answer "no" to everything
when the atlas is missing, so nothing else changes.

## What they are

Rendered from Final Fantasy VII (1997) field models — Square Enix's character
art, not part of this tool's MIT licence. They are included because the models
are nearly thirty years old and widely circulated, which is a judgement call by
this tool's author rather than a licence grant. If you are redistributing a
fork, that is a call to make for yourself; everything still works without them.

`render_sprites.py`, which built this atlas, is not included: it needs a folder
of the 1997 models to run, and those are not shipped either.
