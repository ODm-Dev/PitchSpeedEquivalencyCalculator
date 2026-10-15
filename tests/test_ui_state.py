"""Tests for the original presets and the stepper clamps. Physics stays in test_utils."""

import unittest

import numpy as np

from ui_state import (
    DEFAULT_STATE,
    DIST_HOLD,
    DIST_MAX,
    DIST_MIN,
    DIST_STEP,
    PRESETS,
    REFERENCES,
    SPEED_HOLD,
    SPEED_MAX,
    SPEED_MIN,
    SPEED_STEP,
    bump_distance,
    bump_speed,
    equivalent_mph,
    format_feet,
    format_mph,
    matching_preset,
    normalize_state,
    selection_errors,
    snap_distance,
)
from utils import calculate_equivalent_speeds, calculate_reaction_time, validate_inputs


class TestOriginalPresets(unittest.TestCase):
    def test_presets_are_the_original_release_points(self):
        self.assertEqual(
            PRESETS,
            (
                ("BP", 40, 20.0),
                ("10U", 50, 42.0),
                ("12U", 60, 46.0),
                ("HS", 80, 54.0),
                ("Pro", 95, 54.0),
            ),
        )

    def test_chart_references_match_the_original_labels(self):
        self.assertEqual(
            REFERENCES,
            (
                (20.0, "BP (20ft)"),
                (42.0, "10U (42ft)"),
                (46.0, "12U (46ft)"),
                (54.0, "HS/Pro (54ft)"),
            ),
        )

    def test_every_preset_is_accepted_by_the_existing_validator(self):
        for _name, speed, feet in PRESETS:
            self.assertEqual(validate_inputs(speed, feet), [])
            self.assertGreaterEqual(feet, DIST_MIN)
            self.assertLessEqual(feet, DIST_MAX)
            self.assertGreaterEqual(speed, SPEED_MIN)
            self.assertLessEqual(speed, SPEED_MAX)

    def test_default_is_the_original_twelve_u_point(self):
        self.assertEqual(DEFAULT_STATE["speed"], 60)
        self.assertEqual(DEFAULT_STATE["distance"], 46.0)
        self.assertEqual(matching_preset(60, 46), "12U")
        self.assertEqual(selection_errors(DEFAULT_STATE), [])


class TestMatchingAndNormalize(unittest.TestCase):
    def test_each_preset_matches_only_its_own_pair(self):
        self.assertEqual(matching_preset(40, 20), "BP")
        self.assertEqual(matching_preset(50, 42), "10U")
        self.assertEqual(matching_preset(80, 54), "HS")
        self.assertEqual(matching_preset(95, 54), "Pro")
        self.assertIsNone(matching_preset(61, 46))
        self.assertIsNone(matching_preset(80, 54.5))

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

    def test_normalize_clamps_to_the_old_slider_bounds(self):
        low = normalize_state({"speed": 5, "distance": 10, "rev": 3})
        self.assertEqual(low["speed"], 20)
        self.assertEqual(low["distance"], 15.0)
        self.assertEqual(low["rev"], 3)

        high = normalize_state({"speed": 140, "distance": 80})
        self.assertEqual(high["speed"], SPEED_MAX)
        self.assertEqual(high["distance"], DIST_MAX)

    def test_old_from_to_payload_falls_back_to_the_default(self):
        self.assertEqual(normalize_state(None), DEFAULT_STATE)
        self.assertEqual(normalize_state({"from_feet": 46, "to_feet": 60.5}), DEFAULT_STATE)
        self.assertEqual(normalize_state("nope"), DEFAULT_STATE)

    def test_labels(self):
        self.assertEqual(format_feet(46), "46 ft")
        self.assertEqual(format_feet(46.5), "46.5 ft")
        self.assertEqual(format_feet(60.5), "60 ft 6 in")
        self.assertEqual(format_mph(78.913043478), "78.9")


class TestStepper(unittest.TestCase):
    def test_tap_and_hold_sizes(self):
        self.assertEqual(SPEED_STEP, 1)
        self.assertEqual(SPEED_HOLD, 5)
        self.assertEqual(DIST_STEP, 0.5)
        self.assertEqual(DIST_HOLD, 5.0)

    def test_speed_tap_is_one_and_hold_is_five(self):
        self.assertEqual(bump_speed(60, SPEED_STEP), 61)
        self.assertEqual(bump_speed(60, -SPEED_STEP), 59)
        self.assertEqual(bump_speed(60, SPEED_HOLD), 65)
        self.assertEqual(bump_speed(60, -SPEED_HOLD), 55)
        self.assertEqual(bump_speed(108, SPEED_HOLD), 110)
        self.assertEqual(bump_speed(22, -SPEED_HOLD), 20)

    def test_distance_tap_is_half_a_foot_and_hold_is_five(self):
        self.assertEqual(bump_distance(46, DIST_STEP), 46.5)
        self.assertEqual(bump_distance(46, -DIST_STEP), 45.5)
        self.assertEqual(bump_distance(46, DIST_HOLD), 51.0)
        self.assertEqual(bump_distance(46, -DIST_HOLD), 41.0)
        self.assertEqual(bump_distance(58, DIST_HOLD), 60.5)
        self.assertEqual(bump_distance(18, -DIST_HOLD), 15.0)


class TestEquivalentUsesExistingMath(unittest.TestCase):
    def test_wrapper_matches_utils_and_the_distance_ratio(self):
        speed, release, read_at = 60, 46, 54
        reaction = calculate_reaction_time(speed, release)
        direct = float(calculate_equivalent_speeds(reaction, np.array([read_at]))[0])
        self.assertAlmostEqual(equivalent_mph(speed, release, read_at), direct)
        self.assertAlmostEqual(direct, speed * read_at / release)

    def test_same_release_returns_the_same_speed(self):
        self.assertAlmostEqual(equivalent_mph(80, 54, 54), 80)

    def test_sixty_at_forty_six_reads_the_original_references(self):
        self.assertAlmostEqual(equivalent_mph(60, 46, 20), 60 * 20 / 46)
        self.assertAlmostEqual(equivalent_mph(60, 46, 42), 60 * 42 / 46)
        self.assertAlmostEqual(equivalent_mph(60, 46, 54), 60 * 54 / 46)


if __name__ == "__main__":
    unittest.main()
