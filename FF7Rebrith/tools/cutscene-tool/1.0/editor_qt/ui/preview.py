"""
The preview widgets: camera view, top-down map, lip sync.

Straight ports of the canvas drawing in editor_v3/src/preview, with the maths
moved to core/stage.py. The difference that matters is layout: the camera view
now keeps 16:9 and takes whatever width the window gives it, instead of being
pinned at 426x240 by an HTML attribute.
"""

from __future__ import annotations

import math
from typing import List, Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..core.stage import (
    AIM_Z,
    ASPECT,
    MouthState,
    StageFrame,
    blend_mouth,
    in_frame,
    project,
    turns,
)
from . import sprites, theme


class _Base(QWidget):
    """Shared chrome: dark plate, thin border, antialiasing."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(False)

    def _plate(self, p: QPainter) -> QRectF:
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(r, theme.c(theme.STAGE_BG))
        p.setPen(QPen(theme.c(theme.GRID), 1))
        p.drawRect(r)
        return r


class CameraView(_Base):
    """What the shot is pointing at, at 16:9, as wide as the window allows."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._frame: Optional[StageFrame] = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(320, 180)

    def set_frame(self, frame: Optional[StageFrame]) -> None:
        self._frame = frame
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(960, 540)

    def heightForWidth(self, w: int) -> int:
        return int(w / ASPECT)

    def _viewport(self) -> QRectF:
        """The 16:9 rectangle inside the widget, centred."""
        w, h = self.width(), self.height()
        if w / max(1, h) > ASPECT:
            vw = h * ASPECT
            return QRectF((w - vw) / 2, 0, vw, h)
        vh = w / ASPECT
        return QRectF(0, (h - vh) / 2, w, vh)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), theme.c(theme.BG))
        vp = self._viewport()
        p.fillRect(vp, theme.c(theme.STAGE_BG))
        p.setPen(QPen(theme.c(theme.GRID), 1))
        p.drawRect(vp.adjusted(0.5, 0.5, -0.5, -0.5))

        # rule of thirds
        p.setPen(QPen(QColor("#1b1e27"), 1))
        for k in (1, 2):
            x = vp.left() + vp.width() * k / 3
            y = vp.top() + vp.height() * k / 3
            p.drawLine(QPointF(x, vp.top()), QPointF(x, vp.bottom()))
            p.drawLine(QPointF(vp.left(), y), QPointF(vp.right(), y))

        frame = self._frame
        if not frame or not frame.cam:
            p.setPen(QColor("#575c70"))
            p.setFont(theme.ui_font(9))
            p.drawText(vp.adjusted(12, 10, -12, 0), Qt.AlignLeft | Qt.AlignTop,
                       "no camera data")
            return

        cam = frame.cam
        th = math.tan(math.radians(cam[6] / 2))
        p.setFont(theme.ui_font(8))
        models = sprites.shared()

        for actor, pos, pr in frame.points:
            if pr is None:
                continue
            sx = vp.left() + (pr.x * 0.5 + 0.5) * vp.width()
            sy = vp.top() + (0.5 - pr.y * 0.5) * vp.height()
            visible = in_frame(pr)
            px_per_cm = (1.0 / pr.d) / (th / ASPECT) * (vp.height() / 2)
            hpx = 170.0 * px_per_cm            # a ~170cm figure at this distance
            who = StageFrame.who(actor)
            col = theme.c(theme.character_color(who))

            p.setOpacity(1.0 if visible else 0.25)
            top = None
            if models.has(who) and turns(actor):
                # the root is pelvis height, not the feet: drop to the floor and
                # project that, rather than offsetting the projected root, so it
                # stays right when the camera pitches
                feet = project(cam, pos, -models.root_cm(who)) or pr
                top = models.draw(
                    p, who,
                    vp.left() + (feet.x * 0.5 + 0.5) * vp.width(),
                    vp.top() + (0.5 - feet.y * 0.5) * vp.height(),
                    px_per_cm,
                    cam[5],
                    pos[3] if len(pos) > 3 else 0.0,
                )
            if top is None:
                pen = QPen(col, max(2.0, hpx * 0.1))
                pen.setCapStyle(Qt.RoundCap)
                p.setPen(pen)
                p.drawLine(QPointF(sx, sy + hpx * 0.12), QPointF(sx, sy + hpx * 0.75))
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(col))
                r = max(2.5, hpx * 0.13)
                p.drawEllipse(QPointF(sx, sy), r, r)
                top = sy

            if visible or abs(pr.x) < 1.6:
                p.setOpacity(1.0 if visible else 0.4)
                p.setPen(QColor("#ffffff"))
                label = actor.get("label", "")
                ty = top - max(5.0, hpx * 0.16)
                p.drawText(
                    QRectF(sx - 120, ty - 14, 240, 14),
                    Qt.AlignHCenter | Qt.AlignBottom,
                    label,
                )
        p.setOpacity(1.0)


