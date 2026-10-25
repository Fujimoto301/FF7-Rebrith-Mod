"""
Stage maths: where the camera is pointing and who is in frame.

Positions are sampled actor roots, projected through the sampled camera - enough
to tell whether a cut lands on someone's face or on an empty set. UE's rotation
convention (roll/pitch/yaw about X/Y/Z, X forward) is why the axis maths looks
the way it does.

Kept out of the widget so it can be tested without a window, and so the same
numbers feed both the camera view and the top-down map.
"""

from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .characters import canonical
from .timeline import LipLine, SceneSample

#: Cameras frame roughly 50cm above the actor root - calibrated, not derived.
AIM_Z = 50.0
ASPECT = 16.0 / 9.0

Vec3 = Tuple[float, float, float]


def ue_axes(roll: float, pitch: float, yaw: float) -> Tuple[Vec3, Vec3, Vec3]:
    r = math.radians(roll)
    p = math.radians(pitch)
    y = math.radians(yaw)
    sr, cr = math.sin(r), math.cos(r)
    sp, cp = math.sin(p), math.cos(p)
    sy, cy = math.sin(y), math.cos(y)
    forward = (cp * cy, cp * sy, sp)
    right = (sr * sp * cy - cr * sy, sr * sp * sy + cr * cy, -sr * cp)
    up = (-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp)
    return forward, right, up


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


@dataclass(frozen=True)
class Projected:
    #: -1..1 across the frame
    x: float
    #: -1..1 up the frame
    y: float
    #: distance in front of the camera, cm
    d: float


def project(cam: Sequence[float], p: Sequence[float], dz: float = AIM_Z) -> Optional[Projected]:
    """`cam` is [x, y, z, roll, pitch, yaw, fov]; `p` is an actor root."""
    fwd_axis, right_axis, up_axis = ue_axes(cam[3], cam[4], cam[5])
    d = (p[0] - cam[0], p[1] - cam[1], p[2] + dz - cam[2])
    fwd = _dot(d, fwd_axis)
    if fwd <= 1:
        return None
    th = math.tan(math.radians(cam[6] / 2))
    return Projected(
        x=_dot(d, right_axis) / fwd / th,
        y=_dot(d, up_axis) / fwd / (th / ASPECT),
        d=fwd,
    )


def in_frame(pr: Optional[Projected]) -> bool:
    return bool(pr) and abs(pr.x) < 1 and abs(pr.y) < 1.6


def turns(actor: Dict[str, Any]) -> bool:
    """Does the scene actually rotate this actor?

    Most actors are turned by their animation rather than by the transform
    track, so their sampled yaw is a constant zero - across the extracted
    cutscenes only 3% of cast actors are ever rotated by the track. A character
    model drawn from a yaw like that would face one arbitrary direction for the
    whole scene, so the ones without it keep the pin, which claims nothing about
    which way anybody is looking.
    """
    return any(p and len(p) > 3 and p[3] for p in (actor.get("p") or ()))


def sample_index(ticks: Sequence[float], t: float) -> int:
    """Nearest sample index to a tick."""
    if not ticks:
        return 0
    lo = bisect_left(ticks, t)
    if lo >= len(ticks):
        return len(ticks) - 1
    if lo > 0 and abs(ticks[lo - 1] - t) < abs(ticks[lo] - t):
        lo -= 1
    return lo


@dataclass
class StageFrame:
    """Everything both preview widgets need for one playhead position."""

    cam: Optional[List[float]]
    #: (actor dict, world position, projection or None)
    points: List[Tuple[Dict[str, Any], List[float], Optional[Projected]]]

    @property
    def onscreen(self) -> List[Tuple[str, float, float]]:
        out = [
            (a.get("label", ""), pr.d, pr.x)
            for a, _p, pr in self.points
            if in_frame(pr)
        ]
        out.sort(key=lambda o: o[1])
        return out

    @staticmethod
    def who(actor: Dict[str, Any]) -> str:
        """Canonical character key for one of `points`' actor dicts."""
        return canonical(actor.get("label", ""), actor.get("kind"))


def stage_at(scene: Optional[SceneSample], playhead: float) -> Optional[StageFrame]:
    if not scene:
        return None
    i = sample_index(scene.ticks, playhead)
    cam = scene.cam[i] if i < len(scene.cam) else None
    points = []
    for a in scene.actors:
        p = a["p"][i] if i < len(a.get("p") or []) else None
        if not p:
            continue
        points.append((a, p, project(cam, p) if cam else None))
    # far to near, so the nearest figure is drawn last
    points.sort(key=lambda q: (-(q[2].d) if q[2] else -1e18))
    return StageFrame(cam=cam, points=points)


# -- lip sync ------------------------------------------------------------

#: [width, height, upperLipCurl, teeth] per viseme.
VISEME = {
    "bmp": (0.62, 0.04, 0.0, 0.0),
    "fv": (0.58, 0.16, 0.5, 1.0),
    "aa": (0.6, 0.92, 0.0, 0.0),
    "ee": (1.0, 0.3, 0.0, 1.0),
    "oo": (0.34, 0.62, 0.0, 0.0),
    "ln": (0.52, 0.36, 0.0, 1.0),
    "sh": (0.46, 0.48, 0.0, 0.0),
}


@dataclass(frozen=True)
class MouthState:
    phoneme: str
    shapes: Dict[str, float]
    actor: str
    voice: str


def lip_at(lines: Sequence[LipLine], t: float) -> Optional[MouthState]:
    for ln in lines:
        if not ln.frames:
            continue
        if t < ln.frames[0][0] or t > ln.frames[-1][1]:
            continue
        for f in ln.frames:
            if f[0] <= t < f[1]:
                return MouthState(
                    phoneme=f[2], shapes=f[3] or {}, actor=ln.actor, voice=ln.voice
                )
    return None


def blend_mouth(state: Optional[MouthState]) -> Tuple[float, float, float, float, float]:
    """(width, height, curl, teeth, total weight) - the shape to draw."""
    w, h, curl, teeth, total = 0.55, 0.1, 0.0, 0.0, 0.0
    if state and state.shapes:
        acc = [0.0, 0.0, 0.0, 0.0]
        for k, v in state.shapes.items():
            p = VISEME.get(k)
            if not p or not v:
                continue
            for j in range(4):
                acc[j] += p[j] * v
            total += v
        if total > 0:
            w, h, curl, teeth = (a / total for a in acc)
    return w, h, curl, teeth, total
