"""
The 1997 field models, as sprites for the camera view.

A pin says where somebody is standing. It cannot say who, which is the question
the camera view is usually being asked - is this shot on Cloud's face or on the
back of a soldier's head. So the cast is drawn as their original field models
instead, baked to a sprite atlas by `render_sprites.py` in the tool root.

Nothing here is animated. The models stand in their field pose; only the facing
and the size change, and both come out of the sampled scene data.

Everything is optional. No atlas, or an actor with no model - enemies, NPCs,
Sephiroth - falls back to the pin, and the two styles read fine side by side.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPixmap

#: The tool root, where render_sprites.py leaves chars.png and chars.json.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Never draw a sprite shorter than this - someone 50m away should still be a
#: speck rather than nothing at all.
_MIN_PX = 7.0


class CharacterSprites:
    """The atlas, or a stand-in for it that answers "no" to everything."""

    def __init__(self, root: Optional[str] = None) -> None:
        self._cells: Dict[str, Dict[str, Any]] = {}
        self._angles = 0
        self._cm_per_px = 1.0
        self._sheet: Optional[QPixmap] = None
        base = root or _ROOT
        try:
            with open(os.path.join(base, "chars.json"), encoding="utf-8") as f:
                meta = json.load(f)
            sheet = QPixmap(os.path.join(base, meta.get("sheet", "chars.png")))
            if sheet.isNull() or not meta.get("chars") or not meta.get("angles"):
                return
            self._cells = meta["chars"]
            self._angles = int(meta["angles"])
            self._cm_per_px = float(meta.get("cmPerPx", 1.0))
            self._sheet = sheet
        except (OSError, ValueError, KeyError):
            self._sheet = None      # pins it is

    @property
    def available(self) -> bool:
        return self._sheet is not None

    def has(self, key: str) -> bool:
        return self._sheet is not None and key in self._cells

    def root_cm(self, key: str) -> float:
        """How far this character's actor root sits above the floor.

        The sampled root is roughly pelvis height, so a model planted on it
        floats. `render_sprites.py` documents where the number comes from.
        """
        cell = self._cells.get(key) or {}
        return float(cell.get("root", 0.0))

    def column(self, cam_yaw: float, actor_yaw: float) -> int:
        """Which column faces the camera.

        Column 0 is the model looking straight down the lens and columns advance
        anticlockwise, so this is just where the camera stands relative to the
        way the actor is facing.
        """
        step = 360.0 / self._angles
        rel = (cam_yaw + 180.0 - actor_yaw) % 360.0
        return int(round(rel / step)) % self._angles

    def draw(
        self,
        p: QPainter,
        key: str,
        foot_x: float,
        foot_y: float,
        px_per_cm: float,
        cam_yaw: float,
        actor_yaw: float,
    ) -> Optional[float]:
        """Draw `key` standing at (foot_x, foot_y). Returns the crown's y.

        `px_per_cm` is the on-screen size of a world centimetre at the actor's
        distance - the same number the pin uses for its height.
        """
        cell = self._cells.get(key) if self._sheet is not None else None
        if not cell:
            return None
        cw, ch = float(cell["cw"]), float(cell["ch"])
        scale = max(self._cm_per_px * px_per_cm, _MIN_PX / ch)
        src = QRectF(self.column(cam_yaw, actor_yaw) * cw, float(cell["y"]), cw, ch)
        dst = QRectF(
            foot_x - float(cell["ox"]) * scale,
            foot_y - float(cell["oy"]) * scale,
            cw * scale,
            ch * scale,
        )
        was = p.renderHints()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.drawPixmap(dst, self._sheet, src)
        p.setRenderHints(was)
        return foot_y - (float(cell["cm"]) / self._cm_per_px) * scale


_shared: Optional[CharacterSprites] = None


def shared() -> CharacterSprites:
    """One atlas for the whole application; loaded the first time it is asked for."""
    global _shared
    if _shared is None:
        _shared = CharacterSprites()
    return _shared