class TopDownView(_Base):
    """Where everyone is standing, and which way the camera is looking."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._frame: Optional[StageFrame] = None
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_frame(self, frame: Optional[StageFrame]) -> None:
        self._frame = frame
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(260, 260)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        self._plate(p)
        frame = self._frame
        if not frame or not frame.points:
            return

        w, h = self.width(), self.height()
        pts = [q[1] for q in frame.points]
        allp = list(pts) + ([frame.cam] if frame.cam else [])
        min_x = min(q[0] for q in allp)
        max_x = max(q[0] for q in allp)
        min_y = min(q[1] for q in allp)
        max_y = max(q[1] for q in allp)
        pad = 120.0
        span = max(max_x - min_x, max_y - min_y, 300.0) + pad * 2
        ccx = (min_x + max_x) / 2
        ccy = (min_y + max_y) / 2

        def to_px(q) -> QPointF:
            # world X is up on the map, world Y is right
            return QPointF(
                w / 2 + ((q[1] - ccy) / span) * w,
                h / 2 - ((q[0] - ccx) / span) * h,
            )

        if frame.cam:
            cam = frame.cam
            c = to_px(cam)
            yaw = math.radians(cam[5])
            half = math.radians(cam[6] / 2)
            length = 70.0

            def dir_at(a: float) -> QPointF:
                return QPointF(math.sin(a) * length, -math.cos(a) * length)

            cone = QPainterPath(c)
            cone.lineTo(c + dir_at(yaw - half))
            cone.lineTo(c + dir_at(yaw + half))
            cone.closeSubpath()
            p.fillPath(cone, QBrush(theme.c(theme.PLAY, 0.16)))
            p.setPen(QPen(theme.c(theme.PLAY), 1))
            p.drawPath(cone)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(theme.c(theme.PLAY)))
            p.drawEllipse(c, 3.5, 3.5)

        p.setFont(theme.ui_font(7))
        for actor, pos, pr in frame.points:
            c = to_px(pos)
            col = theme.c(theme.character_color(StageFrame.who(actor)))
            lit = in_frame(pr)
            p.setOpacity(1.0 if lit else 0.42)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(col))
            p.drawEllipse(c, 4, 4)
            ya = math.radians(pos[3] if len(pos) > 3 else 0)
            p.setPen(QPen(col, 1.5))
            p.drawLine(
                c, c + QPointF(math.sin(ya) * 11, -math.cos(ya) * 11)
            )
            p.setPen(QColor(theme.TEXT if lit else "#767b8f"))
            p.drawText(
                QRectF(c.x() - 70, c.y() - 21, 140, 14),
                Qt.AlignHCenter | Qt.AlignBottom,
                actor.get("label", ""),
            )
        p.setOpacity(1.0)


class MouthView(_Base):
    """Rough by design - it exists to show that a cut has landed mid-word."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._state: Optional[MouthState] = None
        self.setMinimumSize(120, 110)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_state(self, state: Optional[MouthState]) -> None:
        self._state = state
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(170, 140)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        self._plate(p)
        st = self._state
        w, h, curl, teeth, total = blend_mouth(st)

        cw, ch = self.width(), self.height()
        mid_x = cw / 2
        mid_y = ch / 2 + 4
        rx = w * cw * 0.36
        ry = max(1.2, h * ch * 0.34)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#c76b7a" if total > 0 else "#3a3f4d")))
        p.drawEllipse(QPointF(mid_x, mid_y), rx + 5, ry + 5)
        p.setBrush(QBrush(QColor("#2a1016")))
        p.drawEllipse(QPointF(mid_x, mid_y), rx, ry)

        if teeth > 0.15 and ry > 3:
            col = QColor("#eef0f5")
            col.setAlphaF(min(1.0, teeth))
            p.setBrush(QBrush(col))
            p.drawRect(
                QRectF(mid_x - rx * 0.8, mid_y - ry, rx * 1.6, min(ry * 0.55, 5.0))
            )
        if curl > 0.2 and ry > 2:
            col = QColor("#eef0f5")
            col.setAlphaF(min(1.0, curl))
            p.setPen(QPen(col, 1.5))
            p.drawLine(
                QPointF(mid_x - rx * 0.7, mid_y + ry * 0.4),
                QPointF(mid_x + rx * 0.7, mid_y + ry * 0.4),
            )
            p.setPen(Qt.NoPen)

        p.setPen(QColor(theme.TEXT if st else "#3c3f4d"))
        p.setFont(theme.ui_font(11, bold=True))
        p.drawText(QRectF(0, 4, cw, 20), Qt.AlignHCenter | Qt.AlignVCenter,
                   st.phoneme if st else "–")

        if st:
            p.setPen(theme.c(theme.ACCENT))
            p.setFont(theme.ui_font(8))
            p.drawText(QRectF(0, ch - 30, cw, 14), Qt.AlignHCenter, st.actor or "")
            p.setPen(QColor("#767b8f"))
            p.setFont(theme.ui_font(7))
            top = "  ".join(
                "%s %.1f" % (k, v)
                for k, v in sorted(st.shapes.items(), key=lambda kv: -kv[1])[:3]
            )
            p.drawText(QRectF(0, ch - 17, cw, 14), Qt.AlignHCenter, top)


