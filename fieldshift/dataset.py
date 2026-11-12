"""Monthly and yearly climate tables for a point, cached on disk.

The cache keeps the small derived tables, not the raw daily download, so the
preset regions ship with the repo and the demo works without internet.
"""
from pathlib import Path

import pandas as pd

from . import climate as cl
from .nasa_power import END_YEAR, START_YEAR, fetch_daily

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_VERSION = "v2"  # bump when the indicators in climate.py change


def _cache_paths(lat, lon):
    stem = f"{CACHE_VERSION}_{lat:.2f}_{lon:.2f}_{START_YEAR}_{END_YEAR}"
    return CACHE_DIR / f"{stem}_monthly.csv", CACHE_DIR / f"{stem}_yearly.csv"


def load_point(lat, lon):
    """Return (monthly, yearly) tables for a point, downloading them on first use."""
    lat, lon = round(lat, 2), round(lon, 2)
    monthly_path, yearly_path = _cache_paths(lat, lon)
    if monthly_path.exists() and yearly_path.exists():
        return pd.read_csv(monthly_path), pd.read_csv(yearly_path)

    daily = fetch_daily(lat, lon)
    monthly = cl.monthly_table(daily, lat)
    yearly = cl.yearly_table(daily, lat)
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        monthly.to_csv(monthly_path, index=False)
        yearly.to_csv(yearly_path, index=False)
    except OSError:
        pass  # read-only filesystem on a host: the cache is optional
    return monthly, yearly
