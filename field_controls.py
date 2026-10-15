"""Browser control panel. Streamlit serves it; the page still runs with main.py."""

from __future__ import annotations

import os

import streamlit.components.v1 as components

from ui_state import (
    DIST_MAX,
    DIST_MIN,
    DIST_STEP,
    PRESETS,
    SPEED_CHIPS,
    SPEED_MAX,
    SPEED_MIN,
    STORAGE_KEY,
)

_component = components.declare_component(
    "field_controls",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "components", "field_controls"),
)


def field_controls(state: dict, result: dict):
    """Render the tap targets and return the latest selection, or None."""
    return _component(
        state=state,
        result=result,
        presets=[{"id": preset_id, "feet": feet} for preset_id, feet in PRESETS],
        speed_min=SPEED_MIN,
        speed_max=SPEED_MAX,
        speed_chips=list(SPEED_CHIPS),
        distance_min=DIST_MIN,
        distance_max=DIST_MAX,
        distance_step=DIST_STEP,
        storage_key=STORAGE_KEY,
        key="field_controls",
        default=None,
    )