class SubtitleBar(QWidget):
    """The subtitle window - now directly under the picture, where it belongs.

    In the browser build this sat *above* the camera view because it was the
    first block in the document. Here it is a sibling widget placed after it,
    which is the whole reason for the move.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._actor = ""
        self._text = ""
        self._idle = "— press Space to play, drag the ruler to scrub —"
        self.setMinimumHeight(66)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_line(self, actor: str, text: str) -> None:
        if (actor, text) != (self._actor, self._text):
            self._actor = actor
            self._text = text
            self.update()

    def clear_line(self) -> None:
        self.set_line("", "")

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        r = QRectF(self.rect())
        p.fillRect(r, QColor("#101116"))
        p.setPen(QPen(QColor("#000000"), 1))
        p.drawLine(r.topLeft(), r.topRight())

        if self._text or self._actor:
            p.setPen(theme.c(theme.ACCENT))
            p.setFont(theme.ui_font(9, bold=True))
            p.drawText(QRectF(r.left(), r.top() + 8, r.width(), 16),
                       Qt.AlignHCenter, self._actor)
            p.setPen(QColor(theme.TEXT))
            f = theme.ui_font(13)
            p.setFont(f)
            p.drawText(
                QRectF(r.left() + 24, r.top() + 26, r.width() - 48, r.height() - 32),
                Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                self._text,
            )
        else:
            p.setPen(QColor("#3c3f4d"))
            p.setFont(theme.ui_font(9))
            p.drawText(r, Qt.AlignCenter, self._idle)
