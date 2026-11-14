"""Paddy balance regressions: python tests/check_rice_water.py."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fieldshift import climate as cl
from fieldshift.crops import CROPS, SOILS
from fieldshift.dataset import load_point
from fieldshift.regions import REGIONS
from fieldshift.rotation import (
    available_water, explain, fit_breakdown, score_rotation, suitability, water_fit,
)

RICE = CROPS["rice"]
WEIGHTS = dict.fromkeys(("soil", "water", "profit", "resilience"), 3)


class PaddyBalanceTests(unittest.TestCase):
    def setUp(self):
        self.soil = SOILS["sierozem"]
        self.climate = dict(season_temp=25, season_precip=600,
                            season_wetness=0.5, frost_free_days=200)

    def test_etc_does_not_replace_full_paddy_demand(self):
        self.assertEqual(RICE.water_need, 700)
        self.assertEqual(RICE.field_water_need, 1720)
        self.assertAlmostEqual(water_fit(RICE, 700), 700 / 1720)
        self.assertEqual(water_fit(RICE, 1720), 1)
        self.assertEqual(water_fit(RICE, 2000), 1)

    def test_percolation_rate_and_flooding_duration_have_distinct_units(self):
        self.assertEqual(replace(RICE, percolation_mm_day=4).field_water_need, 1480)
        self.assertEqual(replace(RICE, percolation_mm_day=8).field_water_need, 1960)
        self.assertEqual(replace(RICE, flooded_days=110).field_water_need, 1660)
        # A changed harvest cycle must not silently change the assumed water regime.
        self.assertEqual(replace(RICE, season_days=140).field_water_need, 1720)

    def test_rain_soil_and_irrigation_are_each_credited_once(self):
        # 600 rain + 80*0.5 soil credit + 450 field irrigation = 1090 mm.
        self.assertEqual(available_water(self.climate, self.soil, True), 1090)
        self.assertAlmostEqual(suitability(RICE, self.climate, self.soil, True), 1090 / 1720)
        self.assertAlmostEqual(fit_breakdown(RICE, self.climate, self.soil, True)["water"],
                               1090 / 1720)
        wetter = dict(self.climate, season_wetness=1)
        delta = (suitability(RICE, wetter, self.soil, True)
                 - suitability(RICE, self.climate, self.soil, True))
        self.assertAlmostEqual(delta, 40 / 1720)  # no second soil credit against SAT
        self.assertEqual(suitability(RICE, self.climate, self.soil, False), 0)

    def test_fallow_credit_is_not_also_deducted_from_saturation(self):
        self.assertAlmostEqual(suitability(RICE, self.climate, self.soil, True, 32),
                               (1090 + 32) / 1720)

    def test_rotation_water_profit_and_resilience_use_full_demand(self):
        result = score_rotation(("rice", "fallow"), self.climate, self.climate,
                                self.soil, True, WEIGHTS)
        rice_fit = (1090 + 32) / 1720  # previous fallow adds 0.4 * 80 mm
        self.assertAlmostEqual(result.scores["water"], (0.6 * rice_fit + 1) / 2)
        self.assertAlmostEqual(result.scores["profit"],
                               (0.7 * rice_fit * 0.76 * 1.15) / 2 / 0.75)
        self.assertAlmostEqual(result.scores["resilience"], 1090 / 1720)

    def test_explanation_warns_when_etc_is_met_but_paddy_demand_is_not(self):
        result = score_rotation(("rice", "fallow"), self.climate, self.climate,
                                self.soil, True, WEIGHTS)
        reasons = explain(result, self.climate, 2035, self.soil, True)
        self.assertTrue(any("Water risk: Rice" in reason for reason in reasons), reasons)
        self.assertTrue(any("1720 mm" in reason for reason in reasons), reasons)

    def test_other_crops_keep_their_existing_water_response(self):
        for key, crop in CROPS.items():
            if key == "rice":
                continue
            with self.subTest(crop=key):
                self.assertEqual(crop.field_water_need, crop.water_need)
                expected = ((min(1, 300 / crop.water_need) ** (1 - 0.7 * crop.drought_tol))
                            if crop.water_need else 1)
                self.assertAlmostEqual(water_fit(crop, 300), expected)

    def test_cached_regional_suitability_uses_full_paddy_demand(self):
        for region, soil_key, salt_factor in [
            ("Kyzylorda (Aral Sea basin)", "saline", 0.76),
            ("Turkestan (Shymkent)", "sierozem", 1),
        ]:
            with self.subTest(region=region):
                _, yearly = load_point(*REGIONS[region])
                now = cl.profile(cl.climate_shift(yearly))
                soil = SOILS[soil_key]
                expected = available_water(now, soil, True) / 1720 * salt_factor
                self.assertAlmostEqual(suitability(RICE, now, soil, True), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
