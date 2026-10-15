"""Tests for mound presets and input clamping. The physics lives in test_utils."""

import unittest

from ui_state import (
    DEFAULT_STATE,
    PRESETS,
    SPEED_CHIPS,
    DIST_MAX,
    DIST_MIN,
    equivalent_mph,
    format_feet,
    format_mph,
    mound_label,
    normalize_state,
    selection_errors,
    snap_distance,
    swapped,
)
from utils import calculate_equivalent_speeds, calculate_reaction_time, validate_inputs
import numpy as np


class TestPresets(unittest.TestCase):
    def test_age_ladder_uses_common_mound_distances(self):
        self.assertEqual(
            PRESETS,
            (
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
            ),
        )

    def test_every_preset_distance_is_accepted_by_the_existing_validator(self):
        for _name, feet in PRESETS:
            self.assertEqual(validate_inputs(60, feet), [])
            self.assertGreaterEqual(feet, DIST_MIN)
            self.assertLessEqual(feet, DIST_MAX)

    def test_full_distance_is_sixty_feet_six_inches(self):
        for name in ("14U", "HS", "College", "MLB"):
            self.assertEqual(dict(PRESETS)[name], 60.5)
            self.assertEqual(format_feet(dict(PRESETS)[name]), "60 ft 6 in")


class TestSnapAndNormalize(unittest.TestCase):
    def test_snap_distance_grid(self):
        self.assertEqual(snap_distance(15), 15.0)
        self.assertEqual(snap_distance(60.5), 60.5)
        self.assertEqual(snap_distance(46), 46.0)
        self.assertEqual(snap_distance(46.2), 46.0)
        self.assertEqual(snap_distance(46.25), 46.5)
        self.assertEqual(snap_distance(60.2), 60.0)
        self.assertEqual(snap_distance(60.4), 60.5)
        self.assertEqual(snap_distance(10), 15.0)
        self.assertEqual(snap_distance(80), 60.5)

    def test_known_preset_wins_over_a_mismatched_distance(self):
        state = normalize_state(
            {
                "speed": 60,
                "from_preset": "10U",
                "from_feet": 20,
                "to_preset": "MLB",
                "to_feet": 46,
                "rev": 2,
            }
        )
        self.assertEqual(state["from_feet"], 46.0)
        self.assertEqual(state["to_feet"], 60.5)
        self.assertEqual(state["rev"], 2)

    def test_custom_distance_snaps_and_speed_clamps_to_the_old_slider_bounds(self):
        low = normalize_state(
            {
                "speed": 5,
                "from_preset": "custom",
                "from_feet": 46.2,
                "to_preset": "custom",
                "to_feet": 70,
                "rev": 1,
            }
        )
        self.assertEqual(low["speed"], 20)
        self.assertEqual(low["from_feet"], 46.0)
        self.assertEqual(low["to_feet"], 60.5)

        high = normalize_state({"speed": 140, "from_preset": "HS", "to_preset": "8U"})
        self.assertEqual(high["speed"], 110)
        self.assertEqual(high["from_preset"], "HS")
        self.assertEqual(high["to_preset"], "8U")

    def test_corrupt_payload_falls_back_to_the_default(self):
        self.assertEqual(normalize_state(None), DEFAULT_STATE)
        self.assertEqual(normalize_state({"from_preset": "10U"}), DEFAULT_STATE)
        self.assertEqual(normalize_state("nope"), DEFAULT_STATE)

    def test_default_selection_is_valid(self):
        self.assertEqual(selection_errors(DEFAULT_STATE), [])
        self.assertEqual(DEFAULT_STATE["speed"], 60)
        self.assertEqual(DEFAULT_STATE["from_feet"], 46.0)
        self.assertEqual(DEFAULT_STATE["to_feet"], 60.5)


class TestSwapAndFormatting(unittest.TestCase):
    def test_swap_flips_distances_and_keeps_speed(self):
        flipped = swapped(DEFAULT_STATE)
        self.assertEqual(flipped["speed"], 60)
        self.assertEqual(flipped["from_preset"], "MLB")
        self.assertEqual(flipped["from_feet"], 60.5)
        self.assertEqual(flipped["to_preset"], "10U")
        self.assertEqual(flipped["to_feet"], 46.0)

    def test_labels(self):
        self.assertEqual(format_feet(46), "46 ft")
        self.assertEqual(format_feet(46.5), "46.5 ft")
        self.assertEqual(format_feet(60.5), "60 ft 6 in")
        self.assertEqual(format_mph(78.913043478), "78.9")
        self.assertEqual(mound_label("10U", 46), "10U (46 ft)")
        self.assertEqual(mound_label("custom", 47.5), "47.5 ft")
        self.assertEqual(mound_label("MLB", 60.5), "MLB (60 ft 6 in)")

    def test_speed_chips_are_five_mph_steps(self):
        self.assertEqual(SPEED_CHIPS[0], 40)
        self.assertEqual(SPEED_CHIPS[-1], 100)
        self.assertTrue(all(b - a == 5 for a, b in zip(SPEED_CHIPS, SPEED_CHIPS[1:])))


class TestEquivalentUsesExistingMath(unittest.TestCase):
    def test_wrapper_matches_utils_and_the_distance_ratio(self):
        speed, from_feet, to_feet = 60, 46, 60.5
        reaction = calculate_reaction_time(speed, from_feet)
        direct = float(
            calculate_equivalent_speeds(reaction, np.array([to_feet]))[0]
        )
        self.assertAlmostEqual(equivalent_mph(speed, from_feet, to_feet), direct)
        self.assertAlmostEqual(direct, speed * to_feet / from_feet)
        self.assertAlmostEqual(equivalent_mph(60, 46, 60.5), 78.91304347826087)

    def test_same_mound_returns_the_same_speed(self):
        self.assertAlmostEqual(equivalent_mph(88, 54, 54), 88)


if __name__ == "__main__":
    unittest.main()
