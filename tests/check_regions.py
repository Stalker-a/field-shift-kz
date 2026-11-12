"""Smoke check on real NASA POWER data: python tests/check_regions.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fieldshift import climate as cl
from fieldshift.crops import CROPS, SOILS
from fieldshift.nasa_power import fetch_monthly
from fieldshift.regions import REGIONS
from fieldshift.rotation import recommend, rule_issues, score_rotation, suitability

WEIGHTS = {"soil": 3, "water": 3, "profit": 3, "resilience": 3}
CASES = [
    ("Kostanay (north, grain belt)", "chernozem", False),
    ("Turkestan (Shymkent)", "sierozem", True),
    ("Kyzylorda (Aral Sea basin)", "saline", True),
]

for region, soil_key, irrigated in CASES:
    lat, lon = REGIONS[region]
    soil = SOILS[soil_key]
    yearly = cl.yearly_table(fetch_monthly(lat, lon))
    shift = cl.climate_shift(yearly)
    now = cl.profile(shift)
    future = cl.profile(shift, years_ahead=2035 - sum(shift["recent_period"]) / 2)

    print(f"\n=== {region} | {soil.name} | irrigated={irrigated} | years {yearly.year.min()}-{yearly.year.max()}")
    for k in ["season_temp", "season_precip", "season_wetness"]:
        s = shift[k]
        print(f"  {k}: {s['past']:.2f} -> {s['recent']:.2f} (trend {s['trend_per_decade']:+.2f}/decade)")
    top = sorted(CROPS.values(), key=lambda c: -suitability(c, now, soil, irrigated))[:6]
    print("  best crops:", ", ".join(f"{c.key} {suitability(c, now, soil, irrigated):.2f}" for c in top))

    base = score_rotation(("wheat", "wheat", "wheat", "fallow"), now, future, soil, irrigated, WEIGHTS)
    print(f"  baseline total {base.total:.2f}", {k: round(v, 2) for k, v in base.scores.items()})
    for r in recommend(now, future, soil, irrigated, WEIGHTS):
        assert not any(hard for hard, _ in rule_issues(r.rotation)), r.rotation
        print(f"  {' > '.join(r.rotation)}: total {r.total:.2f}", {k: round(v, 2) for k, v in r.scores.items()})
        for line in r.reasons:
            print("     -", line)
print("\nOK")
