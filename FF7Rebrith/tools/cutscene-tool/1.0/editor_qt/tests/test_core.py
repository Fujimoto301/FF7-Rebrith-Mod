"""
Tests for the pure model. No Qt, no window, no game.

    py -3 -m unittest discover -s editor_qt/tests -t .

The one that matters is `PlanParity`: it loads every saved plan in ../plans -
including the ones confirmed working in game - reads it into edit state, writes
it back out, and asserts the bytes are unchanged. The plan format is a contract
with patcher.py, and a port is exactly the kind of change that quietly breaks a
contract.
"""

from __future__ import annotations

import glob
import json
import os
import re
import struct
import sys
import tempfile
import unittest
import warnings

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from editor_qt.core import keyframes  # noqa: E402
from editor_qt.core.characters import (  # noqa: E402
    CHARACTERS,
    VOICE_CODE_SPEAKER,
    canonical,
    speaker_code,
)
from editor_qt.core.cues import (  # noqa: E402
    DETACH_CLIPS,
    can_disable,
    cue_descriptor,
    cue_key,
)
from editor_qt.core.edits import (  # noqa: E402
    CueMove,
    CutSpan,
    EditState,
    empty_edits,
    is_untouched,
    keep_ranges,
    normalise_cuts,
    PinSpan,
    pin_spans_for,
    skip_over,
    to_edited,
    to_original,
    with_actor_pin,
    with_cue_moves,
    with_cue_toggled,
    with_cut,
    with_pin_span,
    with_trim,
    without_actor_pin_span,
)
from editor_qt.core import arrays, mixdown  # noqa: E402
from editor_qt.core.collapse import effective, relocatable_cues  # noqa: E402
from editor_qt.core.drag import propose  # noqa: E402
from editor_qt.core.impact import impact_of, make_safe, snap_tick  # noqa: E402
from editor_qt.core.lanes import (  # noqa: E402
    build_lanes,
    can_move,
    clip_family,
    learn_speaker_codes,
    speaker_of,
)
from editor_qt.core.library import SceneLibrary  # noqa: E402
from editor_qt.core.plan import (  # noqa: E402
    from_plan,
    plan_changes_something,
    to_plan,
)
from editor_qt.core.stage import project, stage_at  # noqa: E402
from editor_qt.core.text import fold, plain, window_around  # noqa: E402
from editor_qt.core.timeline import pair_subtitles  # noqa: E402
from editor_qt.core.units import TimeBase, round_half_up  # noqa: E402
from editor_qt.core.waveform import (  # noqa: E402
    Waveform,
    ffmpeg_available,
    load as load_waveform,
)

TIMELINES = os.path.join(TOOL_DIR, "browser_v2", "timelines")
PLANS = os.path.join(TOOL_DIR, "plans")


#: Below this many scanned scenes, "we saw no relocations at all" says nothing
#: about the code - the first few scenes alphabetically are all EV_COMON_* and
#: none of them has a relocatable cue. A 5-scene extraction hit exactly that and
#: failed two invariant tests that are really reporting a thin sample. Above the
#: floor, zero relocations is a genuine regression and still fails.
SAMPLE_FLOOR = 50


def too_thin(checked: int) -> bool:
    return checked < SAMPLE_FLOOR


def have_timelines() -> bool:
    """Is there an extraction to test against?

    `os.path.isdir` is not enough: setup creates `timelines/` before it starts
    filling it, so an interrupted first run leaves an empty folder that passes
    a directory check and then fails every test that opens a scene.
    """
    if not os.path.isdir(TIMELINES):
        return False
    try:
        return any(f.endswith(".json") for f in os.listdir(TIMELINES))
    except OSError:
        return False


class _SkippingLibrary(SceneLibrary):
    """A SceneLibrary that turns "not extracted" into a skip.

    Tests name the scenes they need - EV_FOREE_8510 and friends - and the data
    they need is whatever the user happened to extract. Three states have to be
    told apart:

    * nothing extracted           -> skip, say to run setup
    * extracted, scene missing    -> skip, name the scene
    * extracted, scene present    -> run the test

    Checking only that `timelines/` has *something* in it is not enough, and
    that is not a hypothetical: a `--limit 20` run, or an interrupted setup,
    leaves the first twenty scenes alphabetically and none of the ones these
    tests ask for, which produced 45 errors and 9 failures until this existed.

    Subclassing is what makes it precise. Every test reaches its data through
    `load_cutscene`, so overriding that one method covers all 31 call sites
    and skips exactly the tests whose scene is absent - rather than skipping
    the whole suite because one scene is.
    """

    def load_cutscene(self, ev: str):
        if not os.path.isfile(self.path_for(ev)):
            if not have_timelines():
                raise unittest.SkipTest(
                    "nothing extracted in %s - run firstrun.py first"
                    % TIMELINES)
            raise unittest.SkipTest(
                "%s is not in this extraction" % ev)
        return super().load_cutscene(ev)


def library() -> SceneLibrary:
    """The scene library the tests run against; see _SkippingLibrary."""
    return _SkippingLibrary(
        TIMELINES, os.path.join(TOOL_DIR, "browser_v2", "manifest.json"))


class Units(unittest.TestCase):
    def setUp(self) -> None:
        self.t = TimeBase(24000, 30)

    def test_frame_size(self) -> None:
        self.assertEqual(self.t.ticks_per_frame, 800)

    def test_round_half_up_matches_javascript(self) -> None:
        # Python's round() gives 2 for both of these; JavaScript gives 3 and 2.
        self.assertEqual(round_half_up(2.5), 3)
        self.assertEqual(round_half_up(1.5), 2)
        self.assertEqual(round_half_up(-2.5), -2)

    def test_snapping(self) -> None:
        self.assertEqual(self.t.snap_to_frame(1199), 800)   # 1.499 frames
        self.assertEqual(self.t.snap_to_frame(1300), 1600)  # 1.625 frames
        # exactly half a frame goes up, as it did in JavaScript
        self.assertEqual(self.t.snap_to_frame(1200), 1600)
        self.assertEqual(self.t.floor_to_frame(1199), 800)
        self.assertEqual(self.t.ceil_to_frame(801), 1600)
        self.assertTrue(self.t.is_frame_aligned(96000))
        self.assertFalse(self.t.is_frame_aligned(96001))

    def test_format(self) -> None:
        self.assertEqual(self.t.format(0), "0:00.00")
        self.assertEqual(self.t.format(24000 * 65.25), "1:05.25")
        self.assertEqual(self.t.describe_span(100000), "4.17s · 125f")


class Edits(unittest.TestCase):
    def test_merges_touching_spans(self) -> None:
        cuts = normalise_cuts([CutSpan(200, 300), CutSpan(0, 100), CutSpan(100, 150)])
        self.assertEqual([(c.a, c.b) for c in cuts], [(0, 150), (200, 300)])

    def test_drops_empty_spans(self) -> None:
        self.assertEqual(normalise_cuts([CutSpan(50, 50)]), ())

    def test_keep_ranges_partition_the_timeline(self) -> None:
        s = with_cut(empty_edits(), CutSpan(100, 200))
        self.assertEqual(keep_ranges(s, 500), [[0, 100], [200, 500]])

    def test_keep_ranges_with_a_cut_at_the_head(self) -> None:
        s = with_cut(empty_edits(), CutSpan(0, 200))
        self.assertEqual(keep_ranges(s, 500), [[200, 500]])

    def test_to_edited_shifts_and_removes(self) -> None:
        s = with_cut(empty_edits(), CutSpan(100, 200))
        self.assertEqual(to_edited(s, 50), 50)
        self.assertEqual(to_edited(s, 300), 200)
        self.assertIsNone(to_edited(s, 150))

    def test_to_original_inverts_to_edited(self) -> None:
        s = with_cut(with_cut(empty_edits(), CutSpan(100, 200)), CutSpan(300, 400))
        for t in (0, 50, 99, 200, 250, 299, 400, 450, 500):
            self.assertEqual(to_original(s, to_edited(s, t)), t, t)

    def test_to_original_never_lands_inside_a_cut(self) -> None:
        """Adding up every cut regardless is the bug this guards: an edited
        tick ahead of a cut must not have that cut's length added."""
        s = with_cut(with_cut(empty_edits(), CutSpan(100, 200)), CutSpan(300, 400))
        for e in range(0, 300):
            got = to_original(s, e)
            self.assertFalse(any(c.a <= got < c.b for c in s.cuts),
                             "edited %d -> original %d, inside a cut" % (e, got))

    def test_pinning_an_actor_clears_the_opposite_pin(self) -> None:
        s = with_actor_pin(empty_edits(), "Aerith", "show")
        s = with_actor_pin(s, "Aerith", "hide")
        self.assertEqual(s.force_visible, ())
        self.assertEqual(s.force_hidden, ("Aerith",))

    def test_edit_state_is_immutable(self) -> None:
        s = empty_edits()
        with_cut(s, CutSpan(0, 100))
        self.assertEqual(s.cuts, ())


class SkipOverCuts(unittest.TestCase):
    """Playback previews the edit, so the playhead steps over removed spans."""

    def test_a_tick_outside_every_cut_is_left_alone(self) -> None:
        s = with_cut(empty_edits(), CutSpan(100, 200))
        self.assertEqual(skip_over(s, 50, 500), 50)
        self.assertEqual(skip_over(s, 300, 500), 300)

    def test_a_tick_inside_a_cut_lands_on_its_far_edge(self) -> None:
        s = with_cut(empty_edits(), CutSpan(100, 200))
        self.assertEqual(skip_over(s, 100, 500), 200)
        self.assertEqual(skip_over(s, 150, 500), 200)

    def test_the_far_edge_itself_is_kept_footage(self) -> None:
        """Spans are half-open, so landing on `b` is landing on what survives."""
        s = with_cut(empty_edits(), CutSpan(100, 200))
        self.assertEqual(skip_over(s, 200, 500), 200)

    def test_one_pass_clears_back_to_back_cuts(self) -> None:
        """Touching spans merge, so no skip can land inside another cut."""
        s = with_cut(with_cut(empty_edits(), CutSpan(100, 200)), CutSpan(200, 400))
        self.assertEqual(skip_over(s, 150, 500), 400)

    def test_a_gap_between_two_cuts_survives(self) -> None:
        s = with_cut(with_cut(empty_edits(), CutSpan(100, 200)), CutSpan(300, 400))
        self.assertEqual(skip_over(s, 150, 500), 200)
        self.assertEqual(skip_over(s, 250, 500), 250)
        self.assertEqual(skip_over(s, 350, 500), 400)

    def test_a_cut_running_to_the_end_clamps_to_the_end(self) -> None:
        s = with_cut(empty_edits(), CutSpan(400, 600))
        self.assertEqual(skip_over(s, 450, 500), 500)

    def test_an_untouched_scene_never_moves_the_playhead(self) -> None:
        s = empty_edits()
        self.assertEqual(skip_over(s, 123.5, 500), 123.5)


class Text(unittest.TestCase):
    def test_strips_the_games_escaped_markup(self) -> None:
        self.assertEqual(
            plain("What's &lt;i&gt;with&lt;/i&gt; them?"), "What's with them?"
        )

    def test_keeps_the_games_own_dash(self) -> None:
        self.assertIn("─", plain("not a party─it's a pity"))

    def test_fold_is_matchable(self) -> None:
        self.assertEqual(fold("  What's  &lt;i&gt;WITH&lt;/i&gt; them? "),
                         "what's with them?")

    def test_window_keeps_a_late_match_visible(self) -> None:
        line = "Yuffie: Some know me as the world's greatest materia hunter."
        got = window_around(line, "materia", budget=40)
        self.assertTrue(got.startswith("Yuffie: "), got)
        self.assertIn("materia", got)
        self.assertLess(len(got), len(line))

    def test_window_leaves_a_short_line_alone(self) -> None:
        line = "Cloud: Aerith... Wake up."
        self.assertEqual(window_around(line, "wake up", budget=40), line)

    def test_window_leaves_an_early_match_alone(self) -> None:
        line = "Barret: Myrna! Wake up, baby... Wake up! Don't do this to me."
        self.assertEqual(window_around(line, "Myrna", budget=40), line)


class SpeakerCodes(unittest.TestCase):
    """The three letters on the end of a VoiceName."""

    def test_reads_the_code_off_a_voice_name(self) -> None:
        self.assertEqual(speaker_code("C1910_MAIN_8000_0100_00_cld"), "cld")
        self.assertEqual(speaker_code("C2410_MAIN_0100_0100_09_snk"), "snk")

    def test_a_name_with_no_code_gives_nothing(self) -> None:
        for name in ("", "C1910_MAIN_8000_0100_00", "voice_0001"):
            self.assertEqual(speaker_code(name), "")

    def test_the_table_names_the_cast(self) -> None:
        for code, who in (("cld", "Cloud"), ("blt", "Barret"), ("art", "Aerith"),
                          ("tif", "Tifa"), ("yfi", "Yuffie"), ("red", "Red XIII")):
            self.assertEqual(VOICE_CODE_SPEAKER[code], who)

    def test_the_table_resolves_to_the_colours(self) -> None:
        """A code that names one of the cast has to reach their palette entry,
        or a split row would be headed Cloud and coloured like an extra."""
        for code in ("cld", "blt", "art", "tif", "yfi", "red", "sep", "cid",
                     "vin", "zax", "cat"):
            self.assertIn(canonical(VOICE_CODE_SPEAKER[code]), CHARACTERS)


class Characters(unittest.TestCase):
    def test_the_named_cast(self) -> None:
        for label, want in (
            ("Cloud", "cloud"),
            ("Barret", "barret"),
            ("Tifa", "tifa"),
            ("Aerith", "aerith"),
            ("RedXIII", "redxiii"),
            ("Yuffie", "yuffie"),
            ("CaitSith", "caitsith"),
            ("Sephiroth", "sephiroth"),
            ("Vincent", "vincent"),
            ("Cid", "cid"),
            ("Zack", "zack"),
        ):
            self.assertEqual(canonical(label, "pc"), want)

    def test_spelling_and_spacing_do_not_matter(self) -> None:
        self.assertEqual(canonical("Red XIII"), "redxiii")
        self.assertEqual(canonical("Barrett"), "barret")   # the two-T spelling
        self.assertEqual(canonical("Nanaki"), "redxiii")
        self.assertEqual(canonical("cait sith"), "caitsith")

    def test_qualified_names_resolve_to_the_character(self) -> None:
        self.assertEqual(canonical("TifaAge13", "np"), "tifa")
        self.assertEqual(canonical("SephirothIllusion", "we"), "sephiroth")
        self.assertEqual(canonical("Aerith_Weapon"), "aerith")

    def test_confirmed_doubles_only(self) -> None:
        """PC0000 and PC0003 are documented; the rest must not be guessed."""
        self.assertEqual(canonical("cut_PC0000_00b"), "cloud")
        self.assertEqual(canonical("cut_PC0003_00a"), "aerith")
        self.assertEqual(canonical("cut_PC0007_00a"), "event")

    def test_feelers(self) -> None:
        self.assertEqual(canonical("Feeler", "en"), "feeler")

    def test_asset_ids_are_event_dressing(self) -> None:
        for label in ("FA0052_00a", "MM0000_00c", "MW0000_00b", "EB2170",
                      "WE9005_00b", "EN0000_00"):
            self.assertEqual(canonical(label, "other"), "event", label)

    def test_props_are_event_dressing(self) -> None:
        self.assertEqual(canonical("Chair", "bg"), "event")
        self.assertEqual(canonical("Trolley", "bg"), "event")

    def test_everyone_else_is_an_npc(self) -> None:
        for label in ("Hojo", "Tseng", "Biggs", "Johnny", "SecuritySoldier"):
            self.assertEqual(canonical(label, "np"), "npc", label)

    def test_an_unknown_name_never_guesses_a_main_character(self) -> None:
        self.assertEqual(canonical("SomeoneEntirelyNew", "np"), "npc")

    def test_a_relative_is_not_the_character(self) -> None:
        self.assertEqual(canonical("ZackFather", "np"), "npc")
        self.assertEqual(canonical("ZackMother", "np"), "npc")
        self.assertEqual(canonical("TifaPapa", "np"), "npc")
        # but an age qualifier still is
        self.assertEqual(canonical("TifaAge13", "np"), "tifa")
        self.assertEqual(canonical("CloudAge14", "np"), "cloud")

    def test_event_scoped_names_resolve_through_the_prefix(self) -> None:
        self.assertEqual(canonical("EV_COMON_0010_FA0052_00a"), "event")
        self.assertEqual(canonical("EV_COMON_0010_PC0000_00"), "cloud")
        # unidentified inside an event name is dressing, not a magenta NPC
        self.assertEqual(canonical("EV_FOREE_8514_GA_Blood"), "event")


#: A staged copy of a real scene's assets, left behind by an earlier build.
STAGED = os.path.join(TOOL_DIR, "build", "staged", "End", "Content")
USMAP = os.path.join(TOOL_DIR, "Mappings.usmap")


@unittest.skipUnless(os.path.isdir(STAGED) and os.path.isfile(USMAP),
                     "no staged assets + Mappings.usmap to read")
class Keyframes(unittest.TestCase):
    """Reads `_Character` and `_Light` the way the editor does at scene open."""

    EV = "EV_NIBLE_0110"
    AREA = "8700-NIBLE"

    @classmethod
    def setUpClass(cls) -> None:
        # zenasset reads a package with `open(path,'rb').read()` and lets the
        # handle fall out of scope. Harmless, and not ours to change here.
        warnings.simplefilter("ignore", ResourceWarning)
        cls.keys = keyframes.load(STAGED, USMAP, cls.AREA, cls.EV)

    def test_reads_something(self) -> None:
        self.assertIsNotNone(self.keys)
        self.assertFalse(self.keys.empty)

    def test_every_clip_belongs_to_an_actor(self) -> None:
        """Skeletal tracks list sections under `AnimationSections`, not
        `Sections` — miss that and every clip is unowned."""
        self.assertTrue(self.keys.clips)
        for c in self.keys.clips:
            self.assertNotEqual(c.actor, "?", "clip %s has no binding" % c.clip)
            self.assertNotIn(self.EV, c.actor, "scene prefix should be stripped")

    def test_zero_length_clips_are_dropped(self) -> None:
        for c in self.keys.clips:
            self.assertGreater(c.end, c.start)

    def test_key_ticks_are_sorted_and_unique(self) -> None:
        for actor, ticks in self.keys.actor_keys.items():
            self.assertEqual(list(ticks), sorted(set(ticks)), actor)
        self.assertEqual(list(self.keys.light_keys), sorted(set(self.keys.light_keys)))

    def test_keys_land_inside_the_scene(self) -> None:
        lib = library()
        lib.load()
        cs = lib.load_cutscene(self.EV)
        for actor, ticks in self.keys.actor_keys.items():
            self.assertGreaterEqual(min(ticks), 0, actor)
            self.assertLessEqual(max(ticks), cs.total * 1.01, actor)

    def test_builds_lanes(self) -> None:
        lanes = keyframes.build_key_lanes(self.keys)
        ids = [ln.id for ln in lanes]
        self.assertTrue(any(i.startswith("anim:") for i in ids))
        self.assertNotIn("anim:?", ids)
        for ln in lanes:
            self.assertTrue(ln.items or ln.ticks, "%s is an empty row" % ln.id)

    def test_missing_paths_are_not_an_error(self) -> None:
        self.assertIsNone(keyframes.load(None, USMAP, self.AREA, self.EV))
        self.assertIsNone(keyframes.load(STAGED, USMAP, self.AREA, "EV_DOES_NOT_EXIST"))
        self.assertEqual(keyframes.build_key_lanes(None), [])


