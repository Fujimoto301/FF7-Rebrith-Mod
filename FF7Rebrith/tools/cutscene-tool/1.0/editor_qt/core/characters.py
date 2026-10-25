"""
Working out who an actor is.

Actors arrive under a lot of names for the same person. The sampled scene calls
Cloud `Cloud`, but a visibility cue calls one of his doubles `cut_PC0000_00b`,
a young Tifa is `TifaAge13`, an illusion is `SephirothIllusion`, and a held
prop is `Aerith_Weapon`. Alongside them sit pure asset IDs - `FA0052_00a`,
`MM0000_00c`, `EB2170` - which are extras and set dressing, not characters.

This module answers one question: given a label and the kind the extraction
assigned it, which *character* is this? The answer is a canonical key. What
colour that key gets is a presentation decision and lives in ui/theme.py, so
there is one place to change a colour and one place to change a name.

The identification is deliberately conservative. A label it cannot place comes
back as `npc`, never as a guess at a main character - a wrong colour on a
double is worse than a neutral one, because the whole point of colouring pins
is to trust them when two versions of the same character are on screen at once.
"""

from __future__ import annotations

import re
from typing import Optional

#: Canonical keys, in the order they are worth reading in a legend.
CHARACTERS = (
    "cloud",
    "barret",
    "tifa",
    "aerith",
    "redxiii",
    "yuffie",
    "caitsith",
    "zack",
    "vincent",
    "cid",
    "sephiroth",
)

#: Everything that is not one of the above.
FEELER = "feeler"
EVENT = "event"
NPC = "npc"

#: Other names the game and the community use for the same character.
ALIASES = {
    "nanaki": "redxiii",
    "red13": "redxiii",
    "redxiiii": "redxiii",
    "caith": "caitsith",
    "caitsit": "caitsith",
    "barrett": "barret",   # the spelling with two Ts is the common one
}

#: Player-character asset IDs, only where they are actually confirmed.
#:
#: `SESSION_NOTES_2026-08-08.md` establishes PC0000 as Cloud and PC0003 as
#: Aerith by direct observation. The rest are not guessed: a double coloured as
#: the wrong character defeats the purpose of colouring it at all. Add to this
#: map as each one is confirmed in game.
PC_IDS = {
    "pc0000": "cloud",
    "pc0003": "aerith",
}

#: `FA0052_00a`, `MM0000_00c`, `EB2170`, `WE9005_00b` - extras and set dressing.
_ASSET_ID = re.compile(r"^[a-z]{2}\d{3,4}")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
#: Trailing variant markers: the `_00a` / `00b` that distinguishes two copies.
_VARIANT = re.compile(r"\d{2}[a-z]?$")

#: `EV_COMON_0010_FA0052_00a` - an actor scoped to one cutscene. The scene
#: prefix says nothing about who it is, so it is stripped and the remainder
#: identified on its own. Anything still unidentified after that is set
#: dressing rather than a person: these names are only ever generated for a
#: specific event.
_EV_SCOPED = re.compile(r"^ev_[a-z0-9]+_\d+_(?P<rest>.+)$", re.IGNORECASE)

#: Words that turn a character's name into somebody else's.
#:
#: `TifaAge13` is Tifa; `TifaPapa` is her father, and `ZackFather` is not Zack.
#: Without this guard the prefix match hands a relative the character's colour,
#: which is exactly the confusion the colours exist to prevent.
_NOT_THEM = (
    "father", "mother", "papa", "mama", "dad", "mum", "mom",
    "sister", "brother", "son", "daughter", "enemy",
)

#: Kinds the extraction uses for things that are not people.
_PROP_KINDS = frozenset({"bg", "we"})


def normalise(label: str) -> str:
    """Lowercased and stripped of punctuation: `Red XIII` -> `redxiii`."""
    return _NON_ALNUM.sub("", (label or "").lower())


def _is_relative(remainder: str) -> bool:
    """Does what follows a character's name make it a different person?"""
    return any(remainder.startswith(word) for word in _NOT_THEM)


