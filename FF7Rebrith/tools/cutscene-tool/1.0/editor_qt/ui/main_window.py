"""
The window.

Layout in one sentence: the picture and its subtitles are the central widget,
and everything else - the timeline, the scene list, the details, the actors, the
top-down map, the lip sync - is a dock the user can move, resize, stack, close
or float. View ▸ Panels brings any of them back.

That arrangement is the answer to three of the complaints about the browser
build at once: sections could not be resized, the tracker ran off the edge of
the screen, and the subtitles sat above the picture instead of under it.
"""

from __future__ import annotations

import json
import os
import sys
from typing import List, Optional

from dataclasses import dataclass

from PySide6.QtCore import QProcess, QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from dataclasses import replace as _replace

from ..core import arrays, keyframes, mixdown
from ..core.collapse import describe as describe_collapse, effective
from ..core.cues import DETACH_CLIPS, can_disable, cue_descriptor, cue_key
from ..core.drag import authored_key, revert as drag_revert
from ..core.edits import (
    CutSpan,
    EditState,
    MusicRepoint,
    empty_edits,
    is_untouched,
    removed_ticks,
    PinSpan,
    with_actor_pin,
    with_cue_moves,
    with_cue_toggled,
    with_cut,
    with_music_repointed,
    with_pin_span,
    without_actor_pin_span,
    without_any_pins,
    without_cue_move,
    without_music_repoint,
    without_pin_entry,
)
from ..core.impact import impact_of
from ..core.lanes import apply_relocations, build_lanes
from ..core.music import MusicLibrary, capacity_of
from ..core.library import SceneLibrary
from ..core.plan import from_plan, plan_changes_something, to_plan, write_plan
from ..core.stage import lip_at, stage_at
from ..core.text import plain
from ..core.timeline import Cutscene
from . import theme
from .music_picker import MusicPicker
from .panels import ActorPanel, DetailsPanel, ScenePanel, StageInfoPanel
from .preview import CameraView, MouthView, SubtitleBar, TopDownView
from .timeline_view import TimelineView
from .transport import MixdownLoader, PlaybackClock, PreviewAudio, WaveformLoader

ORG = "FF7R Cutscene Tool"
APP = "Cutscene Editor (native)"


@dataclass
class ToolConfig:
    """Paths the editor needs to do more than read.

    All optional: without `content`/`usmap` there are no keyframe rows, without
    `game_dir`/`rezen` the Build button explains itself instead of running.
    """

    content: Optional[str] = None
    usmap: Optional[str] = None
    game_dir: Optional[str] = None
    rezen: Optional[str] = None
    audiomog: Optional[str] = None
    plans: Optional[str] = None
    timelines: Optional[str] = None
    engine: str = "GAME_UE4_26"

    @property
    def can_build(self) -> bool:
        return bool(self.content and self.usmap and self.game_dir and self.rezen)