class Waveforms(unittest.TestCase):
    def setUp(self) -> None:
        # a synthetic envelope: silent, then loud for one second
        self.wave = Waveform(peaks=[0] * 100 + [200] * 100 + [0] * 100,
                             rate=100, duration=3.0)

    def test_slice_covers_the_window(self) -> None:
        self.assertEqual(len(self.wave.slice_for(0, 3, 60)), 60)

    def test_a_transient_survives_being_zoomed_out(self) -> None:
        """Reduce by max, not by sampling - the whole point of the row."""
        spike = Waveform(peaks=[0] * 999 + [255], rate=100, duration=10.0)
        self.assertEqual(max(spike.slice_for(0, 10, 20)), 255)

    def test_the_loud_second_lands_in_the_middle(self) -> None:
        cols = self.wave.slice_for(0, 3, 30)
        self.assertEqual(max(cols[:10]), 0)
        self.assertEqual(max(cols[10:20]), 200)
        self.assertEqual(max(cols[20:]), 0)

    def test_out_of_range_windows_are_silent_not_an_error(self) -> None:
        self.assertEqual(self.wave.slice_for(-5, -1, 10), [0] * 10)
        self.assertEqual(self.wave.slice_for(90, 95, 10), [0] * 10)

    def test_empty_waveform_slices_to_nothing(self) -> None:
        self.assertEqual(Waveform(peaks=[], rate=100, duration=0).slice_for(0, 1, 10), [])

    @unittest.skipUnless(ffmpeg_available(), "ffmpeg not on PATH")
    @unittest.skipUnless(have_timelines(), "no extracted timelines")
    def test_decodes_a_real_mix(self) -> None:
        lib = library()
        lib.load()
        cs = lib.load_cutscene("EV_FOREE_8510")
        path = lib.audio_path(cs)
        if not path:
            self.skipTest("no rendered mix for that scene")
        wave = load_waveform(path, cache_dir=tempfile.mkdtemp())
        self.assertIsNotNone(wave)
        self.assertGreater(len(wave.peaks), 0)
        self.assertLessEqual(max(wave.peaks), 255)
        # the envelope should agree with what the scene says it is
        self.assertAlmostEqual(wave.duration, cs.audio.duration, delta=1.0)


class CueColours(unittest.TestCase):
    def test_families_are_assigned_not_shared(self) -> None:
        self.assertEqual(clip_family("Se"), "audio")
        self.assertEqual(clip_family("SendStateTrigger"), "flow")
        self.assertEqual(clip_family("DirLightModify"), "light")
        self.assertEqual(clip_family("EnvLightModify"), "light")

    def test_unknown_clips_get_their_own_colour(self) -> None:
        self.assertEqual(clip_family("SomethingNewInAPatch"), "evt")
        self.assertNotEqual(clip_family("SomethingNewInAPatch"), clip_family("Se"))


