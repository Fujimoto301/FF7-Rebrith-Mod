"""
The music picker: choose which track a BGM trigger asks for.

Two columns, because a bank is not a track. `bgm_Corle_005.uasset` holds four
streams and the cutscenes that use it name three of them separately, so
choosing "the music" means choosing a bank *and* which stream of it — the left
column is the 815 banks, the right is what is inside the one you are looking at.
`core/music.py` explains why a stream (a *slice*) rather than a section is the
unit; the short version is that one slice can serve four sections, so sections
are captions and slices are addresses.

Three decisions here are worth not undoing.

**Everything is listed, including what cannot be used.** A trigger's new name
has to fit in the bytes the old one occupies (see `music.capacity_of`), which
rules out roughly half the library for a short cue name. Hiding those would
leave you searching for a track that is there and wondering why it is not — so
they are drawn dim, they still audition, and the reason is on the row and in the
status line. The knowledge that `bgm_Before_Cutscene` exists and is two
characters too long is worth more than a shorter list.

**Preview plays the extracted `.wav`, not the game asset.** AudioMog writes one
per slice beside the bank, which is the same file `mixdown` mixes into the scene
preview — so what you audition here is exactly what you will hear on the
timeline afterwards. A bank nobody has extracted is still selectable; it simply
has nothing to play, and says so.

**Choosing what the scene already plays clears the edit** rather than writing a
repoint that changes nothing, which matches what dragging a cue back to its
authored tick does.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..core.music import MusicBank, MusicLibrary, MusicSlice, cue_name, fits, why_not
from . import theme

try:
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

    HAVE_MULTIMEDIA = True
except ImportError:  # pragma: no cover - Qt built without multimedia
    HAVE_MULTIMEDIA = False

#: `QListWidgetItem.setData` roles for what a row stands for.
BANK_ROLE = Qt.UserRole
SLICE_ROLE = Qt.UserRole + 1


def _mmss(seconds: Optional[float]) -> str:
    if not seconds:
        return ""
    m, s = divmod(int(round(seconds)), 60)
    return "%d:%02d" % (m, s)


class MusicPicker(QDialog):
    """Pick a bank and a slice for one music trigger.

    `chosen` is the cue name to write, `revert` is True when the user asked for
    the scene's own track back. Both are read after `exec()` returns Accepted.
    """

    def __init__(self, library: MusicLibrary, current: str, authored: str,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Point this music trigger at…")
        self.resize(920, 560)

        self.library = library
        #: what the trigger asks for right now (may already be repointed)
        self.current = current
        #: what the scene itself authored — the capacity comes from this one,
        #: because that is the string actually sitting in the asset bytes
        self.authored = authored
        self.chosen: Optional[str] = None
        self.revert = False

        self._player = None
        self._out = None
        self._playing = ""

        cap = len(authored)
        head = QLabel(
            "The scene authors this trigger as <b>%s</b>, and a new name is "
            "written into the bytes that one occupies: <b>%d characters</b> or "
            "fewer, never more.  The budget belongs to the scene's own name, so "
            "repointing never spends it — choosing something shorter today "
            "still leaves all %d characters tomorrow, and <b>%s</b> itself "
            "always fits."
            % (authored, cap, cap, authored),
            self,
        )
        head.setWordWrap(True)
        if current != authored:
            head.setText(
                head.text()
                + "  Right now it is pointed at <b>%s</b>; “Put the scene's own "
                  "track back” undoes that." % current)

        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search the banks — type words in any order")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._refilter)

        self.banks = QListWidget(self)
        self.banks.setUniformItemSizes(True)
        self.banks.currentItemChanged.connect(lambda *_: self._show_bank())

        self.slices = QListWidget(self)
        self.slices.currentItemChanged.connect(lambda *_: self._slice_changed())
        self.slices.itemDoubleClicked.connect(lambda *_: self._accept_choice())

        self.bank_note = QLabel("", self)
        self.bank_note.setProperty("role", "dim")
        self.bank_note.setWordWrap(True)

        left = QWidget(self)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(4)
        ll.addWidget(self.search)
        ll.addWidget(self.banks, 1)

        right = QWidget(self)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        rl.addWidget(QLabel("What is inside this bank", right))
        rl.addWidget(self.slices, 1)
        rl.addWidget(self.bank_note)

        split = QSplitter(Qt.Horizontal, self)
        split.addWidget(left)
        split.addWidget(right)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 4)

        self.play_btn = QPushButton("▶  Listen", self)
        self.play_btn.clicked.connect(self._toggle_play)
        self.status = QLabel("", self)
        self.status.setProperty("role", "dim")
        self.status.setWordWrap(True)

        self.buttons = QDialogButtonBox(self)
        self.ok_btn = self.buttons.addButton("Point at this track",
                                             QDialogButtonBox.AcceptRole)
        self.back_btn = self.buttons.addButton("Put the scene's own track back",
                                               QDialogButtonBox.ResetRole)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.ok_btn.clicked.connect(self._accept_choice)
        self.back_btn.clicked.connect(self._revert)
        self.buttons.rejected.connect(self.reject)
        self.back_btn.setEnabled(current != authored)

        row = QHBoxLayout()
        row.addWidget(self.play_btn)
        row.addWidget(self.status, 1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        lay.addWidget(head)
        lay.addWidget(split, 1)
        lay.addLayout(row)
        lay.addWidget(self.buttons)

        self._fill_banks()
        QTimer.singleShot(0, self.search.setFocus)

    # -- the bank list ----------------------------------------------------

    def _fill_banks(self, query: str = "") -> None:
        self.banks.clear()
        names = self.library.search(query)
        cap = len(self.authored)
        bank_now, _slice_now = self.library.resolve(self.current)
        for name in names:
            item = QListWidgetItem(name)
            item.setData(BANK_ROLE, name)
            if len(name) > cap:
                # Even slice 0 of this bank cannot be named from here. Dim, but
                # present and auditionable — see the module docstring.
                item.setForeground(theme.c(theme.DIM))
                item.setToolTip(why_not(name, self.authored))
            if name == bank_now:
                item.setForeground(theme.c(theme.ACCENT))
            self.banks.addItem(item)
        if not names:
            self.status.setText("nothing matches “%s”" % query)
        if bank_now:
            found = self.banks.findItems(bank_now, Qt.MatchExactly)
            if found:
                self.banks.setCurrentItem(found[0])
                return
        if self.banks.count():
            self.banks.setCurrentRow(0)

    def _refilter(self, text: str) -> None:
        self._fill_banks(text)

    # -- one bank's slices ------------------------------------------------

    def _current_bank(self) -> Optional[MusicBank]:
        item = self.banks.currentItem()
        if item is None:
            return None
        return self.library.bank(item.data(BANK_ROLE))

    def _show_bank(self) -> None:
        self.slices.clear()
        bank = self._current_bank()
        if bank is None:
            self.bank_note.setText("")
            return
        current_bank, slice_now = self.library.resolve(self.current)
        for s in bank.slices:
            name = cue_name(bank.name, s.index)
            bits = ["%d" % s.index, s.label]
            if s.seconds:
                bits.append(_mmss(s.seconds))
            bits.append("→ %s" % name)
            item = QListWidgetItem("   ".join(bits))
            item.setData(SLICE_ROLE, s.index)
            ok = fits(name, self.authored)
            if not ok:
                item.setForeground(theme.c(theme.DIM))
                item.setToolTip(why_not(name, self.authored))
            elif s.unused:
                item.setToolTip("no section in the bank refers to this stream — "
                                "an alternate take, playable all the same")
            if bank.name == current_bank and s.index == slice_now:
                item.setForeground(theme.c(theme.ACCENT))
            self.slices.addItem(item)
        note = []
        if bank.why:
            note.append(bank.why)
        if not bank.extracted:
            note.append("nothing to audition until AudioMog has extracted it")
        self.bank_note.setText("  ·  ".join(note))
        if self.slices.count():
            self.slices.setCurrentRow(0)

    def _current_slice(self) -> Optional[MusicSlice]:
        bank = self._current_bank()
        item = self.slices.currentItem()
        if bank is None or item is None:
            return None
        return bank.slice_at(item.data(SLICE_ROLE))

    def _chosen_name(self) -> str:
        bank = self._current_bank()
        s = self._current_slice()
        if bank is None or s is None:
            return ""
        return cue_name(bank.name, s.index)

    def _slice_changed(self) -> None:
        self._stop()
        name = self._chosen_name()
        s = self._current_slice()
        ok = bool(name) and fits(name, self.authored)
        self.ok_btn.setEnabled(ok)
        self.play_btn.setEnabled(bool(s and s.wav) and HAVE_MULTIMEDIA)
        if not name:
            self.status.setText("")
        elif not ok:
            self.status.setText(why_not(name, self.authored))
        elif s is not None and not s.wav:
            self.status.setText(
                "%s — nothing extracted for this stream, so there is nothing to "
                "hear here. It will still play in game." % name)
        else:
            self.status.setText("%s — this is what the cue will ask for" % name)

    # -- audition ---------------------------------------------------------

    def _ensure_player(self):
        if not HAVE_MULTIMEDIA:
            return None
        if self._player is None:
            self._player = QMediaPlayer(self)
            self._out = QAudioOutput(self)
            self._out.setVolume(0.85)
            self._player.setAudioOutput(self._out)
            self._player.errorOccurred.connect(
                lambda _e, msg: self.status.setText("could not play it: %s" % msg))
            self._player.playbackStateChanged.connect(self._on_state)
        return self._player

    def _on_state(self, state) -> None:
        if not HAVE_MULTIMEDIA:
            return
        playing = state == QMediaPlayer.PlayingState
        self.play_btn.setText("■  Stop" if playing else "▶  Listen")

    def _toggle_play(self) -> None:
        s = self._current_slice()
        if s is None or not s.wav:
            return
        p = self._ensure_player()
        if p is None:
            self.status.setText("no audio backend (PySide6-Multimedia missing)")
            return
        if p.playbackState() == QMediaPlayer.PlayingState and self._playing == s.wav:
            self._stop()
            return
        self._playing = s.wav
        p.setSource(QUrl.fromLocalFile(s.wav))
        p.play()

    def _stop(self) -> None:
        if self._player is not None:
            self._player.stop()
        self._playing = ""

    # -- leaving ----------------------------------------------------------

    def _accept_choice(self) -> None:
        name = self._chosen_name()
        if not name or not fits(name, self.authored):
            return
        self._stop()
        self.chosen = name
        self.revert = name == self.authored
        self.accept()

    def _revert(self) -> None:
        self._stop()
        self.chosen = self.authored
        self.revert = True
        self.accept()

    def closeEvent(self, ev) -> None:
        self._stop()
        super().closeEvent(ev)

    def done(self, result: int) -> None:
        self._stop()
        super().done(result)
