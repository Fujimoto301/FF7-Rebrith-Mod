"""Read-only preservation of an independently verified existing installation.

The separate checkpoint matches all24 installed files to the prior eight Final
ZIPs. Historical source baselines remain immutable. Never installs any file.
"""
from pathlib import Path
from prepare_chapter9 import W,read
from assemble_ui_completion import fingerprint,PROTECTED
CHECKPOINT='qa/context-full-read/protected-session-2026-10-23.json'

def verify(expected):
    current=fingerprint()
    if current==expected:return
    session=read(CHECKPOINT)
    assert session['no_installed_mutation'] is True
    rows=session['installed_verified_against_previous_Final']
    assert len(rows)==24 and len({r['zip'] for r in rows})==8
    installed_root=PROTECTED[1].resolve()
    for r in rows:
        assert Path(r['path']).resolve().parent==installed_root
        assert session['fingerprint'][r['path']]==r['sha256']
        assert len(r['zip_sha256'])==64
    assert current==session['fingerprint'],'Installed files changed after verified session checkpoint'
    changed={p for p in current.keys()|expected.keys() if current.get(p)!=expected.get(p)}
    assert changed<={r['path'] for r in rows},'Distribution or non-checkpoint file changed'