@unittest.skipUnless(have_timelines(), "no extracted timelines")
class Search(unittest.TestCase):
    """Search behaviour, which only means anything over a full extraction.

    These assert on volume - more hits than `RESOLVE_LIMIT`, a preview on over
    half the library - and on particular scenes being findable. Twenty scenes
    from an interrupted setup satisfies `have_timelines()` and then fails six
    of them, so the guard has to be about how much was extracted, not whether
    anything was.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = library()
        cls.lib.load()
        if len(cls.lib.entries) <= SceneLibrary.RESOLVE_LIMIT:
            raise unittest.SkipTest(
                "search needs a full extraction; this one has %d scenes"
                % len(cls.lib.entries))

    def test_empty_query_returns_everything(self) -> None:
        self.assertEqual(len(self.lib.search("")), len(self.lib.entries))

    def test_finds_a_scene_by_a_spoken_line(self) -> None:
        hits = self.lib.search("Wake up")
        names = [m.entry.ev for m in hits]
        self.assertIn("EV_FOREE_7500", names)
        match = next(m for m in hits if m.entry.ev == "EV_FOREE_7500")
        self.assertTrue(match.hit, "should report the line that matched")
        self.assertIn("wake up", match.hit.lower())

    def test_quoted_line_comes_from_the_subtitle_not_the_blob(self) -> None:
        """The manifest runs cast names into dialogue; the line must not."""
        match = next(m for m in self.lib.search("Myrna") if m.entry.ev == "EV_FOREE_3440")
        actor, _, line = match.hit.partition(": ")
        self.assertEqual(actor, "Barret")
        self.assertTrue(line.startswith("Myrna"), line)

    def test_falls_back_to_the_opening_line_past_the_resolve_limit(self) -> None:
        hits = self.lib.search("a")   # matches almost everything
        self.assertGreater(len(hits), self.lib.RESOLVE_LIMIT)
        quoted = sum(1 for m in hits if m.hit)
        self.assertLessEqual(quoted, self.lib.RESOLVE_LIMIT)
        for m in hits:
            self.assertTrue(m.caption == m.entry.preview or m.hit)

    def test_name_matches_do_not_claim_a_dialogue_hit(self) -> None:
        match = next(m for m in self.lib.search("EV_FOREE_7500"))
        self.assertEqual(match.hit, "")
        # falls back to the scene's opening line
        self.assertEqual(match.caption, match.entry.preview)

    def test_search_is_case_and_markup_insensitive(self) -> None:
        self.assertTrue(self.lib.search("WAKE UP"))

    def test_most_scenes_have_an_opening_line(self) -> None:
        with_preview = [e for e in self.lib.entries if e.preview]
        self.assertGreater(len(with_preview), len(self.lib.entries) // 2)


@unittest.skipUnless(have_timelines(), "no extracted timelines")
class RealScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = library()
        cls.lib.load()
        cls.cs = cls.lib.load_cutscene("EV_FOREE_8510")

    def test_reads_the_clock_from_the_scene(self) -> None:
        self.assertEqual(self.cs.time.ticks_per_second, 24000)
        self.assertEqual(self.cs.time.ticks_per_frame, 800)
        self.assertGreater(self.cs.total, 0)

    def test_camera_cuts_are_numbered_in_time_order(self) -> None:
        self.assertEqual(self.cs.cuts[0].name, "C01")
        starts = [c.range[0] for c in self.cs.cuts]
        self.assertEqual(starts, sorted(starts))

    def test_block_labels_carry_no_markup(self) -> None:
        """A block reading `<i>Cloud</i>:` is worse than either form."""
        for lane in build_lanes(self.cs, empty_edits()):
            for item in lane.items:
                self.assertNotIn("<i>", item.name)
                self.assertNotIn("&lt;", item.name)

    def test_a_named_cue_can_be_disabled(self) -> None:
        lanes = {ln.id: ln for ln in build_lanes(self.cs, empty_edits())}
        se = lanes.get("cue:Se")
        if not (se and se.items):
            self.skipTest("scene has no SE cues")
        self.assertTrue(can_disable(se.items[0]).ok)

    def test_a_state_trigger_is_always_refused(self) -> None:
        """It refuses as *unnamed*, not *protected*, and that is not a bug.

        SendStateTrigger carries only a TriggerID — none of CUE_NAME_FIELDS —
        so `cue_descriptor` returns nothing and the PROTECTED_CLIPS check is
        never reached. Either way the editor will not switch it off, which is
        what stands between an edit and a softlock. v2 and v3 behaved the same.
        """
        lanes = {ln.id: ln for ln in build_lanes(self.cs, empty_edits())}
        trig = lanes.get("cue:SendStateTrigger")
        if not (trig and trig.items):
            self.skipTest("scene has no state triggers")
        v = can_disable(trig.items[0])
        self.assertFalse(v.ok)
        self.assertIn(v.reason, ("unnamed", "protected"))

    def test_a_constraint_can_be_switched_off(self) -> None:
        """Not by breaking its name — by turning the attach into a detach.

        EV_CORLE_0100 spent two builds proving the difference: six flower-lei
        constraints renamed to `CUT_ORLE_0100_FA0418_00a`.., the patched asset
        carrying every one, and the leis still on the characters in game.
        """
        lanes = {ln.id: ln for ln in build_lanes(self.cs, empty_edits())}
        row = lanes.get("cue:Constraint")
        if not (row and row.items):
            self.skipTest("scene has no constraints")
        v = can_disable(row.items[0])
        self.assertTrue(v.ok)
        self.assertIn(v.descriptor["clip"], DETACH_CLIPS)

    def test_a_show_hide_cue_is_still_offered(self) -> None:
        """The mechanism is per clip, not per field: `ActorDraw` renaming works."""
        lanes = {ln.id: ln for ln in build_lanes(self.cs, empty_edits())}
        row = lanes.get("cue:ActorDraw")
        if not (row and row.items):
            self.skipTest("scene has no show/hide cues")
        self.assertTrue(can_disable(row.items[0]).ok)

    def test_lanes_cover_the_scene(self) -> None:
        lanes = build_lanes(self.cs, empty_edits())
        ids = [ln.id for ln in lanes]
        self.assertIn("camera", ids)
        self.assertIn("shots", ids)
        self.assertEqual(len(lanes[0].items), len(self.cs.cuts))

    def test_lane_items_stay_inside_the_scene(self) -> None:
        for lane in build_lanes(self.cs, empty_edits()):
            for item in lane.items:
                self.assertGreaterEqual(item.range[1], item.range[0])

    def test_make_safe_never_splits_a_voice_line(self) -> None:
        ticks = self.cs.time.ticks_per_second
        safe = make_safe(self.cs, 90000, 200000)
        if safe is None:
            self.skipTest("no safe cut in that region")
        for v in self.cs.voice:
            s = v.tick
            e = v.tick + (v.duration or 1) * ticks
            straddles = (s < safe.a < e) or (s < safe.b < e)
            self.assertFalse(straddles, "cut splits %s" % v.name)

    def test_snap_prefers_a_camera_cut_boundary(self) -> None:
        edge = self.cs.cuts[1].range[0]
        got = snap_tick(self.cs, [], edge + 37, tolerance=2000)
        self.assertEqual(got, edge)

    def test_impact_counts_whole_camera_cuts(self) -> None:
        c = self.cs.cuts[1]
        self.assertGreaterEqual(impact_of(self.cs, c.range[0], c.range[1]).cuts, 1)

    def test_stage_projection_agrees_with_the_frame_test(self) -> None:
        frame = stage_at(self.cs.scene, 300000)
        self.assertIsNotNone(frame)
        self.assertIsNotNone(frame.cam)
        for _actor, pos, pr in frame.points:
            self.assertEqual(pr, project(frame.cam, pos))

    def test_every_timeline_loads(self) -> None:
        """The whole corpus, so a shape we have never seen is a test failure."""
        bad = []
        for entry in self.lib.entries:
            try:
                cs = self.lib.load_cutscene(entry.ev)
                build_lanes(cs, empty_edits())
            except Exception as exc:  # pragma: no cover - reported below
                bad.append("%s: %s" % (entry.ev, exc))
        self.assertEqual(bad, [], "%d of %d failed" % (len(bad), len(self.lib.entries)))

    # -- dialogue split by speaker --------------------------------------

    def _voice_lanes(self, split: bool):
        return [ln for ln in build_lanes(self.cs, empty_edits(), split)
                if ln.kind == "voice"]

    def test_splitting_dialogue_keeps_every_line(self) -> None:
        one = self._voice_lanes(False)
        if not one:
            self.skipTest("scene has no voice")
        many = self._voice_lanes(True)
        learned = learn_speaker_codes(self.cs)
        # a one-speaker scene splits into one row, and that is correct
        self.assertEqual(len(many), len({speaker_of(v, learned) for v in self.cs.voice}))
        self.assertEqual(sum(len(ln.items) for ln in many), len(one[0].items))
        self.assertEqual(len({ln.id for ln in many}), len(many))

    def test_a_split_row_holds_one_speaker(self) -> None:
        """Which is the point: two blocks on a row cannot be two people."""
        learned = learn_speaker_codes(self.cs)
        by_name = {v.name: v for v in self.cs.voice}
        for lane in self._voice_lanes(True):
            who = {speaker_of(by_name[it.voice.name], learned)
                   for it in lane.items if it.voice}
            self.assertEqual(len(who), 1, lane.label)
            self.assertTrue(lane.label.startswith(who.pop()))

    def test_split_rows_no_longer_bury_a_line(self) -> None:
        """An overlap on the combined row is what makes a block unclickable."""
        def overlaps(lane) -> int:
            items = sorted(lane.items, key=lambda i: i.range[0])
            return sum(1 for a, b in zip(items, items[1:]) if b.range[0] < a.range[1])

        one = self._voice_lanes(False)
        if not one or not overlaps(one[0]):
            self.skipTest("scene has no overlapping dialogue")
        self.assertLess(sum(overlaps(ln) for ln in self._voice_lanes(True)),
                        overlaps(one[0]))

    def test_an_unlabelled_line_is_named_by_its_code(self) -> None:
        """The extraction names a line only where a subtitle matched; the
        VoiceName says who is speaking either way."""
        learned = learn_speaker_codes(self.cs)
        anon = [v for v in self.cs.voice if not v.actor and speaker_code(v.name)]
        if not anon:
            self.skipTest("every line in this scene is attributed")
        named = [v for v in anon if speaker_of(v, learned) != speaker_code(v.name)]
        self.assertTrue(named, "no anonymous line could be attributed")

    def test_a_split_row_is_still_a_voice_row(self) -> None:
        """Trimming, dragging and the lip-sync follow all read `kind`."""
        for lane in self._voice_lanes(True):
            self.assertFalse(lane.range_row)
            for item in lane.items:
                self.assertIsNotNone(item.voice)
                self.assertTrue(can_move(lane, item))

    def test_every_timeline_splits(self) -> None:
        """Same corpus sweep, with the dialogue rows fanned out."""
        bad = []
        for entry in self.lib.entries:
            try:
                cs = self.lib.load_cutscene(entry.ev)
                lanes = build_lanes(cs, empty_edits(), True)
                ids = [ln.id for ln in lanes]
                assert len(ids) == len(set(ids)), "duplicate row id"
                assert sum(len(ln.items) for ln in lanes if ln.kind == "voice") \
                    == len(cs.voice), "lost a line"
            except Exception as exc:  # pragma: no cover - reported below
                bad.append("%s: %s" % (entry.ev, exc))
        self.assertEqual(bad, [], "%d of %d failed" % (len(bad), len(self.lib.entries)))


@unittest.skipUnless(os.path.isdir(PLANS), "no saved plans")
class CarryCuesAcrossACut(unittest.TestCase):
    """Fades and level streaming keep their distance from the end - collapse.py.

    EV_FOREE_7500 is the scene this was written for: it ends on a fade to black
    at 2344000 and preloads the next scene's lighting and sky at 2236000 and
    2368000, all inside the last six seconds.
    """

    EV = "EV_FOREE_7500"
    TOTAL = 2380000
    PRELOAD_A = 2236000     # basement lighting
    FADE = 2344000
    PRELOAD_B = 2368000     # sky

    def scene(self):
        lib = library()
        if not os.path.isfile(lib.path_for(self.EV)):
            self.skipTest("%s not extracted" % self.EV)
        return lib.load_cutscene(self.EV)

    def test_the_scene_still_has_the_cues_this_rests_on(self) -> None:
        cs = self.scene()
        found = {(e["seq"], e["clip"], e["tick"]) for e in relocatable_cues(cs)}
        self.assertIn(("CutEvent", "Fade", self.FADE), found)
        self.assertIn(("Light", "SwitchStreamingVolume", self.PRELOAD_A), found)
        self.assertIn(("Light", "SwitchStreamingVolume", self.PRELOAD_B), found)

    def test_each_cue_keeps_its_distance_from_the_end(self) -> None:
        cs = self.scene()
        new_end = 1880000
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(new_end, cs.total),)))
        got = {r.tick: r.new_tick for r in plan.relocations}
        self.assertEqual(len(got), 3)
        for tick in (self.PRELOAD_A, self.FADE, self.PRELOAD_B):
            self.assertEqual(got[tick], new_end - (cs.total - tick),
                             "%d did not keep its distance from the end" % tick)
        # the fade still finishes exactly on the last frame: 45 frames at
        # 800 ticks each is 36000, and it sat 36000 before the old end
        self.assertEqual(got[self.FADE] + 36000, new_end)

    def test_the_cut_itself_is_never_touched(self) -> None:
        """Nothing is appended and nothing you cut is kept."""
        cs = self.scene()
        state = EditState(cuts=(CutSpan(1880000, cs.total),))
        applied, _plan = effective(cs, state)
        self.assertEqual(applied.cuts, state.cuts)
        self.assertEqual(keep_ranges(applied, cs.total), [[0, 1880000]])

    def test_spacing_between_the_streaming_cues_is_preserved(self) -> None:
        """A Preload has to keep its head start over the switch that uses it."""
        cs = self.scene()
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(1880000, cs.total),)))
        got = {r.tick: r.new_tick for r in plan.relocations}
        self.assertEqual(got[self.PRELOAD_B] - got[self.PRELOAD_A],
                         self.PRELOAD_B - self.PRELOAD_A)
        self.assertEqual(got[self.FADE] - got[self.PRELOAD_A],
                         self.FADE - self.PRELOAD_A)

    def test_everything_lands_left_of_the_join(self) -> None:
        cs = self.scene()
        for at in (1880000, 1200000, 400000):
            _applied, plan = effective(cs, EditState(cuts=(CutSpan(at, cs.total),)))
            for r in plan.relocations:
                self.assertLessEqual(r.new_tick, at, "%s past the join" % r.label)
                self.assertGreaterEqual(r.new_tick, 0)

    def test_an_earlier_cut_is_accounted_for(self) -> None:
        """`new_tick` is on the EDITED timeline; `at_tick` is where to draw it."""
        cs = self.scene()
        state = EditState(cuts=(CutSpan(400000, 600000), CutSpan(1880000, cs.total)))
        _applied, plan = effective(cs, state)
        new_end = 1880000 - 200000
        for r in plan.relocations:
            self.assertEqual(r.new_tick, new_end - (cs.total - r.tick))
            self.assertEqual(r.at_tick - r.new_tick, 200000)

    def test_a_cue_landing_ahead_of_an_earlier_cut_is_drawn_there(self) -> None:
        """EV_FOREE_8510 with two cuts: the streaming cue lands BEFORE the
        first cut, so its drawn position must be in surviving footage, not
        inside that cut's red band."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8510")):
            self.skipTest("EV_FOREE_8510 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8510")
        cuts = (CutSpan(432000, 504000), CutSpan(600000, cs.total))
        _applied, plan = effective(cs, EditState(cuts=cuts))
        self.assertTrue(plan.relocations)
        for r in plan.relocations:
            self.assertFalse(any(c.a <= r.at_tick < c.b for c in cuts),
                             "%s drawn inside a cut" % r.label)
            # and it still keeps its distance from the new end
            edited = cs.total - sum(c.b - c.a for c in cuts)
            self.assertEqual(edited - r.new_tick, cs.total - r.tick)

    def test_no_relocation_is_ever_drawn_inside_a_cut(self) -> None:
        lib = library()
        paths = sorted(glob.glob(os.path.join(TIMELINES, "*.json")))
        if not paths:
            self.skipTest("no timelines extracted")
        checked = scanned = 0
        for path in paths[:300]:
            ev = os.path.splitext(os.path.basename(path))[0]
            try:
                cs = lib.load_cutscene(ev)
            except Exception:
                continue
            if cs.total <= 0:
                continue
            scanned += 1
            t = cs.time
            cuts = (CutSpan(t.snap_to_frame(cs.total * 0.35),
                            t.snap_to_frame(cs.total * 0.45)),
                    CutSpan(t.snap_to_frame(cs.total * 0.5), cs.total))
            _applied, plan = effective(cs, EditState(cuts=cuts))
            for r in plan.relocations:
                self.assertFalse(any(c.a <= r.at_tick < c.b for c in cuts),
                                 "%s in %s drawn inside a cut" % (r.label, ev))
                checked += 1
        if not checked and too_thin(scanned):
            self.skipTest(
                "only %d scenes extracted and none produced a relocation - "
                "extract more to exercise this" % scanned)
        self.assertGreater(checked, 0)

    def test_a_middle_cut_fires_its_cues_at_the_join(self) -> None:
        """An interior cut has no end to measure from - the scene carries on
        past it - so a cue it swallows fires where playback resumes.

        This replaces `test_a_middle_cut_measures_from_that_cut`, which asserted
        the bug: measuring from the end of the *cut* is only the same as
        measuring from the end of the *scene* when the cut reaches the end, and
        every scene the feature had ever run on was cut that way. On an interior
        cut the old rule dropped a cue back by up to the whole length of the cut
        - 26s on EV_FOREE_8514 - into footage that plays long before it.
        """
        cs = self.scene()
        join = 2300000
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(join, 2360000),)))
        fades = [r for r in plan.relocations if r.clip == "Fade"]
        self.assertEqual(len(fades), 1)
        self.assertEqual(fades[0].new_tick, join)

    def test_a_middle_cut_never_places_a_cue_before_its_join(self) -> None:
        """The failure mode the rule above exists to stop, stated directly."""
        cs = self.scene()
        for a, b in ((1000000, 1200000), (1500000, 2300000), (200000, 2300000)):
            _applied, plan = effective(cs, EditState(cuts=(CutSpan(a, b),)))
            for r in plan.relocations:
                self.assertEqual(
                    r.new_tick, a,
                    "%s landed at %s, join was %s" % (r.label, r.new_tick, a))

    def test_cues_outside_a_cut_are_left_alone(self) -> None:
        cs = self.scene()
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(100000, 200000),)))
        self.assertEqual(plan.relocations, ())
        self.assertEqual(plan.lost, ())

    def test_a_surviving_preload_is_never_given_less_lead(self) -> None:
        """Cuts after a preload eat into the time the scene gave the sky to
        load. EV_FOREE_8514 preloads 18.07s before its end; a cut after it must
        not shorten that."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8514")):
            self.skipTest("EV_FOREE_8514 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8514")
        state = EditState(cuts=(CutSpan(4300000, 4400000),),
                          restore_preload_lead=True)
        _applied, plan = effective(cs, state)
        pre = [r for r in plan.relocations if r.tick == 4209600]
        self.assertEqual(len(pre), 1)
        self.assertEqual(pre[0].from_end, cs.total - 4209600)

    def test_lead_restoration_is_off_unless_asked_for(self) -> None:
        """Rescuing a cue the cut destroyed and re-timing one it never touched
        are different promises, and they used to share a switch. Declining the
        second meant declining the first, which is why EV_FOREE_7512 shipped
        with no protection at all."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8514")):
            self.skipTest("EV_FOREE_8514 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8514")
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(4300000, 4400000),)))
        self.assertEqual([r for r in plan.relocations if r.tick == 4209600], [])

    def test_a_distant_cut_does_not_drag_a_preload_back(self) -> None:
        """Pulling back is for a join sitting inside the load window. A cut an
        age earlier is not worth firing the request in a part of the scene the
        player has long left."""
        cs = self.scene()
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(100000, 200000),)))
        self.assertEqual(plan.relocations, ())

    def test_a_join_inside_the_load_window_moves_the_preload_ahead_of_it(self) -> None:
        """EV_FOREE_7512: the sky is preloaded 7.03s before the end, and the
        last join lands 6.27s before it - inside that window - so the engine is
        still streaming the jump when the request arrives.

        Ahead of the join, not *on* it. The old code set `want = j` and then
        floored at `j`, so `max(want, lo)` could only ever be `j` - the rule had
        exactly one possible answer and it was the instant of the jump itself,
        which is the thing it exists to avoid.
        """
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_7512")):
            self.skipTest("EV_FOREE_7512 not extracted")
        cs = lib.load_cutscene("EV_FOREE_7512")
        cuts = tuple(CutSpan(a, b) for a, b in
                     ((71200, 713600), (1121600, 1472800), (1765600, 1856000)))
        state = EditState(cuts=cuts, restore_preload_lead=True)
        _applied, plan = effective(cs, state)
        pre = [r for r in plan.relocations if r.clip == "SwitchStreamingVolume"]
        self.assertEqual(len(pre), 1)
        join = 772000                                  # the last join
        self.assertLess(pre[0].new_tick, join)         # ahead of it, not on it
        self.assertEqual(pre[0].new_tick, join - (1856000 - 1765600))
        self.assertGreater(pre[0].from_end, cs.total - pre[0].tick)
        # the fade after it is untouched: it is glued to its own footage
        self.assertEqual([r.clip for r in plan.relocations], ["SwitchStreamingVolume"])

    def test_nothing_is_moved_when_the_cuts_never_touched_it(self) -> None:
        """EV_FOREE_7512 has no swallowed cue at all - both its relocatable cues
        survive its three cuts. With the repair on and the guess off, the
        correct answer is to do nothing, which is what the scene wanted and
        could not previously express."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_7512")):
            self.skipTest("EV_FOREE_7512 not extracted")
        cs = lib.load_cutscene("EV_FOREE_7512")
        cuts = tuple(CutSpan(a, b) for a, b in
                     ((71200, 713600), (1121600, 1472800), (1765600, 1856000)))
        _applied, plan = effective(cs, EditState(cuts=cuts))
        self.assertEqual(plan.relocations, ())
        self.assertEqual(plan.lost, ())

    def test_a_cue_with_no_readable_tick_is_reported_not_dropped(self) -> None:
        """EV_FOREE_8512's five streaming cues share a Times array with two
        entries past the playback end, so the extractor rejects the whole array
        and every one of them arrives with `tick: None`. Filtering them out made
        the plan report `lostCues: []` while being blind to all five."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8512")):
            self.skipTest("EV_FOREE_8512 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8512")
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(91200, 309600),)))
        self.assertEqual(len(plan.lost), 5)
        for l in plan.lost:
            self.assertIn("could not read", l.reason)

    def test_a_preload_never_lands_on_its_own_switch(self) -> None:
        """One interior cut can swallow a Preload and the SwitchToPreloaded that
        consumes it. Both belong on the join taken cue by cue, but together that
        fires the switch with nothing loaded - the volume flips to a level that
        is not resident, which is a missing sky or a missing light rig.

        Only the Preload moves; the switch is what the player sees."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8514")):
            self.skipTest("EV_FOREE_8514 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8514")
        # swallows the Jenova Preload (4209600) and its switch (4450400)
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(4150000, 4500000),)))
        pre = [r for r in plan.relocations if r.tick == 4209600]
        swi = [r for r in plan.relocations if r.tick == 4450400
               and r.clip == "SwitchStreamingVolume"]
        self.assertEqual(len(pre), 1)
        self.assertEqual(len(swi), 1)
        self.assertLess(pre[0].new_tick, swi[0].new_tick)
        self.assertEqual(swi[0].new_tick - pre[0].new_tick, 4450400 - 4209600)

    def test_a_switch_is_never_moved(self) -> None:
        """SwitchToPreloaded puts the sky on screen; firing it early is visible."""
        lib = library()
        if not os.path.isfile(lib.path_for("EV_FOREE_8514")):
            self.skipTest("EV_FOREE_8514 not extracted")
        cs = lib.load_cutscene("EV_FOREE_8514")
        _applied, plan = effective(cs, EditState(cuts=(CutSpan(4300000, 4400000),)))
        for r in plan.relocations:
            if r.tick < 4300000:
                self.assertNotIn("SwitchToPreloaded", str(r.match.get("SwitchType")))

    def test_off_means_off(self) -> None:
        cs = self.scene()
        state = EditState(cuts=(CutSpan(1880000, cs.total),), collapse_to_end=False)
        applied, plan = effective(cs, state)
        self.assertEqual(applied.cuts, state.cuts)
        self.assertTrue(plan.is_empty())

    def test_the_plan_carries_it(self) -> None:
        cs = self.scene()
        state = EditState(cuts=(CutSpan(1880000, cs.total),))
        p = to_plan(cs, state)
        self.assertTrue(p["collapseToEnd"])
        self.assertEqual(p["removeRanges"], [[1880000, cs.total]])
        self.assertEqual(len(p["relocateCues"]), 3)
        seqs = {m["seq"] for m in p["relocateCues"]}
        self.assertEqual(seqs, {"CutEvent", "Light"})
        # the patcher matches on these, so they have to be there
        for m in p["relocateCues"]:
            self.assertTrue(m["match"], m["label"])
        back, _ = from_plan(cs, p, cue_key)
        self.assertEqual([(c.a, c.b) for c in back.cuts], [(1880000, cs.total)])
        self.assertTrue(back.collapse_to_end)

    def test_an_old_plan_loads_with_the_feature_off(self) -> None:
        """Turning it on for a plan built before it existed would change what
        that plan builds, silently."""
        cs = self.scene()
        state, _ = from_plan(cs, {"cutscene": self.EV,
                                  "removeRanges": [[1880000, cs.total]]}, cue_key)
        self.assertFalse(state.collapse_to_end)

    def test_invariants_across_every_extracted_scene(self) -> None:
        lib = library()
        paths = sorted(glob.glob(os.path.join(TIMELINES, "*.json")))
        if not paths:
            self.skipTest("no timelines extracted")
        checked = moved = 0
        for path in paths[:400]:
            ev = os.path.splitext(os.path.basename(path))[0]
            try:
                cs = lib.load_cutscene(ev)
            except Exception:
                continue
            if cs.total <= 0:
                continue
            for frac in (0.5, 0.9):
                a = cs.time.snap_to_frame(cs.total * frac)
                applied, plan = effective(cs, EditState(cuts=(CutSpan(a, cs.total),)))
                self.assertEqual(applied.cuts, ((CutSpan(a, cs.total)),))
                new_total = a
                for r in plan.relocations:
                    self.assertGreaterEqual(r.new_tick, 0)
                    self.assertLessEqual(r.new_tick, a)
                    self.assertEqual(r.from_end, new_total - r.new_tick)
                    if r.tick >= a:
                        # the cut swallowed it: it lands exactly where the
                        # translation puts it, unless a surviving cue on the
                        # SAME streaming volume is in the way - order on a
                        # volume outranks exact placement, and is the only
                        # thing allowed to override it
                        want = a - (cs.total - r.tick)
                        self.assertGreaterEqual(r.new_tick, want)
                        if r.new_tick != want:
                            self.assertEqual(r.clip, "SwitchStreamingVolume")
                            vol = r.match.get("VolumeLabel")
                            others = [c for c in relocatable_cues(cs)
                                      if (c["props"] or {}).get("VolumeLabel") == vol
                                      and c["tick"] < a]
                            self.assertTrue(others, "clamped with nothing in front")
                    else:
                        # survived: never moved later, and never given less
                        # lead than it could have
                        # survived: only ever moved EARLIER, so it can never
                        # end up with less lead than leaving it alone would
                        # have given it. It may end up with less than the
                        # scene authored, when the cue in front of it or the
                        # last join is in the way - that is the bound, not a
                        # failure.
                        natural = to_edited(EditState(cuts=(CutSpan(a, cs.total),)),
                                            r.tick)
                        self.assertLessEqual(r.new_tick, natural)
                        self.assertGreaterEqual(r.from_end, new_total - natural)
                    moved += 1
            checked += 1
        self.assertGreater(checked, 0)
        if not moved and too_thin(checked):
            self.skipTest(
                "only %d scenes extracted and none has a relocatable cue - "
                "extract more to exercise this" % checked)
        self.assertGreater(moved, 0, "no scene exercised a relocation")


class BoundedActorPins(unittest.TestCase):
    """A pin that ends - see PinSpan in edits.py.

    EV_FOREE_8514 alternates its two Aeriths between 90s and 95s, then at 95s
    deliberately shows BOTH for the rest of the take: the clean one is the body
    on the floor behind Cloud. A whole-scene Hide on her stops the Z-fighting
    and deletes the body; a bounded one does only the first.
    """

    EV = "EV_FOREE_8514"
    SWAP = (2160000, 2280000)          # 90.00s - 95.00s
    HANDBACK = 2280000                 # the command that shows both again

    def scene(self):
        lib = library()
        if not os.path.isfile(lib.path_for(self.EV)):
            self.skipTest("%s not extracted" % self.EV)
        return lib.load_cutscene(self.EV)

    def test_the_scene_really_does_show_both_at_the_end(self) -> None:
        """If this ever stops being true the bug it explains is gone too."""
        cs = self.scene()
        last = {}
        for e in cs.events("CutEvent"):
            p = e.get("props") or {}
            a = p.get("ActorName")
            if a in ("cut_PC0003_00a", "cut_PC0003_00b") and "Hidden" in p:
                if a not in last or e["tick"] >= last[a][0]:
                    last[a] = (e["tick"], p["Hidden"])
        self.assertEqual(last["cut_PC0003_00a"], (self.HANDBACK, False))
        self.assertEqual(last["cut_PC0003_00b"], (self.HANDBACK, False))

    def test_a_bounded_pin_layers_on_the_whole_scene_one(self) -> None:
        """Hide for the scene plus Show over one range is the combination 8514
        needs, and neither pin can say it alone - so they must compose."""
        s = with_actor_pin(empty_edits(), "cut_PC0003_00a", "hide")
        s = with_pin_span(s, PinSpan("cut_PC0003_00a", False, *self.SWAP))
        self.assertEqual(s.force_hidden, ("cut_PC0003_00a",))
        self.assertEqual(len(s.pin_spans), 1)
        # and setting the base state again keeps the exception carved out of it
        s = with_actor_pin(s, "cut_PC0003_00a", "hide")
        self.assertEqual(len(s.pin_spans), 1)

    def test_the_scene_wide_pin_still_wins_outside_the_range(self) -> None:
        """The patcher applies scene-wide pins first and bounded ones on top,
        so the plan has to list them in that order."""
        cs = self.scene()
        s = with_actor_pin(empty_edits(), "cut_PC0003_00a", "hide")
        s = with_pin_span(s, PinSpan("cut_PC0003_00a", False, 2270000, 2290000))
        p = to_plan(cs, s)
        self.assertEqual(p["forceHidden"], ["cut_PC0003_00a"])
        self.assertEqual(p["pinSpans"][0]["hidden"], False)

    def test_the_final_shot_has_no_command_of_its_own(self) -> None:
        """Which is why a pin has to reach back to the one that governs it -
        without that, selecting the final shot could not change anything."""
        cs = self.scene()
        cmds = cs.visibility_commands("cut_PC0003_00a")
        self.assertTrue(cmds)
        self.assertEqual([t for t, _h in cmds if t >= 3748000], [])
        self.assertEqual(cmds[-1], (self.HANDBACK, False))

    def test_there_are_enough_commands_to_bound_a_window(self) -> None:
        """A range pin MOVES spare commands to its edges rather than flipping
        the one before it, which is what makes the window start where it was
        drawn. Two are needed to open and close one."""
        cs = self.scene()
        cmds = [t for t, _h in cs.visibility_commands("cut_PC0003_00a")]
        self.assertGreater(len(cmds), 2)
        # and the two it would move are the last, so their array stays sorted
        # when they travel to a window later than everything else she does
        self.assertEqual(sorted(cmds), cmds)
        self.assertEqual(cmds[-2:], [2209600, self.HANDBACK])

    def test_one_span_per_actor_so_it_can_always_be_changed(self) -> None:
        """Stacking them left a pin on the plan with no way to tweak it."""
        s = with_pin_span(empty_edits(), PinSpan("A", True, 0, 100))
        s = with_pin_span(s, PinSpan("A", False, 400, 500))
        self.assertEqual(len(pin_spans_for(s, "A")), 1)
        self.assertEqual(pin_spans_for(s, "A")[0].a, 400)
        s = with_pin_span(s, PinSpan("B", True, 0, 100))
        self.assertEqual(len(pin_spans_for(s, "A")), 1)
        self.assertEqual(len(pin_spans_for(s, "B")), 1)

    def test_a_mouse_drawn_range_reaches_the_plan_as_integers(self) -> None:
        """Every tick in the asset is an int32. A range dragged with the mouse
        is not, and a float reaching struct.pack_into failed the whole build."""
        cs = self.scene()
        s = with_pin_span(empty_edits(),
                          PinSpan("cut_PC0003_00a", False,
                                  3827439.0034788996, 4447199.367280735))
        rng = to_plan(cs, s)["pinSpans"][0]["range"]
        self.assertEqual(rng, [3827439, 4447199])
        for v in rng:
            self.assertIsInstance(v, int)

    def test_a_span_can_be_cleared_on_its_own(self) -> None:
        s = with_actor_pin(empty_edits(), "A", "hide")
        s = with_pin_span(s, PinSpan("A", False, 0, 100))
        s = without_actor_pin_span(s, "A")
        self.assertEqual(s.pin_spans, ())
        self.assertEqual(s.force_hidden, ("A",))     # the base state survives

    def test_normal_is_the_reset(self) -> None:
        s = with_actor_pin(empty_edits(), "A", "hide")
        s = with_pin_span(s, PinSpan("A", False, 0, 100))
        s = with_actor_pin(s, "A", "normal")
        self.assertEqual(s.pin_spans, ())
        self.assertEqual(s.force_hidden, ())

    def test_a_bounded_pin_counts_as_an_edit(self) -> None:
        s = with_pin_span(empty_edits(), PinSpan("A", True, 0, 100))
        self.assertFalse(is_untouched(s))

    def test_it_round_trips_through_the_plan(self) -> None:
        cs = self.scene()
        s = with_pin_span(EditState(cuts=(CutSpan(1199200, 1825600),)),
                          PinSpan("cut_PC0003_00a", True, *self.SWAP))
        p = to_plan(cs, s)
        self.assertEqual(p["pinSpans"], [{
            "actor": "cut_PC0003_00a", "hidden": True,
            "range": [self.SWAP[0], self.SWAP[1]],
            "seconds": [90.0, 95.0],
        }])
        back, _ = from_plan(cs, p, cue_key)
        self.assertEqual(back.pin_spans, s.pin_spans)

    def test_an_old_plan_has_no_bounded_pins(self) -> None:
        cs = self.scene()
        back, _ = from_plan(cs, {"cutscene": self.EV,
                                 "removeRanges": [], "forceHidden": ["x"]}, cue_key)
        self.assertEqual(back.pin_spans, ())
        self.assertEqual(back.force_hidden, ("x",))


class PlanParity(unittest.TestCase):
    """A plan saved by an earlier build has to load again unchanged."""

    def test_round_trip(self) -> None:
        lib = library()
        checked = 0
        for path in sorted(glob.glob(os.path.join(PLANS, "*_editplan.json"))):
            with open(path, "r", encoding="utf-8") as f:
                original = json.load(f)
            ev = original.get("cutscene")
            if not ev or not os.path.isfile(lib.path_for(ev)):
                continue
            cs = lib.load_cutscene(ev)
            state, _summary = from_plan(cs, original, cue_key)
            rebuilt = to_plan(cs, state)

            with self.subTest(plan=os.path.basename(path)):
                for key in (
                    "cutscene",
                    "tickResolution",
                    "displayRate",
                    "ticksPerFrame",
                    "playbackRange",
                    "removeRanges",
                    "keepRanges",
                    "disableCues",
                    "forceVisible",
                    "forceHidden",
                    "replaceMusic",
                    "originalTicks",
                    "editedTicks",
                ):
                    if key not in original:
                        continue  # older plans predate some keys
                    self.assertEqual(
                        json.dumps(rebuilt[key], sort_keys=True),
                        json.dumps(original[key], sort_keys=True),
                        "%s differs in %s" % (key, os.path.basename(path)),
                    )
            checked += 1
        if not checked:
            # A release ships `plans/` empty - they are the user's working
            # state, not source - so "no plans to check" is the normal state of
            # a fresh install, not a broken one. With plans present this still
            # exercises every one of them.
            self.skipTest("no saved plans match an extracted scene")

    def test_impact_matches_the_saved_analysis(self) -> None:
        """The warnings are the softlock guard; they must not drift in a port."""
        lib = library()
        for path in sorted(glob.glob(os.path.join(PLANS, "*_editplan.json"))):
            with open(path, "r", encoding="utf-8") as f:
                original = json.load(f)
            ev = original.get("cutscene")
            saved = original.get("impact")
            if not ev or not saved or not os.path.isfile(lib.path_for(ev)):
                continue
            cs = lib.load_cutscene(ev)
            state, _ = from_plan(cs, original, cue_key)
            rebuilt = to_plan(cs, state)["impact"]
            with self.subTest(plan=os.path.basename(path)):
                self.assertEqual(len(rebuilt), len(saved))
                for got, want in zip(rebuilt, saved):
                    for key in ("range", "frames", "wholeShots", "voiceLines",
                                "splitsVoiceLine", "stateTriggers", "jumps",
                                "strandedSubtitles", "lipsyncDesync"):
                        if key in want:
                            self.assertEqual(got[key], want[key], key)


if __name__ == "__main__":
    unittest.main(verbosity=2)


# -- dragging cues -------------------------------------------------------


class MoveIdentity(unittest.TestCase):
    """The editor and the patcher must agree on what identifies a cue.

    `patcher._block_matches` is all-or-nothing: a payload block is a candidate
    only if every discriminator it carries also appears in the plan's `match`
    and agrees. So a key the patcher knows and the editor omits does not
    weaken the match, it destroys it - the cue is reported as not found and
    never moves, which from the editor looks like the drag simply did nothing.
    """

    def test_discriminators_match_the_patcher(self) -> None:
        import patcher

        from editor_qt.core.cues import DISCRIMINATORS

        self.assertEqual(tuple(DISCRIMINATORS), tuple(patcher.DISCRIMINATORS))

    def test_identity_keeps_the_name_the_game_looks_up(self) -> None:
        from editor_qt.core.cues import identity

        self.assertEqual(
            identity({"SeName": "EV_X_01", "Language": "EEndCutLangType::JP"}),
            {"SeName": "EV_X_01"},
        )


class CueMoves(unittest.TestCase):
    """Dragging a cue: state, drawing, and the plan."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = library()
        cls.lib.load()
        cls.cs = cls.lib.load_cutscene("EV_FOREE_8510")
        cls.index = arrays.from_events(cls.cs)

    def _se_lane(self, state=None):
        lanes = build_lanes(self.cs, state or empty_edits())
        return next(ln for ln in lanes if ln.id == "cue:Se")

    def _lane(self, lane_id, state=None):
        lanes = build_lanes(self.cs, state or empty_edits())
        return next(ln for ln in lanes if ln.id == lane_id)

    def test_a_small_drag_moves_one_cue(self) -> None:
        lane = self._se_lane()
        item = lane.items[3]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 8000.0)
        self.assertEqual(len(d.moves), 1)
        self.assertFalse(d.clamped)
        key, move = d.moves[0]
        self.assertEqual(move.tick, item.range[0])
        self.assertEqual(move.new_tick, item.range[0] + d.delta)

    def test_a_drag_stops_at_the_next_cue_in_its_array(self) -> None:
        """The patcher refuses a move that unsorts a Times array, so the drag
        has to stop before it makes one - see core.arrays."""
        lane = self._se_lane()
        item = lane.items[3]
        after = lane.items[4].range[0]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 10_000_000.0)
        self.assertTrue(d.clamped)
        self.assertTrue(d.blocked_by)
        landed = item.range[0] + d.delta
        self.assertLess(landed, after)

    def test_a_drag_back_to_the_authored_tick_is_not_a_move(self) -> None:
        lane = self._se_lane()
        item = lane.items[3]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 8000.0)
        state = with_cue_moves(empty_edits(), d.moves)
        self.assertTrue(state.moves)

        lane_after = self._se_lane(state)
        moved = next(i for i in lane_after.items if i.moved)
        back = propose(self.cs, state, self.index, lane_after, moved, -d.delta)
        self.assertTrue(back.empty, back.note)

    def test_dragging_a_line_carries_its_subtitle(self) -> None:
        """A line of dialogue is a Voice clip plus a subtitle on/off pair in
        `_Text`. Moving the voice alone leaves the caption behind."""
        lane = self._lane("voice")
        item = next(i for i in lane.items if i.props.get("VoiceName"))
        d = propose(self.cs, empty_edits(), self.index, lane, item, 6400.0)
        seqs = sorted(m.seq for _k, m in d.moves)
        self.assertEqual(seqs, ["Text", "Text", "Voice"])
        # one delta for all three, so the caption keeps its offset from the line
        self.assertEqual({m.new_tick - m.tick for _k, m in d.moves}, {d.delta})
        # every one of them carries the field the game looks up
        for _k, m in d.moves:
            self.assertTrue(m.match, "%s has no identity to match on" % m.label)

    def test_the_group_is_the_lead_cue(self) -> None:
        lane = self._lane("voice")
        item = next(i for i in lane.items if i.props.get("VoiceName"))
        d = propose(self.cs, empty_edits(), self.index, lane, item, 6400.0)
        lead = [k for k, m in d.moves if not m.group]
        self.assertEqual(len(lead), 1)
        self.assertTrue(all(m.group == lead[0] for _k, m in d.moves if m.group))

    def test_a_moved_cue_is_drawn_where_it_will_fire(self) -> None:
        """The tracker shows what gets built - the same rule `set_edits`
        follows for cuts."""
        lane = self._se_lane()
        item = lane.items[3]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 8000.0)
        state = with_cue_moves(empty_edits(), d.moves)
        moved = [i for i in self._se_lane(state).items if i.moved]
        self.assertEqual(len(moved), 1)
        self.assertEqual(moved[0].moved_from, item.range[0])
        self.assertEqual(moved[0].range[0], item.range[0] + d.delta)

    def test_a_move_is_authored_in_original_ticks(self) -> None:
        """A cut made later must not drag the cue somewhere else.

        The plan speaks edited ticks and the timeline speaks original ones;
        storing the original and converting at plan time is what makes a move
        mean the same thing before and after the cuts change.
        """
        lane = self._se_lane()
        item = lane.items[8]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 8000.0)
        state = with_cue_moves(empty_edits(), d.moves)
        landed = item.range[0] + d.delta

        cut = CutSpan(0, 24000)          # one second off the front
        after = with_cut(state, cut)
        _key, move = next(iter(after.moves.items()))
        self.assertEqual(move.new_tick, landed, "the authored tick moved")

        plan = to_plan(self.cs, after)
        entry = next(r for r in plan["relocateCues"] if r["tick"] == item.range[0])
        self.assertEqual(entry["newTick"], landed - 24000)
        self.assertEqual(entry["atTick"], landed)

    def test_a_cue_moved_onto_removed_footage_is_reported(self) -> None:
        """Never silent: the cue is listed in `lostCues` with the reason."""
        lane = self._se_lane()
        item = lane.items[8]
        d = propose(self.cs, empty_edits(), self.index, lane, item, 8000.0)
        state = with_cue_moves(empty_edits(), d.moves)
        landed = item.range[0] + d.delta
        state = with_cut(state, CutSpan(landed - 800, landed + 800))

        plan = to_plan(self.cs, state)
        self.assertFalse(
            [r for r in plan["relocateCues"] if r["tick"] == item.range[0]],
            "a cue on removed footage must not be issued",
        )
        self.assertTrue(
            [x for x in plan["lostCues"] if x["tick"] == item.range[0]],
            "a cue on removed footage must be reported",
        )

    def test_moves_round_trip_through_a_plan(self) -> None:
        lane = self._lane("voice")
        item = next(i for i in lane.items if i.props.get("VoiceName"))
        d = propose(self.cs, empty_edits(), self.index, lane, item, 6400.0)
        state = with_cue_moves(empty_edits(), d.moves)

        plan = to_plan(self.cs, state)
        again, summary = from_plan(self.cs, plan, cue_key)
        self.assertEqual(again.moves, state.moves)
        self.assertIn("moved", summary)

    def test_a_scene_with_no_moves_writes_no_move_entries(self) -> None:
        """Plan parity: adding the feature must not change existing plans."""
        plan = to_plan(self.cs, empty_edits())
        self.assertEqual(plan["cueMoves"], [])
        self.assertEqual(plan["relocateCues"], [])

    def test_a_move_alone_is_worth_building(self) -> None:
        """Sliding a sound with no cut anywhere is a complete edit."""
        import build_mod

        lane = self._se_lane()
        d = propose(self.cs, empty_edits(), self.index, lane, lane.items[3], 8000.0)
        plan = to_plan(self.cs, with_cue_moves(empty_edits(), d.moves))
        self.assertFalse(plan["removeRanges"])
        self.assertTrue(plan_changes_something(plan))
        self.assertTrue(build_mod.has_work(plan))

    def test_protected_and_structural_rows_cannot_be_dragged(self) -> None:
        for lane in build_lanes(self.cs, empty_edits()):
            for item in lane.items[:4]:
                if lane.range_row:
                    self.assertFalse(can_move(lane, item), lane.id)
                elif lane.kind == "cue" and (item.clip or item.type) not in (
                    "Se", "BGM", "Voice", "SubTitle"
                ):
                    self.assertFalse(can_move(lane, item), lane.id)


