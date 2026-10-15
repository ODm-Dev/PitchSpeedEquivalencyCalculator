"""Selections for the field calculator.

The reaction-time math stays in utils.py. This module only picks mound
distances, clamps the inputs those functions already accept, and calls them.
"""

from __future__ import annotations

import math

import numpy as np

from utils import calculate_equivalent_speeds, calculate_reaction_time, validate_inputs

# Widely used rubber-to-plate distances. Leagues do not all agree, especially
# at 8U and 11U–12U, so every button shows its feet and Custom is always there.
# - 8U: 40 ft. Common USSSA and Pony Pinto kid-pitch distance. Some leagues use 46.
# - 9U, 10U: 46 ft. Little League majors, Pony Mustang, Perfect Game, Cal Ripken.
# - 11U, 12U: 50 ft. Little League Intermediate (50/70), Pony Bronco, Perfect Game.
#   Little League majors often stays at 46 ft through 12U.
# - 13U: 54 ft. Perfect Game and Pony.
# - 14U, high school (NFHS), college (NCAA), MLB: 60 ft 6 in.
PRESETS: tuple[tuple[str, float], ...] = (
    ("8U", 40.0),
    ("9U", 46.0),
    ("10U", 46.0),
    ("11U", 50.0),
    ("12U", 50.0),
    ("13U", 54.0),
    ("14U", 60.5),
    ("HS", 60.5),
    ("College", 60.5),
    ("MLB", 60.5),
)

PRESET_FEET = dict(PRESETS)

# Same bounds the old sliders enforced.
SPEED_MIN = 20
SPEED_MAX = 110
SPEED_CHIPS = tuple(range(40, 101, 5))
DIST_MIN = 15.0
DIST_MAX = 60.5
DIST_STEP = 0.5
STORAGE_KEY = "pitchspeedequiv.selection.v1"

DEFAULT_STATE = {
    "speed": 60,
    "from_preset": "10U",
    "from_feet": 46.0,
    "to_preset": "MLB",
    "to_feet": 60.5,
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


def _normalize_side(preset, feet, fallback_preset: str, fallback_feet: float):
    if preset in PRESET_FEET:
        return preset, PRESET_FEET[preset]
    try:
        return "custom", snap_distance(feet)
    except (TypeError, ValueError):
        return fallback_preset, fallback_feet


def normalize_state(raw) -> dict:
    """Return a complete selection the calculator can trust."""
    if not isinstance(raw, dict):
        return dict(DEFAULT_STATE)
    try:
        speed = _snap_speed(raw["speed"])
    except (KeyError, TypeError, ValueError):
        return dict(DEFAULT_STATE)
    from_preset, from_feet = _normalize_side(
        raw.get("from_preset"), raw.get("from_feet"), "10U", 46.0
    )
    to_preset, to_feet = _normalize_side(
        raw.get("to_preset"), raw.get("to_feet"), "MLB", 60.5
    )
    try:
        rev = int(raw.get("rev", 0))
    except (TypeError, ValueError):
        rev = 0
    if rev < 0:
        rev = 0
    return {
        "speed": speed,
        "from_preset": from_preset,
        "from_feet": from_feet,
        "to_preset": to_preset,
        "to_feet": to_feet,
        "rev": rev,
    }


def swapped(state: dict) -> dict:
    """Flip the from and to mounds. The radar speed stays with From."""
    current = normalize_state(state)
    return normalize_state(
        {
            "speed": current["speed"],
            "from_preset": current["to_preset"],
            "from_feet": current["to_feet"],
            "to_preset": current["from_preset"],
            "to_feet": current["from_feet"],
            "rev": current["rev"],
        }
    )


def format_feet(feet: float) -> str:
    feet = float(feet)
    if abs(feet - 60.5) < 1e-6:
        return "60 ft 6 in"
    if abs(feet - round(feet)) < 1e-6:
        return f"{int(round(feet))} ft"
    return f"{feet:.1f} ft"


def format_feet_spoken(feet: float) -> str:
    feet = float(feet)
    if abs(feet - 60.5) < 1e-6:
        return "60 feet 6 inches"
    if abs(feet - round(feet)) < 1e-6:
        return f"{int(round(feet))} feet"
    return f"{feet:.1f} feet"


def format_mph(value: float) -> str:
    return f"{float(value):.1f}"


def mound_label(preset: str, feet: float) -> str:
    distance = format_feet(feet)
    if preset not in PRESET_FEET:
        return distance
    return f"{preset} ({distance})"


def equivalent_mph(speed: float, from_feet: float, to_feet: float) -> float:
    """Speed at to_feet with the same time-to-plate as speed at from_feet."""
    reaction = calculate_reaction_time(speed, from_feet)
    speeds = calculate_equivalent_speeds(reaction, np.array([to_feet], dtype=float))
    return float(speeds[0])


def selection_errors(state: dict) -> list[str]:
    errors = list(validate_inputs(state["speed"], state["from_feet"]))
    for error in validate_inputs(state["speed"], state["to_feet"]):
        if error.startswith("Distance") and error not in errors:
            errors.append(error)
    return errors
