"""
Cleaning up game text for display.

Subtitles in the manifest carry the game's own markup, HTML-escaped on the way
in: `&lt;i&gt;pity&lt;/i&gt;` is one word in italics. Unescaping without also
stripping the tags would show the reader `<i>pity</i>`, which is worse than
either, so the two always happen together.

The dash the game uses between clauses (─, U+2500 BOX DRAWINGS LIGHT
HORIZONTAL) is left alone: it is what is on screen in game, and matching it is
sometimes how you find a line.
"""

from __future__ import annotations

import html
import re

_TAG = re.compile(r"<[^>]{0,40}>")
_SPACE = re.compile(r"\s+")


def plain(text: str) -> str:
    """Readable one-line form of a subtitle: entities resolved, markup gone."""
    if not text:
        return ""
    out = html.unescape(text)
    out = _TAG.sub("", out)
    return _SPACE.sub(" ", out).strip()


def fold(text: str) -> str:
    """Lowercased and space-collapsed, for matching a search box against."""
    return _SPACE.sub(" ", plain(text).lower()).strip()


def window_around(caption: str, needle: str, budget: int = 46) -> str:
    """Trim a quoted line so the matched words survive being elided.

    A row in the scene list fits roughly `budget` characters. A long line whose
    match sits near the end would be cut off right before the thing being
    searched for, which is the one part that has to be visible - so the middle
    is dropped instead of the tail.

    The speaker is kept whatever happens: knowing *who* says a line is most of
    why it is being shown.
    """
    if not needle or not caption:
        return caption
    speaker, sep, line = caption.partition(": ")
    if not sep:
        speaker, line = "", caption

    at = line.lower().find(needle.lower())
    if at < 0 or len(caption) <= budget:
        return caption

    room = max(12, budget - len(speaker) - 2)
    if at + len(needle) <= room:
        return caption          # the match already fits; plain elision is fine

    start = max(0, at - room // 3)
    space = line.find(" ", start)
    if 0 <= space < at:
        start = space + 1       # don't start mid-word
    body = ("…" if start > 0 else "") + line[start:]
    return ("%s: %s" % (speaker, body)) if speaker else body