class TimesArrays(unittest.TestCase):
    """The clamp has to enforce exactly the rule the build enforces.

    `core.arrays` decides how far a cue may be dragged;
    `patcher.check_relocation_order` decides whether the build keeps the move.
    If those two ever disagree the editor is lying to the user - either
    refusing something that would have worked, or, far worse, allowing a drag
    that vanishes during the build. These tests read the same assets both do.
    """

    EV = "EV_FOREE_8510"
    AREA = "8800-FOREE"

    @classmethod
    def setUpClass(cls) -> None:
        warnings.simplefilter("ignore", ResourceWarning)
        cls.lib = library()
        cls.lib.load()
        cls.cs = cls.lib.load_cutscene(cls.EV)
        cls.content = None
        for root in (STAGED, os.path.join(os.path.dirname(TOOL_DIR), "Content")):
            if arrays.find_ev_dir(root, cls.AREA, cls.EV):
                cls.content = root
                break
        cls.index = arrays.load(cls.content, cls.AREA, cls.EV, cls.cs.total) \
            if cls.content else None

    def setUp(self) -> None:
        if self.index is None:
            self.skipTest("no Content folder with %s in it" % self.EV)

    def test_the_index_is_read_from_the_assets(self) -> None:
        self.assertTrue(self.index.exact)

    def test_audio_cues_really_do_share_arrays(self) -> None:
        """The premise of the whole clamp. If this ever stops being true the
        constraint can be relaxed - but it must be measured, not assumed."""
        se = [e["tick"] for e in self.cs.events("Sound")]
        self.assertGreater(len(se), 4)
        widest = max(
            self.index.limits("Sound", t).hi - self.index.limits("Sound", t).lo
            for t in se[1:-1]
        )
        self.assertLess(widest, float("inf"),
                        "no Sound cue is bounded — they are not sharing arrays")

    def test_the_clamp_agrees_with_the_patcher(self) -> None:
        import patcher

        path = os.path.join(
            arrays.find_ev_dir(self.content, self.AREA, self.EV),
            "%s_Sound.uasset" % self.EV,
        )
        data = bytearray(open(path, "rb").read())
        blocks = patcher.compiled_event_blocks(bytes(data), self.cs.total)
        remap = patcher.Remap([], self.cs.total)
        margin = self.cs.time.ticks_per_frame

        ticks = sorted({b[1] for b in blocks})
        checked = 0
        for tick in ticks:
            name = next(
                (e["props"].get("SeName") for e in self.cs.events("Sound")
                 if e["tick"] == tick and (e.get("props") or {}).get("SeName")),
                None,
            )
            if not name:
                continue
            lim = self.index.limits("Sound", tick)
            if lim.hi == float("inf"):
                continue                     # last in its array, nothing above
            for target, allowed in (
                (lim.hi - margin, True),      # the furthest the clamp allows
                (lim.hi + margin, False),     # one frame past the next cue
            ):
                if target == tick:
                    continue
                report = {}
                moves = [{"seq": "Sound", "clip": "Se", "tick": tick,
                          "newTick": int(target), "match": {"SeName": name},
                          "label": name}]
                got = patcher.relocation_offsets(data, blocks, moves, report, "Sound")
                kept = patcher.check_relocation_order(
                    blocks, dict(got), report, "Sound", remap
                )
                self.assertEqual(
                    bool(kept), allowed,
                    "editor and patcher disagree about %s -> %s" % (tick, target),
                )
                checked += 1
        self.assertGreater(checked, 0, "no cues were checked")

    def test_the_fallback_is_never_more_permissive(self) -> None:
        """Without Content the index guesses, and the guess must only ever be
        tighter than the truth - a refused drag is arguable, a dropped one is
        not."""
        loose = arrays.from_events(self.cs)
        for e in self.cs.events("Sound"):
            t = e["tick"]
            exact = self.index.limits("Sound", t)
            guess = loose.limits("Sound", t)
            self.assertGreaterEqual(guess.lo, exact.lo, "tick %s" % t)
            self.assertLessEqual(guess.hi, exact.hi, "tick %s" % t)

    def test_an_unbounded_side_does_not_break_the_clamp(self) -> None:
        """The first cue in an array has nothing before it. Substituting the
        target for the missing bound made `clamp` return an infinity."""
        first = min(e["tick"] for e in self.cs.events("Sound"))
        lim = self.index.limits("Sound", first)
        margin = self.cs.time.ticks_per_frame
        got = lim.clamp(first + 400, margin)
        self.assertTrue(float("-inf") < got < float("inf"), got)


