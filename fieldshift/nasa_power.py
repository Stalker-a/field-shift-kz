"""Fetch monthly point data from NASA POWER (no API key needed).

Docs: https://power.larc.nasa.gov/docs/services/api/
Responses are cached on disk so the demo still works without internet.
"""
import json
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
PARAMETERS = {
    "T2M": "Temperature at 2 m, °C",
    "PRECTOTCORR": "Precipitation (bias-corrected), mm/day",
    "GWETROOT": "Root-zone soil wetness, 0–1",
}
MISSING = -999
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


def _cache_path(lat, lon, start, end):
    return CACHE_DIR / f"power_{lat:.2f}_{lon:.2f}_{start}_{end}.json"


def fetch_raw(lat, lon, start=1981, end=2024, timeout=60):
    """Return the raw POWER JSON for a point, using the disk cache if present."""
    path = _cache_path(lat, lon, start, end)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "latitude": round(lat, 2),
        "longitude": round(lon, 2),
        "start": start,
        "end": end,
        "format": "JSON",
    }
    resp = requests.get(BASE_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    try:
        CACHE_DIR.mkdir(exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass  # read-only filesystem on a host: the cache is optional
    return data


def to_frame(raw):
    """Turn POWER JSON into a tidy frame: year, month, T2M, PRECTOTCORR, GWETROOT.

    POWER puts the annual value under month "13"; we drop it and compute our own.
    """
    series = raw["properties"]["parameter"]
    rows = {}
    for name, values in series.items():
        for key, value in values.items():
            year, month = int(key[:4]), int(key[4:])
            if month == 13:
                continue
            rows.setdefault((year, month), {})[name] = None if value == MISSING else value

    df = pd.DataFrame(
        [{"year": y, "month": m, **v} for (y, m), v in sorted(rows.items())]
    )
    return df


def fetch_monthly(lat, lon, start=1981, end=2024):
    return to_frame(fetch_raw(lat, lon, start, end))
