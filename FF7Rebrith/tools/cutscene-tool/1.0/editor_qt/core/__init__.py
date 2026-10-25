"""
Pure model for the cutscene editor.

Nothing in this package may import Qt, touch the network, or read a file except
through `library`. That is what keeps it testable without a window, and it is
the same rule editor_v3 held for its `core/`.
"""

from .units import TimeBase, TickRange, make_range, round_half_up  # noqa: F401
from .timeline import Cutscene, CameraCut, VoiceLine, Subtitle, VfxWindow  # noqa: F401
from .edits import CutSpan, EditState, empty_edits  # noqa: F401
from .lanes import Lane, LaneItem, build_lanes  # noqa: F401
from .impact import impact_of, make_safe, snap_tick  # noqa: F401
from .collapse import (  # noqa: F401
    CollapsePlan,
    Lost,
    Relocation,
    effective,
    plan_collapse,
    unreadable_cues,
)
from .plan import to_plan, from_plan  # noqa: F401
from .library import SceneLibrary, SceneEntry  # noqa: F401