class PreviewMixdown(unittest.TestCase):
    """The preview mix has to say the same thing the timeline does.

    A cue switched off must be absent from the sound, a cue dragged must be
    heard where it was dragged to, and a shortened line must stop where the
    block stops. Anything else and the editor is showing one edit and playing
    another, which is the failure the whole tool is arranged to avoid.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = library()
        cls.lib.load()
        cls.cs = cls.lib.load_cutscene("EV_FOREE_8510")
        cls.content = None
        for root in (STAGED, os.path.join(os.path.dirname(TOOL_DIR), "Content")):
            if root and os.path.isdir(os.path.join(root, "Sound")):
                cls.content = root
                break

    def _voice_item(self, index=0):
        lanes = build_lanes(self.cs, empty_edits())
        lane = next(ln for ln in lanes if ln.id == "voice")
        return lane, [i for i in lane.items if i.props.get("VoiceName")][index]

    def test_every_cue_is_placed_at_its_own_tick(self) -> None:
        items, disabled, moved, _r = mixdown.placements(self.cs, empty_edits())
        self.assertTrue(items)
        self.assertEqual((disabled, moved), (0, 0))
        vo = {p.name: p.tick for p in items if p.kind == "vo"}
        for v in self.cs.voice:
            self.assertEqual(vo.get(v.name), v.tick)

    def test_a_disabled_cue_is_left_out_of_the_mix(self) -> None:
        _lane, item = self._voice_item()
        key = cue_key(cue_descriptor(item))
        state = with_cue_toggled(empty_edits(), key, cue_descriptor(item))
        items, disabled, _moved, _r = mixdown.placements(self.cs, state)
        self.assertEqual(disabled, 1)
        self.assertNotIn(item.props["VoiceName"],
                         [p.name for p in items if p.kind == "vo"])

    def test_a_moved_cue_is_heard_where_it_was_dragged(self) -> None:
        """The whole point of attaching the sound to the block."""
        lane, item = self._voice_item(2)
        index = arrays.from_events(self.cs)
        d = propose(self.cs, empty_edits(), index, lane, item, 24000.0)
        self.assertTrue(d.moves)
        state = with_cue_moves(empty_edits(), d.moves)
        items, _disabled, moved, _r = mixdown.placements(self.cs, state)
        self.assertGreaterEqual(moved, 1)
        at = {p.name: p.tick for p in items if p.kind == "vo"}
        self.assertEqual(at[item.props["VoiceName"]], item.range[0] + d.delta)

    def test_a_trimmed_line_stops_where_the_block_stops(self) -> None:
        v = next(x for x in self.cs.voice if x.duration and x.duration > 1.0)
        keep = round(v.duration / 2, 2)
        state = with_trim(empty_edits(), v.name, keep)
        items, _d, _m, _r = mixdown.placements(self.cs, state)
        p = next(x for x in items if x.kind == "vo" and x.name == v.name)
        self.assertEqual(p.max_sec, keep)

    def test_music_stops_where_the_next_track_starts(self) -> None:
        """Two BGM streams running over each other is what makes a music
        change inaudible - which is the edit this exists to preview."""
        items, _d, _m, _r = mixdown.placements(self.cs, empty_edits())
        music = [p for p in items if p.kind == "bgm"]
        if len(music) < 2:
            self.skipTest("scene has fewer than two music cues")
        ticks = self.cs.time.ticks_per_second
        for a, b in zip(music, music[1:]):
            self.assertAlmostEqual(a.max_sec, (b.tick - a.tick) / ticks, places=3)

    def test_the_fingerprint_ignores_cuts_but_not_the_sound(self) -> None:
        """Cuts are applied by the playback clock, not baked into the file, so
        adding one must not throw away a render that is still correct."""
        base = mixdown.edit_fingerprint(self.cs, empty_edits(), "US")
        with_a_cut = mixdown.edit_fingerprint(
            self.cs, with_cut(empty_edits(), CutSpan(0, 24000)), "US")
        self.assertEqual(base, with_a_cut)

        _lane, item = self._voice_item()
        killed = with_cue_toggled(empty_edits(), cue_key(cue_descriptor(item)),
                                  cue_descriptor(item))
        self.assertNotEqual(base, mixdown.edit_fingerprint(self.cs, killed, "US"))

    def test_bgm_variations_resolve_to_their_extracted_wav(self) -> None:
        """`bgm_X_03` is variation 3 of `bgm_X`, written out by AudioMog as
        `bgm_X_Project/bgm_X_003.wav`. Searching for `bgm_X_03.uasset` - what
        audio_build did - can never match anything, which is why every offline
        mix reports `bgm: 0`."""
        if not self.content:
            self.skipTest("no Content folder")
        items, _d, _m, _r = mixdown.placements(self.cs, empty_edits())
        music = [p for p in items if p.kind == "bgm"]
        if not music:
            self.skipTest("scene has no music cues")
        found = [p for p in music if mixdown.bgm_source(self.content, p.name)]
        self.assertTrue(
            found,
            "no music cue resolved — check bgm_<base>_Project/<base>_NNN.wav",
        )

    def test_a_render_is_reused_for_an_unchanged_edit(self) -> None:
        if not self.content:
            self.skipTest("no Content folder")
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("numpy not available")
        with tempfile.TemporaryDirectory() as cache:
            first = mixdown.render(self.cs, empty_edits(), self.content, cache)
            if first is None:
                self.skipTest("nothing placeable in this scene")
            self.assertTrue(os.path.isfile(first.path))
            self.assertFalse(first.cached)
            again = mixdown.render(self.cs, empty_edits(), self.content, cache)
            self.assertTrue(again.cached)
            self.assertEqual(again.path, first.path)
            # and the counts survive a cache hit, so the status line stays honest
            self.assertEqual((again.vo, again.se, again.bgm),
                             (first.vo, first.se, first.bgm))


class BgmLookup(unittest.TestCase):
    """Finding the track a music cue names.

    Every case here is one that was wrong at some point, and each was found by
    measuring the whole set rather than by reading the code - which is the only
    reason the second bug was caught before it shipped.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.content = None
        for root in (STAGED, os.path.join(os.path.dirname(TOOL_DIR), "Content")):
            if root and os.path.isdir(os.path.join(root, "Sound", "BGM")):
                cls.content = root
                break

    def setUp(self) -> None:
        if not self.content:
            self.skipTest("no Content/Sound/BGM folder")

    def _named(self, name):
        return mixdown.bgm_source(self.content, name)

    def test_a_cue_naming_a_whole_bank_resolves_to_that_bank(self) -> None:
        """`bgm_Corle_004` looks like variation 4 of `bgm_Corle` and is not:
        it is a track in its own right. 101 of this game's 195 music cues are
        that shape, and splitting the name before checking whether it exists
        sent every one of them to "unresolved"."""
        src = self._named("bgm_Corle_004")
        if not src.ok:
            self.skipTest("bgm_Corle_004 not extracted here")
        self.assertIn("bgm_Corle_004", os.path.basename(src.path))
        self.assertNotIn("bgm_Corle_000", os.path.basename(src.path))

    def test_a_variation_resolves_to_its_own_wav(self) -> None:
        src = self._named("bgm_Foree2_009_03")
        if not src.ok:
            self.skipTest("bgm_Foree2_009 not extracted here")
        self.assertEqual(os.path.basename(src.path), "bgm_Foree2_009_003.wav")

    def test_a_project_extracted_into_itself_is_still_found(self) -> None:
        """One of the 816 banks here was extracted twice, so its wavs sit in
        `<base>_Project/<base>_Project/`. Looking only at the top level found
        nothing and fell through to a fallback that played another track -
        which is the fault that started this."""
        src = self._named("bgm_Foree2_011_06")
        if not src.ok:
            self.skipTest("bgm_Foree2_011 not extracted here")
        self.assertEqual(os.path.basename(src.path), "bgm_Foree2_011_006.wav")

    def test_an_impossible_variation_is_refused_not_substituted(self) -> None:
        """A bank's HCA stream count and its slice count are different numbers
        - 7 streams for 9 slices in one case here - so indexing streams by the
        cue's number cannot be right even in principle. Confidently wrong music
        is worse than silence: silence gets investigated."""
        src = self._named("bgm_Foree2_009_09")
        self.assertFalse(src.ok)
        self.assertIn("variation", src.why)

    def test_an_unextracted_bank_says_so(self) -> None:
        src = self._named("bgm_ThisBankDoesNotExist_02")
        self.assertFalse(src.ok)
        self.assertTrue(src.why)

    def test_the_wav_index_always_matches_the_cue(self) -> None:
        """Whatever path a cue takes, the file it lands on must carry the
        number the cue asked for. This is the assertion that would have caught
        the original bug on its own."""
        checked = 0
        for name in ("bgm_Foree2_009_03", "bgm_Foree2_009_04",
                     "bgm_Foree2_011_06", "bgm_Foree2_011_00"):
            src = self._named(name)
            if not src.ok or src.kind != "wav":
                continue
            want = int(re.match(r"^.*_(\d+)$", name).group(1))
            got = int(re.match(r"^.*_(\d+)\.wav$", os.path.basename(src.path)).group(1))
            self.assertEqual(got, want, "%s landed on %s" % (name, src.path))
            checked += 1
        self.assertGreater(checked, 0, "no music cue resolved to a wav")


# -- pointing a music trigger somewhere else -----------------------------

from editor_qt.core.edits import (  # noqa: E402
    MusicRepoint,
    music_name_at,
    with_music_repointed,
    without_music_repoint,
)
from editor_qt.core.music import (  # noqa: E402
    MusicLibrary,
    capacity_of,
    cue_name,
    fits,
    split_cue_name,
    why_not,
)

#: The exported game content, if this checkout sits beside it.
CONTENT = os.path.join(os.path.dirname(TOOL_DIR), "Content")


