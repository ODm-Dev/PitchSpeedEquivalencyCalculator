"""Browser control panel. Streamlit serves it; the page still runs with main.py."""

from __future__ import annotations

import os

import streamlit.components.v1 as components

from ui_state import (
    DIST_HOLD,
    DIST_MAX,
    DIST_MIN,
    DIST_STEP,
    PRESETS,
    SPEED_HOLD,
    SPEED_MAX,
    SPEED_MIN,
    SPEED_STEP,
    STORAGE_KEY,
)

_component = components.declare_component(
    "field_controls",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "components", "field_controls"),
)


def field_controls(state: dict):
    """Render the preset row and the two steppers. Returns the latest selection, or None."""
    return _component(
        state=state,
        presets=[
            {"id": name, "speed": speed, "distance": distance}
            for name, speed, distance in PRESETS
        ],
        speed_min=SPEED_MIN,
        speed_max=SPEED_MAX,
        speed_step=SPEED_STEP,
        speed_hold=SPEED_HOLD,
        distance_min=DIST_MIN,
        distance_max=DIST_MAX,
        distance_step=DIST_STEP,
        distance_hold=DIST_HOLD,
        storage_key=STORAGE_KEY,
        key="field_controls",
        default=None,
    )
