"""Offline UI regressions: python tests/check_ui.py.

Browser testing is still required for Leaflet clicks and responsive layout.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit.testing.v1 import AppTest

from fieldshift import climate as cl
from fieldshift.crops import SOILS
from fieldshift.dataset import load_point
from fieldshift.regions import REGIONS
from fieldshift.rotation import score_rotation
from ui_helpers import field_summary, map_point

ROOT = Path(__file__).resolve().parent.parent
DEMO = next(iter(REGIONS))
DEMO_TABLES = load_point(*REGIONS[DEMO])


def button(app, label):
    return next(item for item in app.button if item.label == label)


class MapInputTests(unittest.TestCase):
    def test_invalid_component_values_are_rejected(self):
        for point in [None, [], {}, {"lat": 52}, {"lat": "bad", "lng": 70},
                      {"lat": float("nan"), "lng": 70}, {"lat": 50, "lng": float("inf")},
                      {"lat": 39.999, "lng": 60}, {"lat": 50, "lng": 88.001}]:
            with self.subTest(point=point):
                self.assertIsNone(map_point(point))
        self.assertEqual(map_point({"lat": 40, "lng": 46}), (40, 46))
        self.assertEqual(map_point({"lat": 56, "lng": 88}), (56, 88))
        self.assertEqual(map_point({"lat": 50.1234, "lng": 68.3456}), (50.12, 68.35))


class InterfaceTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)

    def assert_healthy(self, app):
        self.assertFalse(app.exception, [item.message for item in app.exception])
        self.assertFalse(app.error, [item.value for item in app.error])

    def test_rotation_navigation_survives_settings_change(self):
        app = self.app().run()
        self.assert_healthy(app)
        button(app, "Compare rotations").click().run()
        self.assertEqual(app.query_params["tab"], "rotation")
        app.radio[0].set_value("Save water").run()
        self.assert_healthy(app)
        self.assertIn("Rotation plan", app.session_state["active_view"])
        self.assertEqual(app.query_params["tab"], "rotation")

    def test_map_preview_does_not_change_field_until_applied(self):
        with patch("fieldshift.dataset.load_point", return_value=DEMO_TABLES) as loader:
            app = self.app().run()
            app.selectbox[1].set_value("saline")
            app.toggle[0].set_value(True).run()
            with patch("streamlit_folium.st_folium", return_value={
                "last_clicked": {"lat": 50.1234, "lng": 68.3456}
            }):
                before = loader.call_count
                button(app, "Choose on map").click().run()
                self.assert_healthy(app)
                self.assertEqual(app.session_state["field_region"], DEMO)
                self.assertEqual(loader.call_count, before)
                button(app, "Use selected point").click().run()
                self.assert_healthy(app)
                self.assertEqual(app.session_state["field_region"], "Custom coordinates")
                self.assertEqual(app.session_state["chosen_point"], (50.12, 68.35))
                self.assertEqual(tuple(item.value for item in app.number_input), (50.12, 68.35))
                self.assertEqual(app.selectbox[1].value, "saline")
                self.assertTrue(app.toggle[0].value)

    def test_manual_coordinates_apply_together(self):
        with patch("fieldshift.dataset.load_point", return_value=DEMO_TABLES) as loader:
            app = self.app().run()
            app.selectbox(key="field_region").set_value("Custom coordinates").run()
            before = loader.call_count
            app.number_input(key="custom_lat").set_value(50.76)
            app.number_input(key="custom_lon").set_value(68.98)
            self.assertEqual(app.session_state["chosen_point"], REGIONS[DEMO])
            self.assertEqual(loader.call_count, before)
            button(app, "Apply coordinates").click().run()
            self.assert_healthy(app)
            self.assertEqual(app.session_state["chosen_point"], (50.76, 68.98))

    def test_outside_map_point_cannot_be_applied(self):
        app = self.app().run()
        with patch("streamlit_folium.st_folium", return_value={
            "last_clicked": {"lat": 30, "lng": 70}
        }):
            button(app, "Choose on map").click().run()
            self.assertTrue(button(app, "Use selected point").disabled)
            self.assertEqual(app.session_state["field_region"], DEMO)
            self.assertTrue(app.warning)

    def test_custom_data_failure_has_working_demo_recovery(self):
        point = (50.99, 68.99)

        def point_data(lat, lon):
            if (lat, lon) == point:
                raise ConnectionError("Test: NASA unavailable")
            return DEMO_TABLES

        with patch("fieldshift.dataset.load_point", side_effect=point_data):
            app = self.app()
            app.session_state["field_region"] = "Custom coordinates"
            app.session_state["chosen_point"] = point
            app.run()
            self.assertFalse(app.exception)
            self.assertIn("couldn't load", app.error[0].value)
            button(app, "Use Kostanay demo").click().run()
            self.assert_healthy(app)
            self.assertEqual(app.session_state["field_region"], DEMO)

    def test_summary_retains_scenario_and_handles_no_options(self):
        shift = cl.climate_shift(DEMO_TABLES[1])
        now = cl.profile(shift)
        labels = {"soil": "Soil health", "water": "Water saving", "profit": "Income",
                  "resilience": "Resilience 2035"}
        weights = dict.fromkeys(labels, 3)
        baseline = score_rotation(("wheat", "wheat", "wheat", "fallow"),
                                  now, now, SOILS["saline"], True, weights)
        report = field_summary("Example", 50.12, 68.35, SOILS["saline"], True,
                               "Balanced", weights, shift, baseline, [], 2035, labels)
        for required in ["50.12°N, 68.35°E", "Saline soil", "Irrigated: yes",
                         "Wheat → Wheat → Wheat → Green fallow", "No rotation passed",
                         "Income is not money", "not a climate model projection"]:
            self.assertIn(required, report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