def _bank(root: str, name: str, slices: int,
          users=None, extracted: bool = True) -> None:
    """Write a plausible BGM bank into a fake content root."""
    bgm = os.path.join(root, "Sound", "BGM")
    os.makedirs(bgm, exist_ok=True)
    with open(os.path.join(bgm, name + ".uasset"), "wb") as f:
        f.write(b"\0" * 16)
    if not extracted:
        return
    proj = os.path.join(bgm, name + "_Project")
    os.makedirs(proj, exist_ok=True)
    with open(os.path.join(proj, "RebuildSettings.json"), "w") as f:
        json.dump({"Originals": [{"SliceIndex": i} for i in range(slices)]}, f)
    lines = []
    for i in range(slices):
        who = (users or {}).get(i, ["Section%d" % i])
        lines.append("%s_%03d.hca,\t\tusers: %s"
                     % (name, i, ", ".join("%s (layer 0)" % w for w in who)))
        _silence(os.path.join(proj, "%s_%03d.wav" % (name, i)), seconds=1 + i)
    with open(os.path.join(proj, "TrackUsers.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


def _silence(path: str, seconds: int) -> None:
    import wave as wave_file

    with wave_file.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\0" * (2 * 8000 * seconds))


class TurningAnAttachRound(unittest.TestCase):
    """`patcher.detach_constraint` — the one disable that is a flag, not a name.

    A Constraint's ActorName is not something the game looks up: it says which
    actor to attach. EV_CORLE_0100 proved it over two builds — six flower-lei
    constraints renamed, the patched asset carrying every broken name, the leis
    still on the characters. The payload's own `Detach` bool is the switch the
    format actually offers, so switching one off flips that instead, and leaves
    every name intact because the detach has to resolve the same actor.

    Built from bytes rather than from a staged asset: the two constraint files
    in the fixtures have no locatable event blocks, and the format this walks is
    the thing worth pinning anyway.
    """

    ACTOR = "EV_TEST_0100_FA0418_00a"

    def _fstring(self, text: str) -> bytes:
        raw = text.encode("latin1") + b"\0"
        return struct.pack("<i", len(raw)) + raw

    def _payload(self, actor: str, detach: bool) -> bytes:
        """One Clip_Constraint payload: ActorName, SocketName, Detach."""
        out = b"\0" * 8                       # the 8 bytes the walk skips
        for key, value in (("ActorName", actor), ("SocketName", "Attach_FlowerLei01")):
            body = self._fstring(value)
            out += (self._fstring(key) + self._fstring("StrProperty")
                    + struct.pack("<ii", len(body), 0) + b"\0" + body)
        out += (self._fstring("Detach") + self._fstring("BoolProperty")
                + struct.pack("<ii", 0, 0) + bytes([1 if detach else 0]) + b"\0")
        out += self._fstring("None")
        return out

    def _fields(self, data, size):
        import patcher
        return patcher.payload_all_fields(bytes(data), 0, size)

    def test_the_flag_goes_on_and_nothing_moves(self) -> None:
        import patcher
        raw = self._payload(self.ACTOR, detach=False)
        data = bytearray(raw)
        size = len(raw) - 8
        got = patcher.detach_constraint(data, [(0, 4200, 0, size)], self.ACTOR, 4200)
        self.assertEqual(got, 1)
        self.assertEqual(len(data), len(raw), "in-place means the same size")
        flag = dict((k, v) for k, _t, v, _o in self._fields(data, size))
        self.assertTrue(flag["Detach"])

    def test_the_names_are_left_alone(self) -> None:
        """A detach has to resolve the actor the attach resolved."""
        import patcher
        raw = self._payload(self.ACTOR, detach=False)
        data = bytearray(raw)
        size = len(raw) - 8
        patcher.detach_constraint(data, [(0, 4200, 0, size)], self.ACTOR, 4200)
        vals = dict((k, v) for k, _t, v, _o in self._fields(data, size))
        self.assertEqual(vals["ActorName"], self.ACTOR)
        self.assertEqual(vals["SocketName"], "Attach_FlowerLei01")

    def test_another_actor_is_not_touched(self) -> None:
        import patcher
        raw = self._payload("EV_TEST_0100_FA0418_00z", detach=False)
        data = bytearray(raw)
        size = len(raw) - 8
        got = patcher.detach_constraint(data, [(0, 4200, 0, size)], self.ACTOR, 4200)
        self.assertEqual(got, 0)
        self.assertEqual(bytes(data), raw)

    def test_a_cue_at_another_tick_is_not_touched(self) -> None:
        import patcher
        raw = self._payload(self.ACTOR, detach=False)
        data = bytearray(raw)
        size = len(raw) - 8
        got = patcher.detach_constraint(data, [(0, 9999, 0, size)], self.ACTOR, 4200)
        self.assertEqual(got, 0)

    def test_every_copy_of_the_cue_is_flipped(self) -> None:
        """Each payload exists twice — its own section and the compiled
        template a shipping build evaluates. Missing one ships the attach."""
        import patcher
        one = self._payload(self.ACTOR, detach=False)
        size = len(one) - 8
        data = bytearray(one + one)
        blocks = [(0, 4200, 0, size), (1, 4200, len(one), size)]
        self.assertEqual(
            patcher.detach_constraint(data, blocks, self.ACTOR, 4200), 2)


class MusicBudgetIsTheScenesOwn(unittest.TestCase):
    """A repoint must not spend the room it is written into.

    Every build stages pristine assets (`build_mod` wipes the staging folder
    first), so the span a name is written into is always the one the scene
    shipped with. Measure a repoint against its own last choice instead and the
    budget ratchets down with every shorter track picked, until a trigger sent
    somewhere brief can never be sent home again.
    """

    AUTHORED = "bgm_Corle_0001"   # 14
    SHORTER = "bgm_Cor"           # 7

    def test_the_budget_is_the_authored_name(self) -> None:
        self.assertEqual(capacity_of(self.AUTHORED), len(self.AUTHORED))

    def test_a_shorter_choice_is_allowed(self) -> None:
        self.assertTrue(fits(self.SHORTER, self.AUTHORED))

    def test_the_authored_name_always_fits_again(self) -> None:
        """The revert has to be reachable however short the detour was."""
        self.assertTrue(fits(self.AUTHORED, self.AUTHORED))

    def test_measuring_against_the_repoint_would_trap_it(self) -> None:
        """States the bug this guards against, rather than describing the fix:
        pass the *current* name and going home becomes impossible."""
        self.assertFalse(fits(self.AUTHORED, self.SHORTER))

    def test_a_repoint_records_the_authored_budget(self) -> None:
        r = MusicRepoint(seq="ManualSE", tick=0, frm=self.AUTHORED,
                         to=self.SHORTER, capacity=capacity_of(self.AUTHORED))
        self.assertEqual(r.capacity, len(self.AUTHORED))
        self.assertGreater(r.capacity, len(r.to))


class MusicNames(unittest.TestCase):
    """What a cue has to be called, and how much room the name has."""

    KNOWN = {"bgm_Corle_005", "bgm_Corle_004", "bgm_X"}

    def _exists(self, n: str) -> bool:
        return n in self.KNOWN

    def test_slice_zero_is_the_bare_bank_name(self) -> None:
        self.assertEqual(cue_name("bgm_Corle_005", 0), "bgm_Corle_005")
        self.assertEqual(cue_name("bgm_Corle_005", 1), "bgm_Corle_005_01")
        self.assertEqual(cue_name("bgm_Corle_005", 12), "bgm_Corle_005_12")

    def test_a_bank_whose_name_ends_in_digits_is_not_a_slice(self) -> None:
        """`bgm_Corle_004` reads exactly like slice 4 of `bgm_Corle` and is a
        bank in its own right. Existence decides, and it has to be asked
        first - mixdown.bgm_source learned this the expensive way."""
        self.assertEqual(split_cue_name("bgm_Corle_004", self._exists),
                         ("bgm_Corle_004", 0))

    def test_a_suffix_on_a_known_bank_is_a_slice(self) -> None:
        self.assertEqual(split_cue_name("bgm_Corle_005_01", self._exists),
                         ("bgm_Corle_005", 1))

    def test_an_unknown_name_resolves_to_nothing(self) -> None:
        self.assertEqual(split_cue_name("bgm_Nope_99", self._exists), ("", 0))
        self.assertEqual(split_cue_name("", self._exists), ("", 0))

    def test_round_trip_through_a_cue_name(self) -> None:
        for i in (0, 1, 7, 15):
            got = split_cue_name(cue_name("bgm_X", i), self._exists)
            self.assertEqual(got, ("bgm_X", i))

    def test_capacity_is_the_length_of_the_name_already_there(self) -> None:
        self.assertEqual(capacity_of("bgm_Nible_029"), 13)
        self.assertTrue(fits("bgm_Corle_000", "bgm_Nible_029"))   # same length
        self.assertTrue(fits("bgm_silence", "bgm_Nible_029"))     # shorter
        self.assertFalse(fits("bgm_Before_Cutscene", "bgm_Nible_029"))

    def test_the_refusal_names_both_lengths(self) -> None:
        why = why_not("bgm_Before_Cutscene", "bgm_Nible_029")
        self.assertIn("19", why)
        self.assertIn("13", why)
        self.assertEqual(why_not("bgm_silence", "bgm_Nible_029"), "")


class MusicBanks(unittest.TestCase):
    """The library, against a content root built for the purpose."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.tmp.name
        _bank(root, "bgm_Alpha", 1)
        _bank(root, "bgm_beta_002", 3,
              users={0: ["Section0"], 1: ["Skip", "Skip2"], 2: []})
        _bank(root, "bgm_Gamma", 2, extracted=False)
        cls.lib = MusicLibrary(root)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_lists_every_bank_sorted_case_insensitively(self) -> None:
        self.assertEqual(self.lib.names(),
                         ("bgm_Alpha", "bgm_beta_002", "bgm_Gamma"))

    def test_reads_slices_and_the_sections_that_use_them(self) -> None:
        bank = self.lib.bank("bgm_beta_002")
        self.assertEqual([s.index for s in bank.slices], [0, 1, 2])
        self.assertEqual(bank.slices[0].sections, ("Section0",))
        self.assertEqual(bank.slices[1].sections, ("Skip", "Skip2"))
        self.assertEqual(bank.slices[1].label, "Skip, Skip2")

    def test_a_stream_no_section_uses_is_kept_and_marked(self) -> None:
        """Several banks carry alternate takes nothing refers to. They are
        playable, so they stay listed - finding one is the point."""
        s = self.lib.bank("bgm_beta_002").slices[2]
        self.assertTrue(s.unused)
        self.assertEqual(s.label, "slice 2")
        self.assertTrue(s.wav)

    def test_slice_lengths_come_from_the_wav_header(self) -> None:
        bank = self.lib.bank("bgm_beta_002")
        self.assertAlmostEqual(bank.slices[0].seconds, 1.0, places=3)
        self.assertAlmostEqual(bank.slices[2].seconds, 3.0, places=3)

    def test_an_unextracted_bank_still_offers_its_own_name(self) -> None:
        bank = self.lib.bank("bgm_Gamma")
        self.assertEqual([s.index for s in bank.slices], [0])
        self.assertFalse(bank.extracted)
        self.assertIn("AudioMog", bank.why)

    def test_a_bank_that_is_not_there_is_reported_not_invented(self) -> None:
        bank = self.lib.bank("bgm_Nope")
        self.assertEqual(bank.slices, ())
        self.assertTrue(bank.why)

    def test_search_matches_words_in_any_order(self) -> None:
        self.assertEqual(self.lib.search("beta 002"), ("bgm_beta_002",))
        self.assertEqual(self.lib.search("002 BETA"), ("bgm_beta_002",))
        self.assertEqual(self.lib.search(""), self.lib.names())
        self.assertEqual(self.lib.search("nothing here"), ())

    def test_a_name_that_ends_in_digits_resolves_to_the_bank(self) -> None:
        """`bgm_beta_002` is a bank, not slice 2 of `bgm_beta`."""
        self.assertEqual(self.lib.resolve("bgm_beta_002"), ("bgm_beta_002", 0))
        self.assertEqual(self.lib.resolve("bgm_beta_002_01"), ("bgm_beta_002", 1))

    def test_describe_says_bank_slice_and_section(self) -> None:
        line = self.lib.describe("bgm_beta_002_01")
        self.assertIn("bgm_beta_002", line)
        self.assertIn("slice 1", line)
        self.assertIn("Skip", line)

    def test_no_content_root_is_not_an_error(self) -> None:
        empty = MusicLibrary(None)
        self.assertFalse(empty.available)
        self.assertEqual(empty.names(), ())


class MusicRepoints(unittest.TestCase):
    """The edit itself, and its trip through the plan."""

    KEY = "ManualSE|0|MusicName|bgm_Nible_029"

    def _repoint(self, to: str = "bgm_Corle_000") -> MusicRepoint:
        return MusicRepoint(seq="ManualSE", tick=0, frm="bgm_Nible_029", to=to,
                            bank=to, slice=0, capacity=13, label=to)

    def test_it_is_an_edit(self) -> None:
        s = with_music_repointed(empty_edits(), self.KEY, self._repoint())
        self.assertFalse(is_untouched(s))
        self.assertEqual(music_name_at(s, self.KEY, "bgm_Nible_029"),
                         "bgm_Corle_000")

    def test_choosing_the_scene_s_own_track_clears_it(self) -> None:
        """Same rule as dragging a cue back to its authored tick: an edit that
        changes nothing does not belong in the plan."""
        s = with_music_repointed(empty_edits(), self.KEY, self._repoint())
        s = with_music_repointed(s, self.KEY, self._repoint("bgm_Nible_029"))
        self.assertEqual(s.repoints, {})
        self.assertTrue(is_untouched(s))

    def test_removing_one_leaves_the_others(self) -> None:
        s = with_music_repointed(empty_edits(), self.KEY, self._repoint())
        s = with_music_repointed(s, "other", self._repoint("bgm_silence"))
        s = without_music_repoint(s, "other")
        self.assertEqual(list(s.repoints), [self.KEY])
        self.assertIs(without_music_repoint(s, "not there"), s)

    def test_a_cue_can_be_moved_and_repointed(self) -> None:
        """Both maps are keyed the same way on purpose, so one cue can carry
        an entry in each without either knowing about the other."""
        s = with_music_repointed(empty_edits(), self.KEY, self._repoint())
        s = with_cue_toggled(s, "someone else", {"seq": "Voice", "tick": 1,
                                                 "field": "VoiceName", "value": "x"})
        self.assertEqual(len(s.repoints), 1)
        self.assertEqual(len(s.killed), 1)

    def test_it_round_trips_through_a_plan(self) -> None:
        lib = library()
        ev = "EV_GRASE_0010"
        if not os.path.isfile(lib.path_for(ev)):
            self.skipTest("no timeline for %s" % ev)
        cs = lib.load_cutscene(ev)
        state = with_music_repointed(empty_edits(), self.KEY, self._repoint())
        plan = to_plan(cs, state)

        self.assertEqual(len(plan["repointMusic"]), 1)
        entry = plan["repointMusic"][0]
        self.assertEqual(entry["from"], "bgm_Nible_029")
        self.assertEqual(entry["to"], "bgm_Corle_000")
        self.assertEqual(entry["field"], "MusicName")
        self.assertEqual(entry["key"], self.KEY)

        back, summary = from_plan(cs, plan, cue_key)
        self.assertEqual(back.repoints, state.repoints)
        self.assertIn("repointed", summary)
        # and again, so a plan saved by this build reloads byte-identically
        self.assertEqual(json.dumps(to_plan(cs, back)["repointMusic"]),
                         json.dumps(plan["repointMusic"]))

    def test_the_key_is_derived_rather_than_read(self) -> None:
        """An entry with no `key` at all still loads: the key is spelled from
        the sub-sequence, the authored tick and the authored name, which the
        entry carries anyway. Reading it instead is what let a wrong one in."""
        lib = library()
        ev = "EV_GRASE_0010"
        if not os.path.isfile(lib.path_for(ev)):
            self.skipTest("no timeline for %s" % ev)
        cs = lib.load_cutscene(ev)
        plan = to_plan(cs, empty_edits())
        plan["repointMusic"] = [{"seq": "ManualSE", "tick": 0,
                                 "from": "a", "to": "b"}]
        back, _ = from_plan(cs, plan, cue_key)
        self.assertEqual(list(back.repoints), ["ManualSE|0|MusicName|a"])

    def test_an_entry_with_no_from_or_to_is_skipped(self) -> None:
        lib = library()
        ev = "EV_GRASE_0010"
        if not os.path.isfile(lib.path_for(ev)):
            self.skipTest("no timeline for %s" % ev)
        cs = lib.load_cutscene(ev)
        plan = to_plan(cs, empty_edits())
        plan["repointMusic"] = [{"seq": "ManualSE", "tick": 0, "to": "b"},
                                {"seq": "ManualSE", "tick": 0, "from": "a"}]
        back, _ = from_plan(cs, plan, cue_key)
        self.assertEqual(back.repoints, {})

    def test_a_key_from_a_dragged_block_is_repaired_on_load(self) -> None:
        """The bug this cost a session to find.

        The window keyed a repoint off a **dragged** block's current tick, so
        the plan recorded the right cue under a key nothing else in the program
        spelled that way: `mixdown.placements` looked it up by the authored
        tick, found nothing, and the preview went on playing the old track
        while the timeline showed the new one.

        The `tick` beside the key was always the authored one, so a plan
        written that way can be repaired instead of lost.
        """
        lib = library()
        ev = "EV_GRASE_0010"
        if not os.path.isfile(lib.path_for(ev)):
            self.skipTest("no timeline for %s" % ev)
        cs = lib.load_cutscene(ev)
        plan = to_plan(cs, empty_edits())
        plan["repointMusic"] = [{
            "key": "ManualSE|565600|MusicName|bgm_Foree2_011_06",   # where it was dragged
            "seq": "ManualSE",
            "tick": 880000,                                          # where it is authored
            "from": "bgm_Foree2_011_06",
            "to": "bgm_Foree2_011",
        }]
        back, _ = from_plan(cs, plan, cue_key)
        self.assertEqual(list(back.repoints),
                         ["ManualSE|880000|MusicName|bgm_Foree2_011_06"])
        # and saving it again writes the repaired key, so it heals for good
        self.assertEqual(to_plan(cs, back)["repointMusic"][0]["key"],
                         "ManualSE|880000|MusicName|bgm_Foree2_011_06")

    def test_a_repoint_on_its_own_is_worth_building(self) -> None:
        """Swapping a scene's music without cutting a frame is a whole mod."""
        self.assertTrue(plan_changes_something({"repointMusic": [{"to": "x"}]}))
        self.assertFalse(plan_changes_something({"replaceMusic": ["x"]}))

    def test_an_old_plan_still_loads(self) -> None:
        lib = library()
        ev = "EV_GRASE_0010"
        if not os.path.isfile(lib.path_for(ev)):
            self.skipTest("no timeline for %s" % ev)
        cs = lib.load_cutscene(ev)
        plan = to_plan(cs, empty_edits())
        del plan["repointMusic"]
        back, _ = from_plan(cs, plan, cue_key)
        self.assertEqual(back.repoints, {})


def _a_scene_with_music():
    """(ev, area, path to its _ManualSE, MusicName, tick) from the real export."""
    if not os.path.isdir(CONTENT) or not os.path.isdir(TIMELINES):
        return None
    for path in sorted(glob.glob(os.path.join(TIMELINES, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tl = json.load(f)
        except Exception:
            continue
        ev, area = tl.get("cutscene"), tl.get("area")
        if not ev or not area:
            continue
        for seq in ("ManualSE", "Sound"):
            for e in (tl.get("events") or {}).get(seq, []):
                name = (e.get("props") or {}).get("MusicName")
                if not name or e.get("tick") is None:
                    continue
                asset = os.path.join(CONTENT, "Cut", "Game", area, ev,
                                     "%s_%s.uasset" % (ev, seq))
                if os.path.isfile(asset):
                    return ev, seq, asset, name, e["tick"]
    return None


class RelocatedThenRepointed(unittest.TestCase):
    """Verification has to expect the file as it ends up, not as it was matched.

    `apply_plan` moves cues and *then* renames them - it has to, because the
    move is matched on the name the file still carries. So a cue that was
    dragged and repointed answers to the new name by the time `verify` reads
    it back, and checking it against the move's own `match` failed a correct
    build with `relocatedCues: 0 placed, 1 missing`.
    """

    def setUp(self) -> None:
        import build_mod

        self.build_mod = build_mod
        self.plan = {
            "relocateCues": [{
                "seq": "ManualSE", "clip": "BGM", "tick": 880000,
                "newTick": 329600, "match": {"MusicName": "bgm_Foree2_011_06"},
            }],
            "repointMusic": [{
                "seq": "ManualSE", "tick": 880000,
                "from": "bgm_Foree2_011_06", "to": "bgm_Foree2_011",
            }],
        }

    def _want(self, seq="ManualSE"):
        return self.build_mod.expected_match(
            self.plan, seq, self.plan["relocateCues"][0]["match"])

    def test_it_expects_the_repointed_name(self) -> None:
        self.assertEqual(self._want(), {"MusicName": "bgm_Foree2_011"})

    def test_a_repoint_in_another_sub_sequence_does_not_apply(self) -> None:
        self.assertEqual(self._want("Sound"), {"MusicName": "bgm_Foree2_011_06"})

    def test_a_move_with_no_repoint_is_left_alone(self) -> None:
        self.plan["repointMusic"] = []
        self.assertEqual(self._want(), {"MusicName": "bgm_Foree2_011_06"})

    def test_other_discriminators_are_untouched(self) -> None:
        match = {"MusicName": "bgm_Foree2_011_06", "CrossFade": True}
        got = self.build_mod.expected_match(self.plan, "ManualSE", match)
        self.assertEqual(got, {"MusicName": "bgm_Foree2_011", "CrossFade": True})
        self.assertEqual(match["MusicName"], "bgm_Foree2_011_06")  # not mutated

    def test_a_move_that_names_no_music_is_returned_as_is(self) -> None:
        match = {"From": 0, "To": 1, "White": False}
        self.assertEqual(
            self.build_mod.expected_match(self.plan, "CutEvent", match), match)


class MusicCueKeys(unittest.TestCase):
    """Four ways of naming one cue, which must not drift apart.

    A repoint is stored under a cue key, and four places have to arrive at the
    same string for it to be found again: the raw event (`event_cue_key`), the
    block on screen (`drag.authored_key`), the plan entry (`plan.repoint_key`)
    and the window's own lookup. Getting one of them wrong is not a crash - it
    is an edit that shows on the timeline and does nothing to the sound.
    """

    @classmethod
    def setUpClass(cls) -> None:
        from editor_qt.core.cues import event_cue_key
        from editor_qt.core.drag import authored_key
        from editor_qt.core.plan import repoint_key

        cls.event_cue_key = staticmethod(event_cue_key)
        cls.authored_key = staticmethod(authored_key)
        cls.repoint_key = staticmethod(repoint_key)
        cls.lib = library()

    def _scene_with_music(self):
        for ev in ("EV_FOREE_8512", "EV_GRASE_0010", "EV_FOREE_8510"):
            if not os.path.isfile(self.lib.path_for(ev)):
                continue
            cs = self.lib.load_cutscene(ev)
            for seq in mixdown.SE_GROUPS:
                for e in cs.events(seq):
                    if (e.get("props") or {}).get("MusicName"):
                        return cs, seq, e
        raise unittest.SkipTest("no exported scene with a music cue")

    def _bgm_item(self, cs, state):
        for lane in build_lanes(cs, state):
            for item in lane.items:
                if (item.clip or item.type) == "BGM":
                    return item
        return None

    def test_all_four_spellings_agree_for_a_cue_where_it_was_authored(self) -> None:
        cs, seq, e = self._scene_with_music()
        want = self.event_cue_key(seq, e)
        item = self._bgm_item(cs, empty_edits())
        self.assertIsNotNone(item)
        self.assertEqual(self.authored_key(item), want)
        self.assertEqual(
            self.repoint_key(seq, e["tick"], e["props"]["MusicName"]), want)

    def test_they_still_agree_after_the_cue_has_been_dragged(self) -> None:
        """The case that broke. A dragged block is drawn where it will fire, so
        a key taken off it hashes to the new tick - and every other spelling
        still says the authored one."""
        cs, seq, e = self._scene_with_music()
        want = self.event_cue_key(seq, e)
        moved = with_cue_moves(empty_edits(), [(want, CueMove(
            seq=seq, clip="BGM", tick=e["tick"],
            new_tick=e["tick"] + 40000,
            match={"MusicName": e["props"]["MusicName"]}))])
        item = self._bgm_item(cs, moved)
        self.assertIsNotNone(item)
        self.assertIsNotNone(item.moved_from)
        self.assertNotEqual(item.tick_start, item.moved_from)
        self.assertEqual(self.authored_key(item), want)
        self.assertEqual(
            self.repoint_key(seq, item.moved_from, e["props"]["MusicName"]), want)

    def test_a_repoint_on_a_dragged_cue_reaches_the_mix(self) -> None:
        """End to end: drag the music cue, repoint it, and the preview has to
        play the new track. This is the exact sequence that failed."""
        cs, seq, e = self._scene_with_music()
        authored = e["props"]["MusicName"]
        if authored.startswith(mixdown.SILENCE_PREFIX):
            self.skipTest("this scene's cue is a stop, not a track")
        key = self.event_cue_key(seq, e)
        state = with_cue_moves(empty_edits(), [(key, CueMove(
            seq=seq, clip="BGM", tick=e["tick"], new_tick=e["tick"] + 40000,
            match={"MusicName": authored}))])
        item = self._bgm_item(cs, state)
        # exactly what the window does when the picker is accepted
        state = with_music_repointed(state, self.authored_key(item), MusicRepoint(
            seq=item.seq or seq,
            tick=item.moved_from if item.moved_from is not None else item.tick_start,
            frm=authored, to="bgm_Corle_000"))
        items, _d, _m, repointed = mixdown.placements(cs, state)
        self.assertEqual(repointed, 1)
        names = [p.name for p in items if p.kind == "bgm"]
        self.assertIn("bgm_Corle_000", names)
        self.assertNotIn(authored, names)


class MusicInThePreviewMix(unittest.TestCase):
    """What the editor plays has to be what the build will produce.

    `placements` is the whole answer to "why does the viewer still play the old
    track" - the mix is built from cue names, and a repoint changes one.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = library()
        cls.EV = "EV_GRASE_0010"
        if not os.path.isfile(cls.lib.path_for(cls.EV)):
            raise unittest.SkipTest("no timeline for %s" % cls.EV)
        cls.cs = cls.lib.load_cutscene(cls.EV)

    def _music_cue(self):
        for seq in mixdown.SE_GROUPS:
            for e in self.cs.events(seq):
                if (e.get("props") or {}).get("MusicName"):
                    return seq, e
        raise unittest.SkipTest("%s has no music cue" % self.EV)

    def _key_and_name(self):
        from editor_qt.core.cues import event_cue_key

        seq, e = self._music_cue()
        return event_cue_key(seq, e), e["props"]["MusicName"]

    def _bgm(self, state):
        items, _d, _m, repointed = mixdown.placements(self.cs, state)
        return [p for p in items if p.kind == "bgm"], repointed

    def test_the_mix_plays_the_track_the_trigger_was_pointed_at(self) -> None:
        key, authored = self._key_and_name()
        if authored.startswith(mixdown.SILENCE_PREFIX):
            self.skipTest("this scene's cue is a stop, not a track")
        before, _ = self._bgm(empty_edits())
        self.assertIn(authored, [p.name for p in before])

        state = with_music_repointed(empty_edits(), key, MusicRepoint(
            seq="ManualSE", tick=0, frm=authored, to="bgm_Corle_000"))
        after, repointed = self._bgm(state)
        self.assertEqual(repointed, 1)
        self.assertIn("bgm_Corle_000", [p.name for p in after])
        self.assertNotIn(authored, [p.name for p in after])
        # and it keeps its place and its length
        self.assertEqual([p.tick for p in after], [p.tick for p in before])
        self.assertEqual([p.max_sec for p in after], [p.max_sec for p in before])

    def test_pointing_a_cue_at_silence_stops_the_music(self) -> None:
        """`bgm_silence` is how the game says stop. Repointing to it has to
        make the preview stop too - otherwise the edit sounds like nothing
        happened, which is the exact complaint this all started from."""
        key, authored = self._key_and_name()
        state = with_music_repointed(empty_edits(), key, MusicRepoint(
            seq="ManualSE", tick=0, frm=authored, to="bgm_silence"))
        after, repointed = self._bgm(state)
        self.assertEqual(repointed, 1)
        self.assertEqual(after, [])

    def test_a_stop_cue_ends_the_track_before_it(self) -> None:
        """A silence cue places nothing but is still an edge: the track before
        it has to be cut off there rather than playing straight through."""
        ticks = self.cs.time.ticks_per_second
        state = empty_edits()
        items, _d, _m, _r = mixdown.placements(self.cs, state)
        music = [p for p in items if p.kind == "bgm"]
        if not music:
            self.skipTest("no music in this scene")
        for p in music:
            self.assertLessEqual(p.tick + p.max_sec * ticks, self.cs.total + 1)

    def test_the_render_is_not_served_from_a_stale_cache(self) -> None:
        """The mix is named after its edit. A repoint that did not change the
        name would hand back the previous render and play the old track."""
        key, authored = self._key_and_name()
        plain = mixdown.edit_fingerprint(self.cs, empty_edits(), "US")
        state = with_music_repointed(empty_edits(), key, MusicRepoint(
            seq="ManualSE", tick=0, frm=authored, to="bgm_Corle_000"))
        moved = mixdown.edit_fingerprint(self.cs, state, "US")
        self.assertNotEqual(plain, moved)
        other = with_music_repointed(empty_edits(), key, MusicRepoint(
            seq="ManualSE", tick=0, frm=authored, to="bgm_Corle_002"))
        self.assertNotEqual(moved, mixdown.edit_fingerprint(self.cs, other, "US"))


def _a_scene_only_the_tag_can_address():
    """A scene whose music cue the compiled-block walk cannot find.

    53 of this game's 645 music cues are like this: the payload is in the file
    but the Times array behind it cannot be located, so there is no way to
    address the cue by time. `patcher.music_name_spans` is the answer and this
    finds a real one to point it at.
    """
    if not os.path.isdir(CONTENT) or not os.path.isdir(TIMELINES):
        return None
    import patcher as _p

    for path in sorted(glob.glob(os.path.join(TIMELINES, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tl = json.load(f)
        except Exception:
            continue
        ev, area = tl.get("cutscene"), tl.get("area")
        if not ev or not area:
            continue
        for seq in ("ManualSE", "Sound"):
            cues = [e for e in (tl.get("events") or {}).get(seq, [])
                    if (e.get("props") or {}).get("MusicName")]
            if not cues:
                continue
            asset = os.path.join(CONTENT, "Cut", "Game", area, ev,
                                 "%s_%s.uasset" % (ev, seq))
            if not os.path.isfile(asset):
                continue
            with open(asset, "rb") as f:
                raw = f.read()
            by_block = set()
            for _t, _tick, pos, size in _p.compiled_event_blocks(raw, 10 ** 9):
                for _o, _l, _k, val in _p.payload_name_fields(
                        raw, pos, size, ("MusicName",)):
                    by_block.add(val)
            for e in cues:
                name = e["props"]["MusicName"]
                if name not in by_block and any(
                        v == name for _o, _l, v in _p.music_name_spans(raw)):
                    return ev, seq, asset, name, e.get("tick") or 0
    return None


@unittest.skipUnless(_a_scene_with_music(), "no exported cutscene with a BGM cue")
class MusicNameSpans(unittest.TestCase):
    """The property-tag scan, against the compiled-block walk it backs up."""

    def test_it_agrees_with_the_block_walk_where_both_can_look(self) -> None:
        import patcher

        _ev, _seq, asset, name, _tick = _a_scene_with_music()
        with open(asset, "rb") as f:
            raw = f.read()
        by_block = set()
        for _t, _tick2, pos, size in patcher.compiled_event_blocks(raw, 10 ** 9):
            for _o, _l, _k, val in patcher.payload_name_fields(
                    raw, pos, size, ("MusicName",)):
                by_block.add(val)
        by_tag = {v for _o, _l, v in patcher.music_name_spans(raw)}
        self.assertIn(name, by_tag)
        # the tag scan sees everything the block walk sees, and sometimes more
        self.assertTrue(by_block <= by_tag, by_block - by_tag)

    def test_the_spans_it_reports_are_the_names_themselves(self) -> None:
        import patcher

        _ev, _seq, asset, _name, _tick = _a_scene_with_music()
        with open(asset, "rb") as f:
            raw = f.read()
        for off, length, val in patcher.music_name_spans(raw):
            self.assertEqual(raw[off:off + length].split(b"\0")[0].decode(), val)
            self.assertLessEqual(len(val), length)


@unittest.skipUnless(_a_scene_only_the_tag_can_address(),
                     "every exported music cue is addressable by time")
class MusicRepointWithoutATick(unittest.TestCase):
    """The 8% of cues the block walk cannot reach still get repointed."""

    def setUp(self) -> None:
        import shutil

        import patcher

        self.patcher = patcher
        self.ev, self.seq, self.asset, self.name, self.tick = \
            _a_scene_only_the_tag_can_address()
        self.tmp = tempfile.TemporaryDirectory()
        shutil.copy2(self.asset,
                     os.path.join(self.tmp.name, os.path.basename(self.asset)))
        with open(self.asset, "rb") as f:
            self.original = f.read()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, items):
        return self.patcher.repoint_music(
            self.tmp.name, self.ev, items,
            self.patcher.Remap([], 10 ** 9), 10 ** 9)

    def test_it_falls_back_to_the_property_tag(self) -> None:
        to = "bgm_" + "z" * max(1, len(self.name) - 4)
        n, notes, problems = self._run(
            [{"seq": self.seq, "tick": self.tick, "from": self.name, "to": to}])
        self.assertGreater(n, 0, problems)
        self.assertIn("property tag", " ".join(notes))
        after = open(os.path.join(self.tmp.name,
                                  os.path.basename(self.asset)), "rb").read()
        self.assertEqual(len(after), len(self.original))
        self.assertIn(to.encode(), after)

    def test_two_repoints_of_one_name_are_refused_rather_than_guessed(self) -> None:
        """Without a tick there is no telling the copies apart, so a plan that
        sends the same name two ways gets a refusal, not a coin toss."""
        n, _notes, problems = self._run([
            {"seq": self.seq, "tick": self.tick, "from": self.name, "to": "bgm_a"},
            {"seq": self.seq, "tick": self.tick + 1, "from": self.name, "to": "bgm_b"},
        ])
        self.assertEqual(n, 0)
        self.assertTrue(any("refusing to guess" in p for p in problems), problems)
        after = open(os.path.join(self.tmp.name,
                                  os.path.basename(self.asset)), "rb").read()
        self.assertEqual(after, self.original)


@unittest.skipUnless(_a_scene_with_music(), "no exported cutscene with a BGM cue")
class MusicRepointBytes(unittest.TestCase):
    """The patch itself, against a real asset.

    This is the test that matters, because everything above it is bookkeeping
    and this is the part that writes to a file the game loads. Three claims:
    the file comes out **exactly** the size it went in, only the name's own
    bytes change, and the parsers read the new name back.
    """

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        cls.patcher = patcher
        cls.ev, cls.seq, cls.asset, cls.name, cls.tick = _a_scene_with_music()

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.staged = os.path.join(self.tmp.name, self.ev + "_" + self.seq + ".uasset")
        import shutil

        shutil.copy2(self.asset, os.path.join(
            self.tmp.name, os.path.basename(self.asset)))
        self.dir = self.tmp.name
        self.original = open(self.asset, "rb").read()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, to: str):
        return self.patcher.repoint_music(
            self.dir, self.ev,
            [{"seq": self.seq, "tick": self.tick, "from": self.name, "to": to}],
            self.patcher.Remap([], 10 ** 9), 10 ** 9)

    def _patched(self) -> bytes:
        return open(os.path.join(self.dir, os.path.basename(self.asset)), "rb").read()

    #: A stand-in target: the same length as whatever this scene's cue is
    #: called, so it always fits, and never equal to it — the first scene the
    #: search finds turned out to play `bgm_silence`, and a test that renames a
    #: cue to what it already says proves nothing at all.
    @property
    def stand_in(self) -> str:
        return "bgm_" + "z" * max(1, len(self.name) - 4)

    def test_a_shorter_name_lands_and_the_file_does_not_move(self) -> None:
        short = self.stand_in
        self.assertNotEqual(short, self.name)
        n, notes, problems = self._run(short)
        self.assertGreater(n, 0, notes)
        self.assertEqual(problems, [])
        after = self._patched()
        self.assertEqual(len(after), len(self.original),
                         "an in-place patch that changed the file size")
        # only inside the name's own span
        differ = [i for i, (a, b) in enumerate(zip(self.original, after)) if a != b]
        self.assertTrue(differ)
        for i in differ:
            span = self.original[max(0, i - len(self.name)):i + len(self.name)]
            self.assertIn(self.name.encode(), span,
                          "byte %d is nowhere near a music name" % i)

    def test_the_new_name_reads_back(self) -> None:
        short = self.stand_in
        self._run(short)
        from payload_events import extract_events

        names = {(e.get("props") or {}).get("MusicName")
                 for e in extract_events(
                     os.path.join(self.dir, os.path.basename(self.asset)))}
        self.assertIn(short, names)
        # the old name may legitimately survive elsewhere in the file - two
        # cues can play the same track - but not at the tick we just patched
        self.assertNotIn(self.name, names)

    def test_a_much_shorter_name_is_padded_out_with_nuls(self) -> None:
        """The case a same-length rename does not exercise. The length prefix
        and the property tag size stay as they were, so every offset after the
        name is untouched and the readers stop at the first NUL."""
        short = "bgm_z"
        if len(short) >= len(self.name):
            self.skipTest("%s has no room to shorten" % self.name)
        n, _notes, problems = self._run(short)
        self.assertGreater(n, 0, problems)
        after = self._patched()
        self.assertEqual(len(after), len(self.original))
        self.assertIn((short + "\0" * (len(self.name) - len(short))).encode(),
                      after)
        from payload_events import extract_events

        names = {(e.get("props") or {}).get("MusicName")
                 for e in extract_events(
                     os.path.join(self.dir, os.path.basename(self.asset)))}
        self.assertIn(short, names)

    def test_a_longer_name_is_refused_and_nothing_is_written(self) -> None:
        n, _notes, problems = self._run(self.name + "_and_then_some")
        self.assertEqual(n, 0)
        self.assertTrue(problems)
        self.assertIn("room for", " ".join(problems))
        self.assertEqual(self._patched(), self.original)

    def test_a_name_the_cue_does_not_carry_is_refused(self) -> None:
        """Identity is the name as well as the tick, so a plan cannot overwrite
        whatever cue happens to sit at that moment now."""
        n, _notes, problems = self.patcher.repoint_music(
            self.dir, self.ev,
            [{"seq": self.seq, "tick": self.tick,
              "from": "bgm_not_the_one", "to": "bgm_x"}],
            self.patcher.Remap([], 10 ** 9), 10 ** 9)
        self.assertEqual(n, 0)
        self.assertTrue(problems)
        self.assertEqual(self._patched(), self.original)

    def test_the_editor_and_the_patcher_agree_about_the_room(self) -> None:
        """`music.capacity_of` is what the picker greys rows out with, and the
        patcher measures the real span. If the two ever disagreed the window
        would offer a name the build then refused."""
        exactly = "x" * capacity_of(self.name)
        n, _notes, problems = self._run(exactly)
        self.assertGreater(n, 0, problems)
        self.assertEqual(problems, [])
        one_more = "x" * (capacity_of(self.name) + 1)
        self.setUp()   # fresh copy
        n, _notes, problems = self._run(one_more)
        self.assertEqual(n, 0)
        self.assertTrue(problems)


def _text_asset(ev, area):
    p = os.path.join(CONTENT, "Cut", "Game", area, ev, "%s_Text.uasset" % ev)
    return p if os.path.isfile(p) else None


def _a_scene_with_a_multilanguage_line():
    """(ev, asset, label, [on ticks]) for a line that exists in more than one
    language. 44 of the game's 9,806 lines do; they are the reason a caption
    cannot be switched off at a single tick."""
    if not os.path.isdir(CONTENT) or not os.path.isdir(TIMELINES):
        return None
    for path in sorted(glob.glob(os.path.join(TIMELINES, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tl = json.load(f)
        except Exception:
            continue
        ev, area = tl.get("cutscene"), tl.get("area")
        if not ev or not area:
            continue
        by_label = {}
        for e in (tl.get("events") or {}).get("Text", []):
            p = e.get("props") or {}
            if not p.get("TextLabel") or e.get("tick") is None or not p.get("Enable"):
                continue
            by_label.setdefault(p["TextLabel"], {})[p.get("Language")] = e["tick"]
        for label, langs in sorted(by_label.items()):
            if len(langs) < 2:
                continue
            asset = _text_asset(ev, area)
            if asset:
                return ev, asset, label, sorted(langs.values())
    return None


def _a_scene_with_a_reused_label():
    """(ev, asset, label, [on ticks]) for a label used twice in one scene.
    176 labels are. They are the reason a caption cannot be switched off by
    label alone either."""
    if not os.path.isdir(CONTENT) or not os.path.isdir(TIMELINES):
        return None
    for path in sorted(glob.glob(os.path.join(TIMELINES, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tl = json.load(f)
        except Exception:
            continue
        ev, area = tl.get("cutscene"), tl.get("area")
        if not ev or not area:
            continue
        by_key = {}
        for e in (tl.get("events") or {}).get("Text", []):
            p = e.get("props") or {}
            if not p.get("TextLabel") or e.get("tick") is None or not p.get("Enable"):
                continue
            by_key.setdefault((p["TextLabel"], p.get("Language")), set()).add(e["tick"])
        for (label, _lang), ticks in sorted(by_key.items()):
            if len(ticks) < 2:
                continue
            asset = _text_asset(ev, area)
            if asset:
                return ev, asset, label, sorted(ticks)
    return None


@unittest.skipUnless(os.path.isdir(CONTENT), "no Content folder")
class SubtitlesAreSwitchedOffByTheirFlag(unittest.TestCase):
    """Breaking a name buys silence from a sound and gibberish from a caption.

    A sound whose name no longer resolves plays nothing, which is the whole
    mechanism `disable_cues` rests on. A caption whose label no longer resolves
    still gets drawn - the broken label is what ends up on screen - so the same
    edit that switches a sound off turns a subtitle into garbage rather than
    removing it. `Enable` is the flag that actually means "do not raise this",
    and these tests hold the patcher to using it.
    """

    EV = "EV_FOREE_8514"
    AREA = "8800-FOREE"

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        warnings.simplefilter("ignore", ResourceWarning)
        cls.patcher = patcher
        cls.asset = _text_asset(cls.EV, cls.AREA)

    def setUp(self) -> None:
        if not self.asset:
            self.skipTest("%s not exported" % self.EV)
        with open(self.asset, "rb") as f:
            self.raw = f.read()
        self.blocks = self.patcher.compiled_event_blocks(self.raw, 10 ** 9)

    def _switches(self, label=None):
        return self.patcher.subtitle_switches(self.raw, self.blocks, label)

    def test_every_caption_carries_the_flag(self) -> None:
        """The premise. If a payload without `Enable` ever turns up, switching
        it off needs a different answer - and it must be measured, not
        assumed."""
        labelled = 0
        for _t, _tick, pos, size in self.blocks:
            for key, typ, _v, _o in self.patcher.payload_all_fields(
                    self.raw, pos, size):
                if key == "TextLabel" and typ != "BoolProperty":
                    labelled += 1
        self.assertGreater(labelled, 0)
        self.assertEqual(len(self._switches()), labelled)

    def test_a_line_is_raised_and_dropped_in_pairs(self) -> None:
        raised = [s for s in self._switches() if s[2]]
        dropped = [s for s in self._switches() if not s[2]]
        self.assertEqual(len(raised), len(dropped))

    def test_the_flag_sits_where_the_walk_says_it_does(self) -> None:
        """The offsets are written to directly, so they have to be the byte the
        walk read - not one before or after it."""
        for _toff, _tick, raises, off in self._switches():
            self.assertEqual(bool(self.raw[off]), raises)

    def test_clearing_a_line_leaves_the_file_the_same_size(self) -> None:
        data = bytearray(self.raw)
        label = self._switches()[0]
        lab = self._label_of(label[0])
        self.patcher.clear_subtitle(data, self.blocks, lab, label[1])
        self.assertEqual(len(data), len(self.raw))

    def _label_of(self, want_toff):
        for toff, _tick, pos, size in self.blocks:
            if toff != want_toff:
                continue
            for key, typ, val, _o in self.patcher.payload_all_fields(
                    self.raw, pos, size):
                if key == "TextLabel" and typ != "BoolProperty":
                    return val
        return None

    def test_the_label_is_never_touched(self) -> None:
        """The rename is the bug. A cleared caption keeps the name it was
        authored with - its own "off" payload is matched by that name, and
        nothing looks the name up once the caption is never raised."""
        data = bytearray(self.raw)
        for toff, tick, raises, _off in self._switches():
            if raises:
                self.patcher.clear_subtitle(
                    data, self.blocks, self._label_of(toff), tick)
        self.assertNotIn(b"CUT_", bytes(data))
        # every byte outside the flags themselves is identical
        before, after = bytearray(self.raw), bytearray(data)
        for _toff, _tick, _r, off in self._switches():
            before[off] = after[off] = 0
        self.assertEqual(bytes(before), bytes(after))

    def test_clearing_every_line_raises_none_of_them(self) -> None:
        data = bytearray(self.raw)
        for toff, tick, raises, _off in self._switches():
            if raises:
                self.patcher.clear_subtitle(
                    data, self.blocks, self._label_of(toff), tick)
        left = [s for s in self.patcher.subtitle_switches(
            bytes(data), self.blocks) if s[2]]
        self.assertEqual(left, [])


@unittest.skipUnless(_a_scene_with_a_multilanguage_line(),
                     "no exported scene has a line in more than one language")
class SwitchingOffAllOfALine(unittest.TestCase):
    """A line read in three languages is three "on" payloads at three ticks.

    `$C3510_MAIN_3100_1800_00_sep` in EV_FOREE_8514 opens at 2962400 in
    Japanese, 3001600 in English and 3003200 in German. Clearing the one tick
    the plan carries switches the caption off for a Japanese player and leaves
    it on screen for everyone else - a bug that would never show up in the
    language the editor happened to pair.
    """

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        warnings.simplefilter("ignore", ResourceWarning)
        cls.patcher = patcher
        cls.ev, cls.asset, cls.label, cls.ticks = _a_scene_with_a_multilanguage_line()

    def setUp(self) -> None:
        with open(self.asset, "rb") as f:
            self.raw = f.read()
        self.blocks = self.patcher.compiled_event_blocks(self.raw, 10 ** 9)

    def test_the_variants_really_do_sit_at_different_ticks(self) -> None:
        self.assertGreater(len(self.ticks), 1)
        self.assertGreater(len(set(self.ticks)), 1)

    def test_they_are_read_as_one_line(self) -> None:
        lines = self.patcher.subtitle_lines(self.raw, self.blocks, self.label)
        holding = [ln for ln in lines if ln[0] <= self.ticks[0] <= ln[1]]
        self.assertEqual(len(holding), 1)
        for t in self.ticks:
            self.assertTrue(holding[0][0] <= t <= holding[0][1],
                            "%d outside %r" % (t, holding[0][:2]))

    def test_switching_it_off_at_one_tick_clears_every_language(self) -> None:
        data = bytearray(self.raw)
        self.patcher.clear_subtitle(data, self.blocks, self.label, self.ticks[0])
        left = [s for s in self.patcher.subtitle_switches(
            bytes(data), self.blocks, self.label) if s[2]]
        self.assertEqual(left, [], "a language variant was left raised")

    def test_it_clears_both_copies(self) -> None:
        """Every payload exists twice - in its section export and in the
        compiled template, which is the one a shipping build evaluates."""
        raised = [s for s in self.patcher.subtitle_switches(
            self.raw, self.blocks, self.label) if s[2]]
        self.assertGreaterEqual(len(raised), 2 * len(set(self.ticks)))
        data = bytearray(self.raw)
        n = self.patcher.clear_subtitle(data, self.blocks, self.label, self.ticks[0])
        self.assertEqual(n, len(raised))


@unittest.skipUnless(_a_scene_with_a_reused_label(),
                     "no exported scene uses one label twice")
class SwitchingOffOnlyOneUseOfALabel(unittest.TestCase):
    """176 labels are used more than once in their own scene.

    Which is why a caption cannot simply be cleared by name: switching off the
    first use would take the second with it. Two uses never overlap - 0 of 86
    consecutive pairs - so the count of raised captions returning to zero is
    what separates them.
    """

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        warnings.simplefilter("ignore", ResourceWarning)
        cls.patcher = patcher
        cls.ev, cls.asset, cls.label, cls.ticks = _a_scene_with_a_reused_label()

    def setUp(self) -> None:
        with open(self.asset, "rb") as f:
            self.raw = f.read()
        self.blocks = self.patcher.compiled_event_blocks(self.raw, 10 ** 9)

    def test_the_uses_are_read_as_separate_lines(self) -> None:
        lines = self.patcher.subtitle_lines(self.raw, self.blocks, self.label)
        self.assertGreaterEqual(len(lines), 2)
        for a, b in zip(lines, lines[1:]):
            self.assertLessEqual(a[1], b[0], "two uses of a label overlap")

    def test_a_use_is_found_by_the_tick_it_raises_at(self) -> None:
        """Two uses can meet exactly end to start, and a tick on that seam sits
        inside both ranges. The raise is what tells them apart."""
        lines = self.patcher.subtitle_lines(self.raw, self.blocks, self.label)
        for start, _end, _offsets, ticks in lines:
            self.assertIn(start, ticks)
        seams = [b for a, b in zip(lines, lines[1:]) if a[1] == b[0]]
        for b in seams:
            data = bytearray(self.raw)
            self.patcher.clear_subtitle(data, self.blocks, self.label, b[0])
            for a, _b2 in [(a, b2) for a, b2 in zip(lines, lines[1:])
                           if b2[0] == b[0]]:
                self.assertTrue(all(data[o] for o in a[2]),
                                "the line before the seam was cleared too")

    def test_switching_one_off_leaves_the_other_alone(self) -> None:
        data = bytearray(self.raw)
        self.patcher.clear_subtitle(data, self.blocks, self.label, self.ticks[0])
        left = {s[1] for s in self.patcher.subtitle_switches(
            bytes(data), self.blocks, self.label) if s[2]}
        self.assertNotIn(self.ticks[0], left)
        for t in self.ticks[1:]:
            self.assertIn(t, left, "a later use of the label was cleared too")


@unittest.skipUnless(_a_scene_with_a_multilanguage_line(),
                     "no exported scene has a line in more than one language")
class DisablingASubtitleEndToEnd(unittest.TestCase):
    """Through `disable_cues`, the way a build reaches it."""

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        warnings.simplefilter("ignore", ResourceWarning)
        cls.patcher = patcher
        cls.ev, cls.asset, cls.label, cls.ticks = _a_scene_with_a_multilanguage_line()

    def setUp(self) -> None:
        import shutil

        self.tmp = tempfile.TemporaryDirectory()
        self.staged = os.path.join(self.tmp.name, "%s_Text.uasset" % self.ev)
        shutil.copy2(self.asset, self.staged)
        with open(self.asset, "rb") as f:
            self.original = f.read()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self):
        return self.patcher.disable_cues(
            self.tmp.name, self.ev,
            [{"seq": "Text", "tick": self.ticks[0],
              "field": "TextLabel", "value": self.label}],
            self.patcher.Remap([], 10 ** 9), 10 ** 9)

    def _patched(self):
        with open(self.staged, "rb") as f:
            return f.read()

    def test_it_clears_the_line(self) -> None:
        n, notes = self._run()
        self.assertGreater(n, 0, notes)
        raw = self._patched()
        blocks = self.patcher.compiled_event_blocks(raw, 10 ** 9)
        left = [s for s in self.patcher.subtitle_switches(raw, blocks, self.label)
                if s[2]]
        self.assertEqual(left, [])

    def test_it_does_not_break_the_name(self) -> None:
        self._run()
        raw = self._patched()
        self.assertNotIn(b"CUT_", raw)
        self.assertIn(self.label.encode("latin1"), raw)

    def test_it_is_still_an_in_place_patch(self) -> None:
        self._run()
        self.assertEqual(len(self._patched()), len(self.original))

    def test_only_the_flag_bytes_move(self) -> None:
        self._run()
        raw = self._patched()
        differing = [i for i in range(len(raw)) if raw[i] != self.original[i]]
        blocks = self.patcher.compiled_event_blocks(self.original, 10 ** 9)
        flags = {off for _t, _tick, _r, off
                 in self.patcher.subtitle_switches(self.original, blocks, self.label)}
        self.assertTrue(set(differing) <= flags,
                        "bytes changed outside the Enable flags")


@unittest.skipUnless(os.path.isdir(CONTENT) and os.path.isfile(USMAP),
                     "no Content folder")
class CaptionsTheCutSwallowed(unittest.TestCase):
    """A caption inside a removed range outlives the footage it belonged to.

    Only its "on" event is inside the cut, so that lands on the join while the
    matching "off" survives untouched further down the timeline - the line for
    footage that is no longer there sits over whatever follows until the moment
    it was originally due to end. `SILENCE_KEYS` never covered this, because it
    only knows how to break names and a caption is not switched off by its
    name.
    """

    EV = "EV_FOREE_8514"
    AREA = "8800-FOREE"

    @classmethod
    def setUpClass(cls) -> None:
        import patcher

        cls.patcher = patcher
        cls.asset = _text_asset(cls.EV, cls.AREA)
        cls.usmap = patcher.Usmap(USMAP) if cls.asset else None

    def setUp(self) -> None:
        if not self.asset:
            self.skipTest("%s not exported" % self.EV)
        with open(self.asset, "rb") as f:
            self.raw = f.read()
        self.blocks = self.patcher.compiled_event_blocks(self.raw, 10 ** 9)
        self.raised = sorted({s[1] for s in self.patcher.subtitle_switches(
            self.raw, self.blocks) if s[2]})
        self.tmp = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.tmp.name, "%s_Text.uasset" % self.EV)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _build(self, removes):
        remap = self.patcher.Remap(removes, 10 ** 9)
        report = {}
        self.patcher.patch_file(self.asset, self.out, remap, self.usmap,
                                10 ** 9, report)
        with open(self.out, "rb") as f:
            return remap, report, f.read()

    def _a_cut_over_one_caption(self):
        """A removed range holding exactly one caption's "on" event."""
        t = self.raised[len(self.raised) // 2]
        return t, (t - 800, t + 800)

    def test_a_swallowed_caption_is_never_raised(self) -> None:
        t, cut = self._a_cut_over_one_caption()
        remap, report, got = self._build([cut])
        self.assertEqual(len(got), len(self.raw))
        self.assertIn("cutSubtitles", report, report)
        blocks = self.patcher.compiled_event_blocks(got, 10 ** 9)
        at_join = remap.point(t)
        still = [s for s in self.patcher.subtitle_switches(got, blocks)
                 if s[2] and s[1] == at_join]
        self.assertEqual(still, [], "a caption from removed footage still fires")

    def test_captions_outside_the_cut_are_left_alone(self) -> None:
        t, cut = self._a_cut_over_one_caption()
        remap, _report, got = self._build([cut])
        blocks = self.patcher.compiled_event_blocks(got, 10 ** 9)
        left = {s[1] for s in self.patcher.subtitle_switches(got, blocks) if s[2]}
        for other in self.raised:
            if cut[0] <= other < cut[1]:
                continue
            self.assertIn(remap.point(other), left,
                          "a caption outside the cut stopped being raised")

    def test_the_label_is_still_not_touched(self) -> None:
        _t, cut = self._a_cut_over_one_caption()
        _remap, _report, got = self._build([cut])
        self.assertNotIn(b"CUT_", got)

    def test_a_scene_with_no_cut_is_untouched(self) -> None:
        """Parity: the pass must do nothing where there is nothing to do."""
        _remap, report, got = self._build([])
        self.assertNotIn("cutSubtitles", report)
        blocks = self.patcher.compiled_event_blocks(got, 10 ** 9)
        left = {s[1] for s in self.patcher.subtitle_switches(got, blocks) if s[2]}
        self.assertEqual(left, set(self.raised))


class SubtitlePairing(unittest.TestCase):
    """One block per line on screen, whatever languages it is read in.

    Pairing on the label alone walks straight through a line that has
    per-language variants: the German "on" is still open when the Japanese
    "off" arrives, so those two get paired with each other and the events left
    over are dropped. The block the editor draws is then one variant's range
    and the rest have no block at all.
    """

    def _ev(self, tick, label, enable, lang="EEndCutLangType::JP", **extra):
        """`text` and `actor` sit on the event, not in its props - that is
        where `extract_timeline` attaches them from the subtitle manifest."""
        e = {"tick": tick,
             "props": {"TextLabel": label, "Language": lang, "Enable": enable}}
        e.update(extra)
        return e

    def test_a_plain_line_is_one_range(self) -> None:
        got = pair_subtitles([
            self._ev(100, "$a", True, text="hello", actor="Cloud"),
            self._ev(200, "$a", False),
        ])
        self.assertEqual(len(got), 1)
        self.assertEqual((got[0]["start"], got[0]["end"]), (100, 200))
        self.assertEqual(got[0]["actor"], "Cloud")

    def test_language_variants_merge_into_one(self) -> None:
        got = pair_subtitles([
            self._ev(100, "$a", True, "EEndCutLangType::JP", text="konnichiwa"),
            self._ev(140, "$a", True, "EEndCutLangType::US", text="hello"),
            self._ev(200, "$a", False, "EEndCutLangType::JP"),
            self._ev(230, "$a", False, "EEndCutLangType::US"),
        ])
        self.assertEqual(len(got), 1)
        self.assertEqual((got[0]["start"], got[0]["end"]), (100, 230))

    def test_pairing_by_label_alone_would_have_lost_events(self) -> None:
        """The bug this replaced, stated as a fact about the input rather than
        about the old code: the two languages interleave."""
        evs = [
            self._ev(100, "$a", True, "EEndCutLangType::JP"),
            self._ev(140, "$a", True, "EEndCutLangType::US"),
            self._ev(200, "$a", False, "EEndCutLangType::JP"),
            self._ev(230, "$a", False, "EEndCutLangType::US"),
        ]
        ticks = [e["tick"] for e in evs]
        self.assertEqual(ticks, sorted(ticks))
        self.assertTrue(evs[1]["tick"] < evs[2]["tick"])

    def test_two_uses_of_a_label_stay_apart(self) -> None:
        got = pair_subtitles([
            self._ev(100, "$a", True),
            self._ev(200, "$a", False),
            self._ev(900, "$a", True),
            self._ev(950, "$a", False),
        ])
        self.assertEqual([(r["start"], r["end"]) for r in got],
                         [(100, 200), (900, 950)])

    def test_uses_meeting_end_to_start_stay_apart(self) -> None:
        got = pair_subtitles([
            self._ev(100, "$a", True),
            self._ev(200, "$a", False),
            self._ev(200, "$a", True),
            self._ev(300, "$a", False),
        ])
        self.assertEqual(len(got), 2)

    def test_ranges_come_back_in_time_order(self) -> None:
        got = pair_subtitles([
            self._ev(900, "$b", True),
            self._ev(950, "$b", False),
            self._ev(100, "$a", True),
            self._ev(200, "$a", False),
        ])
        self.assertEqual([r["label"] for r in got], ["$a", "$b"])


@unittest.skipUnless(os.path.isdir(TIMELINES), "no timelines extracted")
class ARescueNeverCrossesItsArrayNeighbour(unittest.TestCase):
    """`collapse._array_floor` — the planner learns the rule the build enforces.

    A cue fires at an int32 in a shared, sorted `Times` array, so
    `patcher.check_relocation_order` drops any move that would unsort one. The
    automatic rescue never knew that. It measured distance from the end and
    handed back a tick, and where the two disagreed the patcher won silently:
    the cue was remapped onto the join, the plan went on claiming it would be
    somewhere else, and `build_mod.verify` failed a build whose bytes were fine.

    EV_GRASE_2280 is the scene that showed it. `Sky_Grass` is hidden at 0, shown
    at 1466400 and hidden again at 1760800 — one array of three — and a 24.1s
    tail cut starting on that last hide asked for it at 389600, in front of its
    own show. Built, it came back as ``relocatedCues 2 placed, 2 missing``.

    These tests read the real arrays out of the real assets, so they check the
    editor's answer against the constraint the build actually applies rather
    than against a restatement of it.
    """

    EV = "EV_GRASE_2280"
    CUTS = (CutSpan(648000, 1440800), CutSpan(1760800, 2339200))
    HIDE = 1760800          # the last Sky_Grass hide: first tick of the tail cut
    SHOW = 1466400          # the Sky_Grass show it must not overtake
    NEW_END = 968000

    @classmethod
    def setUpClass(cls) -> None:
        lib = library()
        if not os.path.isfile(lib.path_for(cls.EV)):
            raise unittest.SkipTest("%s not extracted" % cls.EV)
        cls.cs = lib.load_cutscene(cls.EV)
        cls.index = arrays.load(CONTENT, cls.cs.area, cls.EV, cls.cs.total)

    def state(self) -> EditState:
        return EditState(cuts=self.CUTS)

    def _hide(self, plan):
        for r in plan.relocations:
            if r.seq == "Light" and r.tick == self.HIDE:
                return r
        return None

    def test_the_scene_still_has_the_array_this_rests_on(self) -> None:
        if self.index is None:
            self.skipTest("Content not beside this checkout")
        for arr in self.index.arrays_for("Light"):
            if self.HIDE in arr:
                self.assertEqual(arr, [0, self.SHOW, self.HIDE])
                return
        self.fail("no Light array holds %d" % self.HIDE)

    def test_without_the_arrays_it_plans_the_move_the_build_refuses(self) -> None:
        """Not an endorsement — this is the bug, pinned, so the fix is visible.

        With no index there is nothing to prove the move illegal, and the
        behaviour is deliberately exactly what shipped.
        """
        _applied, plan = effective(self.cs, self.state())
        r = self._hide(plan)
        self.assertIsNotNone(r)
        self.assertEqual(r.new_tick, 389600)
        self.assertLess(r.new_tick, to_edited(self.state(), self.SHOW))

    def test_with_the_arrays_it_fires_at_the_join_instead(self) -> None:
        if self.index is None:
            self.skipTest("Content not beside this checkout")
        _applied, plan = effective(self.cs, self.state(), self.index)
        r = self._hide(plan)
        self.assertIsNotNone(r)
        self.assertEqual(r.new_tick, self.NEW_END)
        self.assertGreaterEqual(r.new_tick, to_edited(self.state(), self.SHOW))

    def test_the_join_is_where_the_patcher_would_have_put_it_anyway(self) -> None:
        """So the fix changes what the plan SAYS, not what the game gets.

        That is the whole claim: the build was already doing the right thing by
        refusing, and the only casualty was the verification.
        """
        if self.index is None:
            self.skipTest("Content not beside this checkout")
        _applied, plan = effective(self.cs, self.state(), self.index)
        r = self._hide(plan)
        removed = sum(b - a for a, b in
                      ((c.a, c.b) for c in normalise_cuts(self.CUTS))
                      if b <= self.HIDE)
        join = self.CUTS[1].a - sum(c.b - c.a for c in self.CUTS if c.b <= self.CUTS[1].a)
        self.assertEqual(r.new_tick, join)
        self.assertEqual(removed, self.CUTS[0].b - self.CUTS[0].a)

    def test_every_array_comes_out_sorted(self) -> None:
        """`check_relocation_order`'s rule, applied to the editor's answer.

        Swept over every saved plan's scene rather than only this one, because
        a planner that satisfies the constraint on the scene it was written for
        and breaks it elsewhere is the failure this is here to catch.
        """
        if not os.path.isdir(PLANS):
            self.skipTest("no saved plans")
        lib = library()
        checked = 0
        for path in sorted(glob.glob(os.path.join(PLANS, "*_editplan.json"))):
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            ev = saved.get("cutscene")
            ranges = saved.get("removeRanges") or []
            if not ev or not ranges or not os.path.isfile(lib.path_for(ev)):
                continue
            cs = lib.load_cutscene(ev)
            index = arrays.load(CONTENT, cs.area, ev, cs.total)
            if index is None:
                continue
            state = EditState(cuts=tuple(CutSpan(a, b) for a, b in ranges))
            _applied, plan = effective(cs, state, index)
            moved = {(r.seq, float(r.tick)): r.new_tick for r in plan.relocations}
            for seq in arrays.RELOCATABLE_SEQS:
                for arr in index.arrays_for(seq):
                    out = []
                    for t in arr:
                        if (seq, float(t)) in moved:
                            out.append(moved[(seq, float(t))])
                        else:
                            e = to_edited(state, t)
                            out.append(e if e is not None else _join(state, t))
                    self.assertEqual(
                        out, sorted(out),
                        "%s %s array %s came out %s" % (ev, seq, arr, out))
                    checked += 1
        if not checked:
            self.skipTest("Content not beside this checkout")


def _join(state: EditState, t: float) -> float:
    """Where a tick inside a cut lands when nothing carries it."""
    removed = 0.0
    for c in normalise_cuts(state.cuts):
        if c.a <= t < c.b:
            return c.a - removed
        removed += c.b - c.a
    return t - removed