class MainWindow(QMainWindow):
    def __init__(self, library: SceneLibrary, start_scene: Optional[str] = None,
                 config: Optional[ToolConfig] = None) -> None:
        super().__init__()
        self.setWindowTitle("FF7 Rebirth — Cutscene Editor")
        self.resize(1600, 980)

        self.library = library
        self.config = config or ToolConfig()
        # The BGM folder, listed on demand. Constructed even without a content
        # root: it simply reports itself unavailable, and the menu item then
        # explains why rather than disappearing.
        self.music = MusicLibrary(self.config.content)
        self.cs: Optional[Cutscene] = None
        #: Times-array membership for the open scene; set in `_show_cutscene`
        self._arrays = None
        self.edits: EditState = empty_edits()
        self._undo: List[EditState] = []
        self._redo: List[EditState] = []
        self._build_proc: Optional[QProcess] = None

        self._build_central()
        self._build_docks()
        self._build_toolbar()
        self._build_menus()
        self._build_shortcuts()

        self.audio = PreviewAudio(self)
        self.audio.state_text.connect(self._on_audio_state)
        self.waveforms = WaveformLoader(self)
        self.waveforms.ready.connect(self._on_waveform)

        # Preview audio that follows the edit. Debounced rather than fired on
        # every state change: dragging a cue commits once on release, but
        # loading a plan, undo and redo can all land in quick succession, and
        # each one would otherwise start a render the next immediately makes
        # stale.
        self.mixer = MixdownLoader(self)
        self.mixer.ready.connect(self._on_mix_ready)
        self._mix_token = 0
        self._mix_timer = QTimer(self)
        self._mix_timer.setSingleShot(True)
        self._mix_timer.setInterval(250)
        self._mix_timer.timeout.connect(lambda: self._request_mix())
        self._mix_path: Optional[str] = None
        self.clock = PlaybackClock(parent=self)
        self.clock.audio = self.audio
        self.clock.tick.connect(self._on_clock)
        self.clock.jumped.connect(self._on_clock_jump)
        self.clock.stopped.connect(lambda: self.play_action.setText("▶  Play"))

        self.status_scene = QLabel("", self)
        self.status_audio = QLabel("", self)
        self.status_audio.setProperty("role", "dim")
        self.statusBar().addWidget(self.status_scene, 1)
        self.statusBar().addPermanentWidget(self.status_audio)

        self._restore_layout()
        # On unless it has been turned off: the combined dialogue row is the
        # thing that does not work, so defaulting to it would ship the problem.
        # QSettings hands strings back from the registry on Windows.
        saved_split = self._settings().value("splitVoiceBySpeaker", True)
        # Signals stay connected on purpose, so the toolbar's tick box follows
        # the restored value. No scene is open yet, so the handler does nothing
        # beyond writing the preference straight back.
        self.split_voice_action.setChecked(
            str(saved_split).lower() not in ("false", "0"))
        entries = self.library.load()
        self.scene_panel.set_library(self.library)
        self._fill_picker(entries)

        wanted = start_scene or self._settings().value("lastScene", "")
        if wanted and os.path.isfile(self.library.path_for(wanted)):
            QTimer.singleShot(0, lambda: self.open_scene(wanted))
        elif entries:
            QTimer.singleShot(0, lambda: self.open_scene(entries[0].ev))

    # -- construction ---------------------------------------------------

    def _build_central(self) -> None:
        self.camera = CameraView(self)
        self.subtitles = SubtitleBar(self)

        stage = QWidget(self)
        lay = QVBoxLayout(stage)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.camera, 1)
        lay.addWidget(self.subtitles, 0)   # under the picture, where it belongs

        self.timeline = TimelineView(self)
        self.timeline.playhead_moved.connect(self._on_scrub)
        self.timeline.item_selected.connect(self._on_item_selected)
        self.timeline.selection_changed.connect(self._on_selection_changed)
        self.timeline.cue_drag_preview.connect(self._on_cue_drag_preview)
        self.timeline.cue_dragged.connect(self._on_cue_dragged)
        self.timeline.context_requested.connect(self._on_context_menu)
        self.timeline.stack_hit.connect(self._on_stack_hit)

        # The stage is the central widget; the tracker is a dock like everything
        # else, so it can be moved, floated or stacked with the rest. It used to
        # be the bottom half of a fixed vertical splitter, which is the one
        # arrangement you could not change.
        self.setCentralWidget(stage)

        # Both bottom corners belong to the bottom dock area, so a dock down
        # there runs the full width of the window rather than being squeezed
        # between the left and right columns. Qt gives the corners to the side
        # areas by default; for a timeline, width is the whole point.
        self.setCorner(Qt.BottomLeftCorner, Qt.BottomDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.BottomDockWidgetArea)

    def _dock(self, title: str, widget: QWidget, area: Qt.DockWidgetArea,
              name: str) -> QDockWidget:
        d = QDockWidget(title, self)
        d.setObjectName(name)
        d.setWidget(widget)
        d.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(area, d)
        return d

    def _build_docks(self) -> None:
        self.dock_timeline = self._dock("Timeline", self.timeline,
                                        Qt.BottomDockWidgetArea, "dockTimeline")
        # enough for the ruler, the waveform and a few rows; the stage is
        # Expanding and will otherwise take everything it is offered
        self.timeline.setMinimumHeight(220)

        self.scene_panel = ScenePanel(self)
        self.scene_panel.scene_chosen.connect(self.open_scene)
        self.dock_scenes = self._dock("Cutscenes", self.scene_panel,
                                      Qt.LeftDockWidgetArea, "dockScenes")

        self.stage_info = StageInfoPanel(self)
        self.dock_info = self._dock("In frame", self.stage_info,
                                    Qt.RightDockWidgetArea, "dockInfo")

        self.topdown = TopDownView(self)
        self.dock_map = self._dock("Top-down", self.topdown,
                                   Qt.RightDockWidgetArea, "dockMap")

        self.mouth = MouthView(self)
        self.dock_lip = self._dock("Lip sync", self.mouth,
                                   Qt.RightDockWidgetArea, "dockLip")

        self.details = DetailsPanel(self)
        self.dock_details = self._dock("Details", self.details,
                                       Qt.RightDockWidgetArea, "dockDetails")

        self.actors = ActorPanel(self)
        self.actors.pin_changed.connect(self._on_pin)
        self.actors.pin_ranged.connect(self._on_pin_range)
        self.actors.pin_span_cleared.connect(self._on_pin_span_cleared)
        self.actors.pin_removed.connect(self._on_pin_removed)
        self.actors.pins_cleared.connect(self._on_pins_cleared)
        self.dock_actors = self._dock("Actors", self.actors,
                                      Qt.RightDockWidgetArea, "dockActors")

        self.build_log = QPlainTextEdit(self)
        self.build_log.setReadOnly(True)
        self.build_log.setFont(theme.mono_font(9))
        self.dock_log = self._dock("Build log", self.build_log,
                                   Qt.BottomDockWidgetArea, "dockLog")
        self._apply_default_layout()

    #: Where each dock starts, and where "Reset window layout" puts it back.
    def _default_areas(self):
        return (
            (self.dock_timeline, Qt.BottomDockWidgetArea),
            (self.dock_log, Qt.BottomDockWidgetArea),
            (self.dock_scenes, Qt.LeftDockWidgetArea),
            (self.dock_info, Qt.RightDockWidgetArea),
            (self.dock_map, Qt.RightDockWidgetArea),
            (self.dock_lip, Qt.RightDockWidgetArea),
            (self.dock_details, Qt.RightDockWidgetArea),
            (self.dock_actors, Qt.RightDockWidgetArea),
        )

    def _apply_default_layout(self) -> None:
        """Put every dock back where the window is built with it.

        Rebuilt from the areas rather than restored from a `saveState` blob:
        `restoreState` over a layout that is already tabified leaves the old
        tab bar behind, so resetting twice grows a second row of Details/Actors
        tabs. Re-adding each dock says the same thing without that.
        """
        for dock, area in self._default_areas():
            # Only re-add what is actually out of place. `addDockWidget` pulls
            # a dock out of its tab group, and re-tabifying afterwards leaves
            # the old tab bar behind - so a reset with nothing to fix would
            # still grow a second row of Details/Actors tabs.
            if dock.isFloating() or self.dockWidgetArea(dock) != area:
                dock.setFloating(False)
                self.addDockWidget(area, dock)
            dock.show()
        # under the tracker, not beside it - two docks in the same area sit
        # side by side otherwise, and neither ends up wide enough to read
        self.splitDockWidget(self.dock_timeline, self.dock_log, Qt.Vertical)
        self.dock_log.hide()          # only worth space once a build is running

        # Only if they are not already a pair: tabifying an existing tab group
        # leaves the old tab bar behind, so resetting twice grew a second row
        # of Details/Actors tabs.
        if self.tabifiedDockWidgets(self.dock_details) != [self.dock_actors]:
            self.tabifyDockWidget(self.dock_details, self.dock_actors)
        self.dock_details.raise_()
        self.resizeDocks([self.dock_scenes], [280], Qt.Horizontal)
        self.resizeDocks([self.dock_timeline], [400], Qt.Vertical)

    def _toolbar_checkbox(self, tb: QToolBar, action: QAction) -> QCheckBox:
        """Put a checkable action on the toolbar as an actual tick box.

        A checkable QToolButton says it is on by looking very slightly pressed,
        which is easy to miss and impossible to read at a glance when three of
        them sit in a row. The QAction stays the state everything else talks to
        - the View menu, `Ctrl+D`, the code that syncs a toggle back from the
        edits - and the box is just a second view of it.
        """
        box = QCheckBox(action.text(), self)
        box.setToolTip(action.toolTip())
        box.setChecked(action.isChecked())
        box.toggled.connect(action.setChecked)

        def mirror(on: bool) -> None:
            box.blockSignals(True)
            box.setChecked(on)
            box.blockSignals(False)

        action.toggled.connect(mirror)
        tb.addWidget(box)
        return box

    def _build_toolbar(self) -> None:
        tb = self.toolbar = QToolBar("Transport", self)
        tb.setObjectName("toolbarTransport")
        tb.setMovable(False)
        self.addToolBar(tb)

        self.picker = QComboBox(self)
        self.picker.setMinimumWidth(240)
        self.picker.activated.connect(
            lambda i: self.open_scene(self.picker.itemData(i))
        )
        tb.addWidget(self.picker)
        tb.addSeparator()

        self.play_action = QAction("▶  Play", self)
        self.play_action.triggered.connect(self.toggle_play)
        tb.addAction(self.play_action)

        for text, slot in (
            ("⏮", lambda: self.seek_to(0)),
            ("⏭", lambda: self.seek_to(self.cs.total if self.cs else 0)),
        ):
            a = QAction(text, self)
            a.triggered.connect(slot)
            tb.addAction(a)

        tb.addSeparator()
        for text, slot in (
            ("Fit", lambda: self.timeline.zoom_to_fit()),
            ("−", lambda: self.timeline.zoom_by(1 / 1.4)),
            ("+", lambda: self.timeline.zoom_by(1.4)),
        ):
            a = QAction(text, self)
            a.triggered.connect(slot)
            tb.addAction(a)

        tb.addSeparator()
        self.mute_action = QAction("Mute", self)
        self.mute_action.setCheckable(True)
        self.mute_action.toggled.connect(lambda on: self.audio.set_muted(on))
        tb.addAction(self.mute_action)

        self.split_voice_action = QAction("Split dialogue by speaker", self)
        self.split_voice_action.setCheckable(True)
        self.split_voice_action.setToolTip(
            "Give every character who speaks their own dialogue row (Ctrl+D).\n"
            "Lines overlap constantly — a reaction lands under the tail of the "
            "line it answers, and on one row the buried block cannot be clicked, "
            "so it cannot be trimmed, dragged or switched off.\n"
            "Who is speaking comes from the scene's own subtitles first, then "
            "from what its labelled lines prove its voice codes mean, then from "
            "the table counted across every extracted scene."
        )
        self.split_voice_action.toggled.connect(self._on_split_voice_toggled)
        self._toolbar_checkbox(tb, self.split_voice_action)

        self.collapse_action = QAction("Carry fades && streaming", self)
        self.collapse_action.setCheckable(True)
        self.collapse_action.setChecked(True)
        self.collapse_action.setToolTip(
            "Stop a cut where the scene's fade to black begins, instead of on a "
            "hard frame.\n"
            "The fade then lands on the join and everything after it plays "
            "under black — so the level-streaming commands that preload the "
            "next scene still fire, and you never see the footage they sit in.\n"
            "The edit ends up longer than the cut by the fade's own length; the "
            "timeline draws that stretch in black."
        )
        self.collapse_action.toggled.connect(self._on_collapse_toggled)
        self._toolbar_checkbox(tb, self.collapse_action)

        self.preload_lead_action = QAction("Restore preload lead", self)
        self.preload_lead_action.setCheckable(True)
        self.preload_lead_action.setChecked(False)
        self.preload_lead_action.setToolTip(
            "Move a Preload the cuts never touched, when a join lands inside "
            "the window the sky needs to load in.\n"
            "Separate from “Carry fades && streaming”, which repairs cues a cut "
            "destroyed and is always wanted. This one is a guess about how the "
            "engine spends streaming bandwidth, and it has not been confirmed "
            "in game — so it is off unless you ask for it.\n"
            "Only Preload moves; SwitchToPreloaded puts the sky on screen and "
            "is never touched."
        )
        self.preload_lead_action.toggled.connect(self._on_preload_lead_toggled)
        self._toolbar_checkbox(tb, self.preload_lead_action)

        tb.addSeparator()
        for text, tip, slot in (
            ("↶", "Undo (Ctrl+Z)", self.undo),
            ("↷", "Redo (Ctrl+Y)", self.redo),
        ):
            a = QAction(text, self)
            a.setToolTip(tip)
            a.triggered.connect(slot)
            tb.addAction(a)

        save_action = QAction("Save plan", self)
        save_action.setToolTip("Write the edit plan to the plans folder (Ctrl+S)")
        save_action.triggered.connect(self.save_plan)
        tb.addAction(save_action)

        self.build_action = QAction("Build && install", self)
        self.build_action.setToolTip("Save the plan, patch the assets, pack and "
                                     "install the mod (Ctrl+B)")
        self.build_action.triggered.connect(self.build_and_install)
        tb.addAction(self.build_action)

        tb.addSeparator()
        self.time_label = QLabel("0:00.00", self)
        self.time_label.setFont(theme.mono_font(10))
        tb.addWidget(self.time_label)

        self.edit_label = QLabel("", self)
        self.edit_label.setProperty("role", "dim")
        self.edit_label.setStyleSheet("color: %s; padding-left: 12px;" % theme.SEL)
        tb.addWidget(self.edit_label)

        #: what keeping fades and streaming is costing this edit - red when it
        #: is holding back most of what was cut, which is worth noticing
        self.collapse_label = QLabel("", self)
        self.collapse_label.setProperty("role", "dim")
        self.collapse_label.setStyleSheet("color: %s; padding-left: 12px;" % theme.DIM)
        tb.addWidget(self.collapse_label)

    def _panels(self) -> List[QDockWidget]:
        """Every dock, in the order they are worth listing in a menu."""
        return [self.dock_timeline, self.dock_scenes, self.dock_details,
                self.dock_actors, self.dock_info, self.dock_map, self.dock_lip,
                self.dock_log]

    def _build_menus(self) -> None:
        """A menu bar exists for one reason: a closed panel has to be findable.

        Qt gives a hidden dock no affordance of its own - the title bar you
        would click to bring it back went with it - and the toolbar's own
        right-click menu is no help once the toolbar itself is hidden. Worse,
        the layout is saved on exit, so a panel closed by accident stays closed
        across restarts with nothing on screen to say it exists. The menu bar
        is the one thing that cannot be dismissed.
        """
        view = self.menuBar().addMenu("&View")
        view.addAction(self.split_voice_action)
        view.addSeparator()

        panels = view.addMenu("Panels")
        for dock in self._panels():
            panels.addAction(dock.toggleViewAction())
        view.addAction(self.toolbar.toggleViewAction())
        view.addSeparator()

        show_all = QAction("Show every panel", self)
        show_all.setToolTip("Bring back anything closed, where it was")
        show_all.triggered.connect(self.show_all_panels)
        view.addAction(show_all)

        reset = QAction("Reset window layout", self)
        reset.setToolTip("Docks, toolbar and splitter back to how they started")
        reset.triggered.connect(self.reset_layout)
        view.addAction(reset)

    def show_all_panels(self) -> None:
        """Unhide everything, leaving where each one sits alone.

        The gentler of the two: someone who has arranged their docks and closed
        one wants it back, not their arrangement undone.
        """
        for dock in self._panels():
            dock.show()
        self.toolbar.show()
        self.statusBar().showMessage("all panels shown", 2500)

    def reset_layout(self) -> None:
        """Back to the layout the window is built with."""
        self._apply_default_layout()
        self.toolbar.show()
        self.statusBar().showMessage("window layout reset", 2500)

    def _build_shortcuts(self) -> None:
        """Only chorded shortcuts live here.

        Bare keys (Space, Delete, arrows…) are handled in `keyPressEvent`
        instead of as application shortcuts, and the difference matters: an
        application shortcut fires even while the search box has focus, which
        would turn typing a space into play/pause and pressing Delete while
        correcting a query into deleting a cue. Key events, by contrast, only
        bubble up here after the focused widget declined them.
        """

        def act(keys: str, fn) -> None:
            a = QAction(self)
            a.setShortcut(QKeySequence(keys))
            a.setShortcutContext(Qt.WindowShortcut)
            a.triggered.connect(fn)
            self.addAction(a)

        act("Ctrl+Z", self.undo)
        act("Ctrl+Y", self.redo)
        act("Ctrl+Shift+Z", self.redo)
        act("Ctrl+S", self.save_plan)
        act("Ctrl+B", self.build_and_install)
        act("Ctrl+M", self.repoint_selected_music)
        act("Ctrl+D", self.split_voice_action.toggle)

    def keyPressEvent(self, ev) -> None:
        k = ev.key()
        mods = ev.modifiers()
        cs = self.cs
        if k == Qt.Key_Space:
            self.toggle_play()
        elif k == Qt.Key_Home:
            self.seek_to(0)
        elif k == Qt.Key_End:
            self.seek_to(cs.total if cs else 0)
        elif k == Qt.Key_Left:
            self.step_frames(-30 if mods & Qt.ShiftModifier else -1)
        elif k == Qt.Key_Right:
            self.step_frames(30 if mods & Qt.ShiftModifier else 1)
        elif k == Qt.Key_F:
            self.timeline.zoom_to_fit()
        elif k in (Qt.Key_Plus, Qt.Key_Equal):
            self.timeline.zoom_by(1.4)
        elif k == Qt.Key_Minus:
            self.timeline.zoom_by(1 / 1.4)
        elif k == Qt.Key_M:
            self.mute_action.toggle()
        elif k in (Qt.Key_Delete, Qt.Key_Backspace):
            if mods & Qt.ShiftModifier:
                self.cut_selection()
            else:
                self.delete_selected()
        elif k in (Qt.Key_Return, Qt.Key_Enter):
            self.render_mix()
        elif k == Qt.Key_R:
            self.restore_moved_cue()
        elif k == Qt.Key_Escape:
            self.timeline.set_selection(None)
        else:
            super().keyPressEvent(ev)
            return
        ev.accept()

    # -- scenes ---------------------------------------------------------

    def _fill_picker(self, entries) -> None:
        self.picker.blockSignals(True)
        self.picker.clear()
        for i, e in enumerate(entries):
            self.picker.addItem(e.ev, e.ev)
            if e.preview:
                self.picker.setItemData(i, e.preview, Qt.ToolTipRole)
        self.picker.blockSignals(False)
        self._previews = {e.ev: e.preview for e in entries}

    def open_scene(self, ev: str) -> None:
        if not ev:
            return
        try:
            cs = self.library.load_cutscene(ev)
        except Exception as exc:
            QMessageBox.warning(self, "Could not open", str(exc))
            return

        self.clock.stop()
        self.cs = cs
        self.edits = empty_edits()
        self.clock.edits = self.edits
        self._undo.clear()
        self._redo.clear()
        self._keys = self._load_keyframes(cs)

        self.setWindowTitle("FF7 Rebirth — Cutscene Editor — %s" % cs.name)
        opening = getattr(self, "_previews", {}).get(cs.name, "")
        if not opening and cs.subtitles:
            first = cs.subtitles[0]
            opening = plain(
                (first.actor + ": " if first.actor else "") + (first.text or first.label)
            )
        self.status_scene.setText(
            "%s   ·   %s%s"
            % (cs.name, cs.summary(), ("   ·   " + opening) if opening else "")
        )
        self.timeline.set_cutscene(cs, self._all_lanes(cs))
        self.timeline.set_edits(self.edits)
        # Which cues share a Times array, so a drag stops at its neighbours
        # instead of being dropped during the build. Read from the assets when
        # Content is configured; the fallback is conservative, never permissive.
        #
        # Kept on the window as well as handed to the timeline, because the
        # automatic rescue in `collapse.py` is under the same constraint and
        # every `effective()` call has to be told about it - the editor showing
        # a cue somewhere the build will refuse to put it is the same class of
        # bug as the editor showing one thing and building another.
        self._arrays = arrays.for_scene(cs, self.config.content)
        self.timeline.set_array_index(self._arrays)
        self.actors.set_actors(cs.actors_with_visibility(), self.edits)
        self.details.clear()

        self.clock.configure(cs.time.ticks_per_second, cs.total)
        audio_path = self.library.audio_path(cs)
        self.audio.load(audio_path, cs.time.ticks_per_second)
        self.timeline.set_waveform(None)
        self._wave_path = audio_path
        self._wave_token = self.waveforms.request(audio_path)
        self._mix_path = None
        self._schedule_mix()

        idx = self.picker.findData(cs.name)
        if idx >= 0:
            self.picker.setCurrentIndex(idx)
        self.scene_panel.select(cs.name)

        self._settings().setValue("lastScene", cs.name)
        self._load_saved_plan(cs)
        self._refresh_edit_status()
        self._render(0.0)

    def _all_lanes(self, cs: Cutscene, collapse=None) -> List:
        """Timeline rows: the ones from the extraction, plus the ones read live
        from the game assets when the Content folder is configured.

        `collapse` places the cues the tool is carrying across a cut at the tick
        they will fire on, the same way `build_lanes` places the ones dragged by
        hand. Both kinds of relocation move the block itself; nothing is drawn
        to describe the move.
        """
        lanes = build_lanes(cs, self.edits, self.split_voice_action.isChecked())
        if collapse is not None:
            apply_relocations(cs, collapse, lanes)
        return lanes + keyframes.build_key_lanes(
            getattr(self, "_keys", None)
        )

    def _load_keyframes(self, cs: Cutscene):
        """Animation clips and key ticks, straight from `_Character`/`_Light`.

        Absent Content paths, or an asset that will not parse, means no rows —
        every other part of the editor is unaffected.
        """
        try:
            keys = keyframes.load(self.config.content, self.config.usmap, cs.area, cs.name)
        except Exception:
            return None
        if keys is None and self.config.content:
            self.statusBar().showMessage(
                "no _Character/_Light assets found for %s" % cs.name, 4000)
        return keys

    # -- transport ------------------------------------------------------

    def toggle_play(self) -> None:
        if not self.cs:
            return
        if self.clock.running:
            self.clock.stop()
            self.audio.pause()
            self.play_action.setText("▶  Play")
        else:
            at = self.timeline.playhead
            if at >= self.cs.total:
                at = 0.0
            # scrubbing into a cut is allowed - it is how you check an edge -
            # but playing from inside one would start on removed footage
            at = self.clock.skip_gap(at)
            self.clock.start(at)
            self.audio.play(at)
            self._render(at)
            self.play_action.setText("❚❚  Pause")

    def seek_to(self, t: float) -> None:
        if not self.cs:
            return
        t = max(0.0, min(self.cs.total, t))
        self.clock.set_playhead(t)
        self.audio.seek(t)
        self._render(t)

    def step_frames(self, n: int) -> None:
        if not self.cs:
            return
        self.seek_to(self.timeline.playhead + n * self.cs.time.ticks_per_frame)

    def _on_clock(self, t: float) -> None:
        self._render(t)

    def _on_clock_jump(self, t: float) -> None:
        """The clock stepped over a cut: take the sound with it.

        Seeking marks the player untrusted for a moment (`SEEK_SETTLE`), which
        is what stops the stale position it reports meanwhile from dragging the
        playhead back into the gap we just left.
        """
        self.audio.seek(t)

    def _on_scrub(self, t: float) -> None:
        self.clock.set_playhead(t)
        self.audio.seek(t)
        self._render(t, follow=False)

    def _on_audio_state(self, text: str) -> None:
        self.status_audio.setText(text)

    def _on_waveform(self, wave, token: int) -> None:
        # a decode that lands after the user moved on belongs to another scene
        if token != getattr(self, "_wave_token", 0):
            return
        self.timeline.set_waveform(wave)

    # -- rendering ------------------------------------------------------

    def _render(self, t: float, follow: bool = True) -> None:
        cs = self.cs
        if not cs:
            return
        self.timeline.set_playhead(t, follow=follow)
        self.time_label.setText(
            "%s   /   %s" % (cs.time.format(t), cs.time.format(cs.total))
        )

        frame = stage_at(cs.scene, t)
        self.camera.set_frame(frame)
        self.topdown.set_frame(frame)
        self.stage_info.set_frame(frame)
        self.mouth.set_state(lip_at(cs.lipsync, t))

        sub = cs.subtitle_at(t)
        if sub:
            # the game's own markup is HTML-escaped in the extraction
            self.subtitles.set_line(sub.actor, plain(sub.text) or sub.label)
        else:
            self.subtitles.clear_line()

    def _selection_pin_info(self, cs, sel):
        """Per actor, a plain sentence for what pinning over the selection does.

        Visibility only changes where a command exists, so the truthful answer
        is usually "from <the governing command>" rather than "over the range
        you drew" - and when there is no command at all, that it cannot work.
        """
        out = {}
        closes = sel.b < cs.total
        need = 2 if closes else 1
        for actor in cs.actors_with_visibility():
            cmds = [t for t, _h in cs.visibility_commands(actor)]
            if len(cmds) > need:
                out[actor] = (
                    "Exact: %s of its %d commands move to the edges of the range"
                    % ("Two" if need == 2 else "One", len(cmds))
                )
            elif cmds:
                gov = [t for t in cmds if t < sel.a]
                out[actor] = (
                    "Only %d command%s — too few to bound the range, so the "
                    "state would change from %s instead"
                    % (len(cmds), "" if len(cmds) == 1 else "s",
                       cs.time.format(gov[-1]) if gov else "the first one in it")
                )
            else:
                out[actor] = ("%s has no show/hide command anywhere, so nothing "
                              "can change it" % actor)
        return out

    def _on_selection_changed(self, _span) -> None:
        """The actor panel's range buttons act on the selection, so they have
        to know when there is one."""
        cs = self.cs
        if not cs:
            return
        sel = self.timeline.selection
        if sel and sel.b > sel.a:
            self.actors.set_selection_label(
                "%s – %s" % (cs.time.format(sel.a), cs.time.format(sel.b)),
                self._selection_pin_info(cs, sel))
        else:
            self.actors.set_selection_label("")
        self.actors.set_actors(cs.actors_with_visibility(), self.edits)

    def _on_stack_hit(self, index: int, count: int) -> None:
        """Say so when the click landed on a pile rather than a block.

        Two cues on the same frame are drawn on the same pixels, so without
        this the second one is invisible *and* silent: you would switch off the
        one you can see, believe the job done, and find the other still firing
        in game. That is exactly how EV_CORLE_0100 kept a flower lei.
        """
        if count > 1:
            self.statusBar().showMessage(
                "cue %d of %d on this frame — click again for the next"
                % (index + 1, count), 4000)

    def _on_item_selected(self, item, lane) -> None:
        if not self.cs:
            return
        found = self._music_cue(item)
        repoint = self.edits.repoints.get(found[0]) if found else None
        self.details.show_item(self.cs, item, lane, repoint)

    # -- preview audio that follows the edit ------------------------------

    def _mix_cache(self) -> Optional[str]:
        """Beside the offline mixes and the waveform peaks, and gitignored the
        same way. Keeping renders next to the audio they stand in for is what
        makes them obvious to delete when the folder gets big."""
        if not self.config.timelines:
            return None
        return os.path.join(self.config.timelines, "audio", ".preview")

    def _request_mix(self, fmt: Optional[str] = None) -> None:
        cache = self._mix_cache()
        if not self.cs or not self.config.content or not cache:
            return
        lang = (self.cs.audio.lang if self.cs.audio and self.cs.audio.lang
                else "US")
        self._mix_token = self.mixer.request(
            self.cs, self.edits, self.config.content, cache, lang, fmt)

    def _schedule_mix(self) -> None:
        if self.cs and self.config.content:
            self._mix_timer.start()

    def render_mix(self) -> None:
        """Enter: render the current edit as a keepable .ogg, now.

        The automatic preview is a WAV because that is the quick thing to write
        - see `mixdown.DRAFT_FORMAT`. This is the small file, for keeping or
        sending somewhere, and it also serves as "do it now" when the debounce
        has not fired yet.
        """
        if not self.cs or not self.config.content:
            self.statusBar().showMessage(
                "no Content folder configured — nothing to render from", 4000)
            return
        self.statusBar().showMessage("rendering the edit…")
        self._request_mix(fmt=mixdown.KEEP_FORMAT)

    def _on_mix_ready(self, report, token: int) -> None:
        if token != self._mix_token or report is None:
            return
        keep = report.path.endswith("." + mixdown.KEEP_FORMAT)
        # Reload at the position we are already at, so a render landing
        # mid-scrub does not throw the playhead back to the top.
        at = self.timeline.playhead
        was_playing = self.clock.running
        self._mix_path = report.path
        self.audio.load(report.path, self.cs.time.ticks_per_second)
        self.audio.seek(at)
        # The top row is meant to be the audio you are listening to. It used to
        # be the OFFLINE mix for the whole session, so the moment an edit was
        # made the picture of the sound and the sound itself were two different
        # recordings - and a repointed music cue is the case where that gap is
        # most obvious, since the whole waveform under it changes. Each render
        # is named after its edit, so re-requesting only costs a decode when
        # something actually changed, and the peaks cache keys on mtime.
        if report.path != getattr(self, "_wave_path", None):
            self._wave_path = report.path
            self._wave_token = self.waveforms.request(report.path)
        if was_playing:
            self.audio.play(at)
        note = report.summary()
        if keep:
            note += "  ·  rendered to %s" % os.path.basename(report.path)
        self.status_audio.setText(note)

    def _on_cue_drag_preview(self, proposal) -> None:
        """Say what the drag would do while it is still being made.

        The status bar rather than a tooltip, because the interesting case is
        the one where the block has stopped following the pointer - it has hit
        a neighbour it cannot cross - and that needs a sentence, not a number.
        """
        if proposal is None:
            self.statusBar().clearMessage()
        elif proposal.note:
            self.statusBar().showMessage(proposal.note)

    def _on_cue_dragged(self, proposal) -> None:
        if not self.cs or proposal is None or proposal.empty:
            return
        self.apply_edits(with_cue_moves(self.edits, proposal.moves), proposal.note)

    def restore_moved_cue(self) -> None:
        """Send the selected cue back to the tick the scene authors it at."""
        item = self.timeline.selected_item
        if not self.cs or item is None:
            return
        key = drag_revert(self.edits, item)
        if not key:
            self.statusBar().showMessage(
                "that cue is where the scene put it — nothing to restore", 3000)
            return
        self.apply_edits(without_cue_move(self.edits, key),
                         "%s back where the scene put it" % (item.name or item.type))

    # -- music triggers ---------------------------------------------------

    def _music_cue(self, item):
        """(cue key, the name the scene authored) for a music block, or None.

        Identity is the *authored* name and the *authored* tick.

        The name, because a second repoint of the same cue has to find the
        first one, and because `from` is what the patcher matches in the bytes.

        The tick, because a block that has been dragged is drawn where it will
        fire, so a descriptor taken straight off it hashes to the new tick and
        agrees with nothing else in the program - `mixdown.placements` spells
        the key from the raw event, and so does `cueMoves`. That is exactly
        what `drag.authored_key` exists to prevent, and using anything else
        here was a real bug: the repoint went into the plan under a key the
        preview mix could not find, so the editor showed the new track and
        played the old one.
        """
        if item is None or (item.clip or item.type) != "BGM":
            return None
        name = (item.props or {}).get("MusicName")
        key = authored_key(item)
        if not name or not key:
            return None
        return key, name

    def repoint_selected_music(self) -> None:
        """Point the selected music trigger at a different track."""
        item = self.timeline.selected_item
        found = self._music_cue(item)
        if not self.cs or not found:
            self.statusBar().showMessage(
                "select a music cue first — the rose row", 4000)
            return
        key, authored = found
        if not self.music.available:
            self.statusBar().showMessage(
                "the music library needs --content (the game's End/Content "
                "folder); StartEditorNative.bat passes it", 8000)
            return

        existing = self.edits.repoints.get(key)
        current = existing.to if existing else authored
        dlg = MusicPicker(self.music, current, authored, self)
        if not dlg.exec() or not dlg.chosen:
            return

        chosen = dlg.chosen
        if chosen == authored:
            if existing is None:
                return
            self.apply_edits(without_music_repoint(self.edits, key),
                             "%s plays the track the scene authored again"
                             % authored)
            return

        bank, index = self.music.resolve(chosen)
        self.apply_edits(
            with_music_repointed(self.edits, key, MusicRepoint(
                seq=item.seq or "ManualSE",
                # the tick the SCENE authors it at, not where a drag put it -
                # the same rule `CueMove.tick` follows, and what the patcher
                # remaps to find the payload
                tick=item.moved_from if item.moved_from is not None
                else (item.tick_start or 0),
                frm=authored,
                to=chosen,
                bank=bank,
                slice=index,
                capacity=capacity_of(authored),
                label=self.music.describe(chosen),
            )),
            "music now plays %s" % self.music.describe(chosen),
        )

    def _on_context_menu(self, item, lane, pos) -> None:
        menu = self.context_menu_for(item, lane)
        if menu is not None and not menu.isEmpty():
            menu.exec(pos)

    def context_menu_for(self, item, lane):
        """The right-click menu. Only what applies to the block under it.

        Built separately from showing it so the choices can be asserted on
        without a pointer: `menu.exec` blocks, and a menu whose contents depend
        on the edit state is exactly the sort of thing that quietly stops
        offering an action.
        """
        if not self.cs:
            return None
        menu = QMenu(self)
        found = self._music_cue(item)
        if found:
            key, authored = found
            act = menu.addAction("Point this trigger at another track…")
            act.triggered.connect(self.repoint_selected_music)
            if key in self.edits.repoints:
                back = menu.addAction(
                    "Play %s again (what the scene authored)" % authored)
                back.triggered.connect(
                    lambda: self.apply_edits(
                        without_music_repoint(self.edits, key),
                        "%s plays the track the scene authored again" % authored))
        if item is not None and lane is not None and not lane.range_row:
            refusal = can_disable(item)
            if refusal.ok:
                off = menu.addAction(
                    "Put this cue back" if refusal.key in self.edits.killed
                    else "Switch this cue off")
                off.triggered.connect(self.delete_selected)
            if item.moved_from is not None:
                back = menu.addAction("Send it back to where the scene put it")
                back.triggered.connect(self.restore_moved_cue)
        return menu

    # -- editing ---------------------------------------------------------

    def apply_edits(self, new_state: EditState, describe: str = "") -> None:
        """Every mutation funnels through here: one undo entry, one refresh."""
        if new_state is self.edits:
            return
        self._undo.append(self.edits)
        self._redo.clear()
        self._set_edits(new_state)
        if describe:
            self.statusBar().showMessage(describe, 4000)

    def _on_collapse_toggled(self, on: bool) -> None:
        """Not an undo step in itself, but it changes what the cuts mean, so it
        goes through the same path everything else does."""
        if self.edits.collapse_to_end == on:
            return
        self.apply_edits(
            _replace(self.edits, collapse_to_end=on),
            "fades and streaming will be carried back across the join" if on
            else "fades and streaming will collapse onto the join",
        )

    def _on_split_voice_toggled(self, on: bool) -> None:
        """A view preference: the rows are rearranged, the plan is untouched.

        So it does not go through `apply_edits` - there is nothing here to undo
        - and it is remembered between sessions the way the window layout is.
        """
        self._settings().setValue("splitVoiceBySpeaker", on)
        cs = self.cs
        if not cs:
            return
        _applied, collapse = effective(cs, self.edits, self._arrays)
        self.timeline.set_lanes(self._all_lanes(cs, collapse))
        self.statusBar().showMessage(
            "dialogue split by speaker" if on else "dialogue back on one row", 2500)

    def _on_preload_lead_toggled(self, on: bool) -> None:
        if self.edits.restore_preload_lead == on:
            return
        self.apply_edits(
            _replace(self.edits, restore_preload_lead=on),
            "surviving preloads will be issued ahead of a join inside their "
            "load window" if on
            else "surviving preloads will fire where the scene authored them",
        )

    def _set_edits(self, state: EditState) -> None:
        self.edits = state
        self._schedule_mix()
        # What the build will actually do. The authored cuts stay in
        # `self.edits` so the handles and undo still work on what was drawn;
        # everything that PREVIEWS the edit uses the effective one, so the
        # editor can't show one thing and build another.
        cs = self.cs
        applied, collapse = (state, None)
        if cs:
            applied, collapse = effective(cs, state, self._arrays)
        # the clock previews the edit, so it needs the current one, not the one
        # the scene opened with
        self.clock.edits = applied
        if cs:
            self.timeline.set_lanes(self._all_lanes(cs, collapse))
            self.timeline.set_edits(applied)
            self.timeline.set_collapse(collapse)
            sel = self.timeline.selection
            if sel and sel.b > sel.a:
                self.actors.set_selection_label(
                    "%s – %s" % (cs.time.format(sel.a), cs.time.format(sel.b)),
                    self._selection_pin_info(cs, sel))
            else:
                self.actors.set_selection_label("")
            self.actors.set_actors(cs.actors_with_visibility(), state)
        if self.collapse_action.isChecked() != state.collapse_to_end:
            self.collapse_action.blockSignals(True)
            self.collapse_action.setChecked(state.collapse_to_end)
            self.collapse_action.blockSignals(False)
        if self.preload_lead_action.isChecked() != state.restore_preload_lead:
            self.preload_lead_action.blockSignals(True)
            self.preload_lead_action.setChecked(state.restore_preload_lead)
            self.preload_lead_action.blockSignals(False)
        self._refresh_edit_status(collapse)

    def undo(self) -> None:
        if not self._undo:
            return
        self._redo.append(self.edits)
        self._set_edits(self._undo.pop())
        self.statusBar().showMessage("undone", 2000)

    def redo(self) -> None:
        if not self._redo:
            return
        self._undo.append(self.edits)
        self._set_edits(self._redo.pop())
        self.statusBar().showMessage("redone", 2000)

    def delete_selected(self) -> None:
        """DEL: the selected cue first, the selected range second.

        Per-cue priority is deliberate and matches v2/v3: clicking an SE and
        pressing Delete removes that sound, not the half-second of scene it
        happens to sit in. Shift+Delete always cuts the range.
        """
        if not self.cs:
            return
        item = self.timeline.selected_item
        if item is not None:
            v = can_disable(item)
            if v.ok:
                on = v.key in self.edits.killed
                # An attach is not deleted, it is turned round: the build
                # flips the payload's own Detach flag, so say that rather than
                # "deleted", which would promise something else.
                verb = ("re-attached " if on else "detached ") \
                    if v.descriptor.get("clip") in DETACH_CLIPS \
                    else ("restored " if on else "deleted ")
                self.apply_edits(
                    with_cue_toggled(self.edits, v.key, v.descriptor),
                    verb + v.descriptor.get("label", "cue"),
                )
                return
            if v.reason == "protected":
                self.statusBar().showMessage(
                    "%s is protected — the game needs it to progress. "
                    "Cut its time range instead if you must." % v.clip, 6000)
                return
            # unnamed: nothing to break; fall through to the range if there is one
            self.statusBar().showMessage(
                "%s has no name to disable — Shift+Del cuts its time range" % v.what,
                5000,
            )
            return
        self.cut_selection()

    def cut_selection(self) -> None:
        """Ripple-cut the selected span, snapped outward to frame boundaries."""
        cs = self.cs
        sel = self.timeline.selection
        if not cs or not sel:
            self.statusBar().showMessage(
                "nothing selected — drag on the timeline or click a camera cut", 4000)
            return
        a = cs.time.floor_to_frame(max(0.0, sel.a))
        b = cs.time.ceil_to_frame(min(cs.total, sel.b))
        if b <= a:
            return
        h = impact_of(cs, a, b)
        warn = []
        if h.mid_line:
            warn.append("splits the line %s" % h.mid_line)
        if h.triggers:
            warn.append("removes state trigger(s) %s" % ", ".join(h.triggers))
        if h.jumps:
            warn.append("removes %d jump(s)" % len(h.jumps))
        if h.stranded:
            warn.append("strands subtitle(s) %s" % ", ".join(h.stranded))
        msg = "cut %s" % cs.time.describe_span(b - a)
        if warn:
            msg += "  ⚠ " + "; ".join(warn)
        self.apply_edits(with_cut(self.edits, CutSpan(a, b)), msg)
        self.timeline.set_selection(None)

    def _on_pin(self, actor: str, how: str) -> None:
        if not self.cs:
            return
        self.apply_edits(with_actor_pin(self.edits, actor, how))

    def _on_pin_range(self, actor: str, hidden: bool) -> None:
        """Pin an actor over the selected range only.

        The scene takes its own visibility back at the first command after the
        range, which is the whole point: a whole-scene pin cannot end.
        """
        cs = self.cs
        sel = self.timeline.selection
        if not cs or not sel or sel.b <= sel.a:
            self.statusBar().showMessage(
                "drag a range on the timeline first, then pin over it", 4000)
            return
        span = PinSpan(actor, hidden, round(sel.a), round(sel.b))
        cmds = [t for t, _h in cs.visibility_commands(actor)]
        if not cmds:
            self.statusBar().showMessage(
                "%s has no show/hide command anywhere in this scene — nothing "
                "can change it" % actor, 6000)
            return
        need = 2 if sel.b < cs.total else 1
        exact = len(cmds) > need
        self.apply_edits(
            with_pin_span(self.edits, span),
            "%s %s from %s to %s%s"
            % (actor, "hidden" if hidden else "visible",
               cs.time.format(sel.a), cs.time.format(sel.b),
               "" if exact else " (approximate — too few commands to bound it)"),
        )

    def _on_pin_span_cleared(self, actor: str) -> None:
        self.apply_edits(without_actor_pin_span(self.edits, actor),
                         "range pin on %s removed" % actor)

    def _on_pin_removed(self, entry) -> None:
        where = ("whole scene" if entry.is_global
                 else "%s – %s" % (self.cs.time.format(entry.span.a),
                                   self.cs.time.format(entry.span.b)))
        self.apply_edits(without_pin_entry(self.edits, entry),
                         "removed: %s %s over %s"
                         % (entry.actor, "hidden" if entry.hidden else "visible",
                            where))

    def _on_pins_cleared(self) -> None:
        self.apply_edits(without_any_pins(self.edits), "all visibility pins removed")

    def _refresh_edit_status(self, collapse=None) -> None:
        """`collapse` is passed in by `_set_edits`, which has just worked it
        out; anyone else can leave it out and it is recomputed."""
        cs = self.cs
        if not cs or is_untouched(self.edits):
            self.edit_label.setText("")
            self.collapse_label.setText("")
            return
        if collapse is None:
            _applied, collapse = effective(cs, self.edits, self._arrays)
        bits = []
        # what the build removes, which is not always what was drawn
        removed = removed_ticks(self.edits)
        if removed:
            bits.append("−%s" % cs.time.describe_span(removed))
        if self.edits.killed:
            n = len(self.edits.killed)
            bits.append("%d cue%s off" % (n, "" if n == 1 else "s"))
        if self.edits.moves:
            # count the gestures, not the cues: a line of dialogue moves three
            # things and "3 cues moved" for one drag reads as a mistake
            n = sum(1 for m in self.edits.moves.values() if not m.group)
            bits.append("%d cue%s moved" % (n, "" if n == 1 else "s"))
        if self.edits.repoints:
            n = len(self.edits.repoints)
            bits.append("%d music cue%s repointed" % (n, "" if n == 1 else "s"))
        pins = len(self.edits.force_visible) + len(self.edits.force_hidden)
        if pins:
            bits.append("%d pin%s" % (pins, "" if pins == 1 else "s"))
        self.edit_label.setText("  ·  ".join(bits))

        line, loud = describe_collapse(cs, collapse) if collapse else ("", False)
        self.collapse_label.setText(line)
        self.collapse_label.setStyleSheet(
            "color: %s; padding-left: 12px;" % (theme.CUT if loud else theme.DIM)
        )

    # -- plans and building ----------------------------------------------

    def _plan_path(self, ev: str) -> Optional[str]:
        if not self.config.plans:
            return None
        return os.path.join(self.config.plans, "%s_editplan.json" % ev)

    def save_plan(self) -> Optional[str]:
        cs = self.cs
        path = self._plan_path(cs.name) if cs else None
        if not cs or not path:
            return None
        plan = to_plan(cs, self.edits, self._arrays)
        if not plan_changes_something(plan) and is_untouched(self.edits):
            self.statusBar().showMessage("no edits to save", 3000)
            return None
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write_plan(path, plan)
        self.statusBar().showMessage("plan saved — %s" % os.path.basename(path), 4000)
        return path

    def _load_saved_plan(self, cs: Cutscene) -> None:
        path = self._plan_path(cs.name)
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                plan = json.load(f)
            state, summary = from_plan(cs, plan, cue_key)
        except Exception as exc:
            self.statusBar().showMessage("saved plan not loaded: %s" % exc, 6000)
            return
        self._set_edits(state)
        if summary:
            self.statusBar().showMessage("loaded saved plan: %s" % summary, 5000)

    def build_and_install(self) -> None:
        """Save the plan and run build_mod.py — the same command, flags and
        defaults the browser helper used, so a build from here is a build."""
        cs = self.cs
        if not cs:
            return
        if self._build_proc is not None:
            self.statusBar().showMessage("a build is already running", 4000)
            return
        if not self.config.can_build:
            QMessageBox.information(
                self, "Build not configured",
                "Building needs the Content, Mappings.usmap, game Paks and "
                "UnrealReZen paths.\n\nStart the editor with "
                "StartEditorNative.bat and they are passed automatically.")
            return
        plan = to_plan(cs, self.edits, self._arrays)
        if not plan_changes_something(plan):
            self.statusBar().showMessage("this plan changes nothing — make an edit first", 5000)
            return
        path = self.save_plan()
        if not path:
            return

        tool_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        args = [
            os.path.join(tool_dir, "build_mod.py"),
            "--plan", path,
            "--content", self.config.content,
            "--usmap", self.config.usmap,
            "--out", os.path.join(self.config.plans or tool_dir, "build"),
            "--game-dir", self.config.game_dir,
            "--rezen", self.config.rezen,
            "--engine-version", self.config.engine,
            "--audio",
            "--run",
        ]
        if self.config.timelines:
            args += ["--timelines", self.config.timelines]
        if self.config.audiomog:
            args += ["--audiomog", self.config.audiomog]

        self.build_log.clear()
        self.dock_log.show()
        self.dock_log.raise_()
        self.build_log.appendPlainText("$ python %s\n" % " ".join(args))

        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        proc.readyReadStandardOutput.connect(
            lambda: self.build_log.appendPlainText(
                bytes(proc.readAllStandardOutput()).decode("utf-8", "replace").rstrip()))
        proc.finished.connect(self._on_build_finished)
        self._build_proc = proc
        self.build_action.setEnabled(False)
        proc.start(sys.executable, args)

    def _on_build_finished(self, code: int, _status) -> None:
        self._build_proc = None
        self.build_action.setEnabled(True)
        ok = code == 0
        self.build_log.appendPlainText(
            "\n%s (exit %d)" % ("BUILD OK — installed" if ok else "BUILD FAILED", code))
        self.statusBar().showMessage(
            "build finished — installed" if ok else "build FAILED — see log", 8000)

    # -- layout persistence ---------------------------------------------

    def _settings(self) -> QSettings:
        return QSettings(ORG, APP)

    def _restore_layout(self) -> None:
        s = self._settings()
        geo = s.value("geometry")
        if geo:
            self.restoreGeometry(geo)
        state = s.value("windowState")
        if not state:
            # First run: hand the tracker a usable share of the window. Asked
            # for after the event loop starts, because a dock cannot be sized
            # against a layout that has not happened yet.
            QTimer.singleShot(0, lambda: self.resizeDocks(
                [self.dock_timeline], [400], Qt.Vertical))
            return

        self.restoreState(state)
        # A layout saved before the tracker became a dock knows nothing about
        # it. `restoreState` leaves an unknown dock where it was added, which is
        # right, but it can come back hidden - and a hidden tracker is an empty
        # editor.
        self.dock_timeline.show()

    def closeEvent(self, ev) -> None:
        self.mixer.shutdown()
        s = self._settings()
        s.setValue("geometry", self.saveGeometry())
        s.setValue("windowState", self.saveState())
        self.clock.stop()
        self.waveforms.shutdown()
        super().closeEvent(ev)
