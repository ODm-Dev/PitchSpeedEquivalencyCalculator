"""Characterization tests for the pitch-equivalency math.

These lock the behavior of utils.py. The conversion factor is
1 mph = 1.467 ft/s. Equivalent speed is the speed that keeps the
same time-to-plate at a different distance.
"""

import unittest

import numpy as np

from utils import (
    calculate_equivalent_speeds,
    calculate_reaction_time,
    generate_distance_range,
    validate_inputs,
)

MPH_TO_FT_PER_SEC = 1.467


class TestCalculateReactionTime(unittest.TestCase):
    def test_uses_one_point_four_six_seven_feet_per_second(self):
        speed_mph = 60
        distance_ft = 46
        expected = distance_ft / (speed_mph * MPH_TO_FT_PER_SEC)
        self.assertAlmostEqual(
            calculate_reaction_time(speed_mph, distance_ft), expected
        )

    def test_doubles_when_distance_doubles(self):
        slower_look = calculate_reaction_time(90, 30.25)
        full = calculate_reaction_time(90, 60.5)
        self.assertAlmostEqual(full, slower_look * 2)

    def test_halves_when_speed_doubles(self):
        slower = calculate_reaction_time(40, 46)
        faster = calculate_reaction_time(80, 46)
        self.assertAlmostEqual(slower, faster * 2)

    def test_known_sixty_mph_at_forty_six_feet(self):
        # 60 * 1.467 = 88.02 ft/s; 46 / 88.02 = 0.522608498...
        self.assertAlmostEqual(calculate_reaction_time(60, 46), 46 / 88.02)


class TestCalculateEquivalentSpeeds(unittest.TestCase):
    def test_round_trip_returns_original_speed(self):
        speed = 73
        distance = 50
        reaction = calculate_reaction_time(speed, distance)
        equivalent = calculate_equivalent_speeds(reaction, np.array([distance]))
        self.assertAlmostEqual(float(equivalent[0]), speed)

    def test_scales_with_the_distance_ratio(self):
        speed = 65
        reaction = calculate_reaction_time(speed, 46)
        equivalents = calculate_equivalent_speeds(
            reaction, np.array([40, 50, 54, 60.5])
        )
        self.assertAlmostEqual(float(equivalents[0]), speed * 40 / 46)
        self.assertAlmostEqual(float(equivalents[1]), speed * 50 / 46)
        self.assertAlmostEqual(float(equivalents[2]), speed * 54 / 46)
        self.assertAlmostEqual(float(equivalents[3]), speed * 60.5 / 46)

    def test_sixty_at_forty_six_matches_full_distance(self):
        """60 mph from 46 ft is the same reaction time as ~78.913 mph from 60.5 ft."""
        reaction = calculate_reaction_time(60, 46)
        equivalent = calculate_equivalent_speeds(reaction, np.array([60.5]))
        self.assertAlmostEqual(float(equivalent[0]), 60 * 60.5 / 46)
        self.assertAlmostEqual(float(equivalent[0]), 78.91304347826087)

    def test_accepts_the_generated_distance_range(self):
        reaction = calculate_reaction_time(55, 46)
        distances = generate_distance_range()
        equivalents = calculate_equivalent_speeds(reaction, distances)
        self.assertEqual(len(equivalents), len(distances))
        self.assertAlmostEqual(float(equivalents[0]), 55 * float(distances[0]) / 46)
        self.assertAlmostEqual(float(equivalents[-1]), 55 * float(distances[-1]) / 46)


class TestGenerateDistanceRange(unittest.TestCase):
    def test_runs_from_15_to_60_5_by_half_feet(self):
        distances = generate_distance_range()
        self.assertAlmostEqual(float(distances[0]), 15.0)
        self.assertAlmostEqual(float(distances[-1]), 60.5)
        self.assertAlmostEqual(float(distances[1] - distances[0]), 0.5)
        self.assertEqual(len(distances), 92)


class TestValidateInputs(unittest.TestCase):
    def test_accepts_in_range_values(self):
        self.assertEqual(validate_inputs(60, 46), [])
        self.assertEqual(validate_inputs(20, 15), [])
        self.assertEqual(validate_inputs(110, 60.5), [])
        self.assertEqual(validate_inputs(1, 15.0), [])

    def test_rejects_non_positive_speed(self):
        self.assertIn("Speed must be a positive number", validate_inputs(0, 46))
        self.assertIn("Speed must be a positive number", validate_inputs(-5, 46))
        self.assertIn("Speed must be a positive number", validate_inputs("60", 46))

    def test_rejects_distance_outside_15_to_60_5(self):
        self.assertIn(
            "Distance must be between 15 and 60.5 feet",
            validate_inputs(60, 14.9),
        )
        self.assertIn(
            "Distance must be between 15 and 60.5 feet",
            validate_inputs(60, 60.6),
        )
        self.assertIn(
            "Distance must be between 15 and 60.5 feet",
            validate_inputs(60, "46"),
        )


if __name__ == "__main__":
    unittest.main()