def canonical(label: str, kind: Optional[str] = None) -> str:
    """Which character a label refers to, as a key into the colour table.

    Returns a name from `CHARACTERS`, or `FEELER`, `EVENT` or `NPC`.
    """
    scoped = _EV_SCOPED.match((label or "").strip())
    if scoped:
        who = canonical(scoped.group("rest"), kind)
        # unidentified inside an event-scoped name means dressing, not a person
        return EVENT if who == NPC else who

    norm = normalise(label)
    if not norm:
        return NPC

    # a cue name like cut_PC0003_00a: drop the wrapper, then the variant letter
    if norm.startswith("cut"):
        norm = norm[3:]

    if norm in CHARACTERS:
        return norm
    if norm in ALIASES:
        return ALIASES[norm]

    for prefix, who in PC_IDS.items():
        if norm.startswith(prefix):
            return who

    if norm.startswith("feeler"):
        return FEELER

    # TifaAge13, SephirothIllusion, Aerith_Weapon - a character plus a qualifier.
    # Longest first, so a name that is a prefix of another cannot win by luck.
    for who in sorted(CHARACTERS, key=len, reverse=True):
        if norm.startswith(who):
            return NPC if _is_relative(norm[len(who):]) else who
    for alias, who in ALIASES.items():
        if norm.startswith(alias):
            return NPC if _is_relative(norm[len(alias):]) else who

    if _ASSET_ID.match(norm):
        return EVENT
    if kind in _PROP_KINDS:
        return EVENT
    if kind == "other" and _VARIANT.search(norm):
        return EVENT

    return NPC


def is_character(key: str) -> bool:
    """Is this one of the named cast, rather than an extra or a prop?"""
    return key in CHARACTERS


# -- who is speaking a line ---------------------------------------------
#
# A VoiceName ends in a three-letter speaker code: `C1910_MAIN_8000_0100_00_cld`
# is Cloud. The extraction only fills in `actor` when a subtitle line was found
# to match, so roughly a third of the voice cues in a scene - grunts, reactions,
# lines delivered off-screen - arrive anonymous even though the filename says
# exactly who they belong to.
#
# The table below was not guessed. It was counted across the 678 extracted
# scenes that have voice: every line where the extraction DID name an actor
# votes for its code, and a code is listed here only when at least six lines
# agree and at least three quarters of them name the same person. The codes
# that failed that bar are the generic ones - `mma`, `skm`, `mfa` are shared by
# every guard, trooper and tannoy in the game - and they are deliberately
# absent rather than resolved to whichever NPC happened to talk most.
#
# Evidence from the scene in front of you always wins over this table; see
# `lanes.learn_speaker_codes`.

#: Speaker code -> the name the game's own subtitles give that speaker.
VOICE_CODE_SPEAKER = {
    "art": "Aerith", "bgh": "Bugenhagen", "big": "Biggs", "blt": "Barret",
    "brd": "Broden", "cat": "Cait Sith", "chd": "Chadley", "cid": "Cid",
    "cld": "Cloud", "clm": "Claudia", "cln": "Don Corneo", "crn": "Doctor Sheiran",
    "csn": "Cissnei", "dio": "Dio", "dyn": "Dyne", "efa": "Ifalna",
    "elm": "Elmyra", "eln": "Elena", "est": "Esther", "gas": "Garth",
    "ges": "Gus", "grb": "Billy", "gro": "Bill", "gst": "The Gi",
    "hjo": "Hojo", "hyd": "Heidegger", "jny": "Johnny", "joe": "Joe",
    "kdg": "Kid G", "koc": "Kotch", "kpn": "Mayor Kapono", "kre": "Kyrie",
    "ldn": "Rhonda", "leg": "Regina", "lud": "Rude", "mrn": "Marlene",
    "ntk": "Gi Nattak", "plm": "Palmer", "prs": "Priscilla", "rch": "Roche",
    "red": "Red XIII", "ren": "Reno", "rgs": "Glenn", "riv": "Reeve",
    "ruf": "Rufus", "scr": "Scarlet", "sep": "Sephiroth", "sma": "Concierge",
    "snk": "Shinra Middle Manager", "soc": "Scotch", "sum": "Sam", "tif": "Tifa",
    "tsu": "Tseng", "ttv": "Captain Titov", "vin": "Vincent", "yfi": "Yuffie",
    "zax": "Zack", "zng": "Zangan",
}

#: `C1910_MAIN_8000_0100_00_cld` -> `cld`. Empty when the name has no code.
def speaker_code(voice_name: str) -> str:
    tail = (voice_name or "").rsplit("_", 1)[-1].lower()
    return tail if tail.isalpha() and 2 <= len(tail) <= 4 else ""
