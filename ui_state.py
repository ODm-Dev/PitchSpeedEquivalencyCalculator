"""Selections for the calculator.

The original app has two inputs: pitch velocity and release distance.
A preset fills both at once. The reaction-time math stays in utils.py.
"""

from __future__ import annotations

import math

import numpy as np

from utils import calculate_equivalent_speeds, calculate_reaction_time, validate_inputs

# Original presets: (name, speed_mph, release_ft).
# These are release points, not rubber-to-plate distances. Stride shortens
# the flight, so 10U is 42 ft and high school / pro are 54 ft.
PRESETS: tuple[tuple[str, int, float], ...] = (
    ("BP", 40, 20.0),
    ("10U", 50, 42.0),
    ("12U", 60, 46.0),
    ("HS", 80, 54.0),
    ("Pro", 95, 54.0),
)

# Marks on the original chart, in release feet.
REFERENCES: tuple[tuple[float, str], ...] = (
    (20.0, "BP (20ft)"),
    (42.0, "10U (42ft)"),
    (46.0, "12U (46ft)"),
    (54.0, "HS/Pro (54ft)"),
)

# Same bounds the old sliders enforced.
SPEED_MIN = 20
SPEED_MAX = 110
SPEED_STEP = 1
SPEED_HOLD = 5
DIST_MIN = 15.0
DIST_MAX = 60.5
DIST_STEP = 0.5
DIST_HOLD = 5.0
STORAGE_KEY = "pitchspeedequiv.selection.v2"

# The original page opened on 60 mph at 46 ft, which is the 12U preset.
DEFAULT_STATE = {
    "speed": 60,
    "distance": 46.0,
    "rev": 0,
}


def snap_distance(feet: float) -> float:
    """Clamp to 15–60.5 ft and snap to the nearest 0.5 ft, half-feet rounding up."""
    feet = float(feet)
    if feet < DIST_MIN:
        feet = DIST_MIN
    if feet > DIST_MAX:
        feet = DIST_MAX
    steps = math.floor((feet - DIST_MIN) / DIST_STEP + 0.5 + 1e-8)
    snapped = DIST_MIN + steps * DIST_STEP
    if snapped > DIST_MAX:
        snapped = DIST_MAX
    if snapped < DIST_MIN:
        snapped = DIST_MIN
    return round(snapped, 4)


def _snap_speed(speed: float) -> int:
    snapped = math.floor(float(speed) + 0.5 + 1e-8)
    return min(SPEED_MAX, max(SPEED_MIN, snapped))


def bump_speed(speed: float, delta: float) -> int:
    """Move velocity by a tap (1 mph) or a hold (5 mph), then clamp."""
    return _snap_speed(_snap_speed(speed) + delta)


def bump_distance(feet: float, delta: float) -> float:
    """Move release distance by a tap (0.5 ft) or a hold (5 ft), then clamp."""
    return snap_distance(float(feet) + delta)


def matching_preset(speed: float, distance: float):
    """Return the preset name when both values match, otherwise None."""
    speed = _snap_speed(speed)
    distance = snap_distance(distance)
    for name, preset_speed, preset_distance in PRESETS:
        if speed == preset_speed and abs(distance - preset_distance) < 1e-6:
            return name
    return None


def normalize_state(raw) -> dict:
    """Return a speed and release distance the calculator can trust."""
    if not isinstance(raw, dict):
        return dict(DEFAULT_STATE)
    try:
        speed = _snap_speed(raw["speed"])
        distance = snap_distance(raw["distance"])
    except (KeyError, TypeError, ValueError):
        return dict(DEFAULT_STATE)
    try:
        rev = int(raw.get("rev", 0))
    except (TypeError, ValueError):
        rev = 0
    if rev < 0:
        rev = 0
    return {"speed": speed, "distance": distance, "rev": rev}


def format_feet(feet: float) -> str:
    feet = float(feet)
    if abs(feet - 60.5) < 1e-6:
        return "60 ft 6 in"
    if abs(feet - round(feet)) < 1e-6:
        return f"{int(round(feet))} ft"
    return f"{feet:.1f} ft"


def format_mph(value: float) -> str:
    return f"{float(value):.1f}"


def equivalent_mph(speed: float, release_feet: float, read_feet: float) -> float:
    """Speed at read_feet with the same time-to-plate as speed at release_feet."""
    reaction = calculate_reaction_time(speed, release_feet)
    speeds = calculate_equivalent_speeds(reaction, np.array([read_feet], dtype=float))
    return float(speeds[0])


def selection_errors(state: dict) -> list[str]:
    return list(validate_inputs(state["speed"], state["distance"]))
