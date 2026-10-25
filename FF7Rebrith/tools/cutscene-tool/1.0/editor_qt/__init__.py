"""
FF7 Rebirth cutscene editor - native (Qt) front end.

Why this exists, in one paragraph: the browser editors (v2, v3) hit walls that
are not bugs but properties of the platform. A web page cannot open the Windows
file browser and learn a path, it cannot lay out a timeline that does not clip,
its panels are not resizable by the user, and it can only reach patcher.py
through a local HTTP helper that has to be running and that caches hard. This
app is the same logic in the same language as the rest of the tool, in a window
that behaves like a desktop application.

v2 and v3 are untouched and still work; StartEditor.bat still serves them.
"""

__version__ = "0.1.0"
