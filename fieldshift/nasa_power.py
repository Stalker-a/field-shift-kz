"""Fetch daily point data from NASA POWER (no API key needed).

Docs: https://power.larc.nasa.gov/docs/services/api/
"""
import pandas as pd
import requests

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = {
    "T2M": "Temperature at 2 m, daily mean, °C",
    "T2M_MAX": "Temperature at 2 m, daily maximum, °C",
    "T2M_MIN": "Temperature at 2 m, daily minimum, °C",
    "PRECTOTCORR": "Precipitation (bias-corrected), mm/day",
    "GWETROOT": "Root-zone soil wetness, 0–1",
}
MISSING = -999
START_YEAR, END_YEAR = 1981, 2025


def fetch_daily(lat, lon, start=START_YEAR, end=END_YEAR, timeout=120):
    """Return one row per day: date plus one column per POWER parameter."""
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "latitude": round(lat, 2),
        "longitude": round(lon, 2),
        "start": f"{start}0101",
        "end": f"{end}1231",
        "format": "JSON",
    }
    resp = requests.get(BASE_URL, params=params, timeout=timeout)
    resp.raise_for_status()

    df = pd.DataFrame(resp.json()["properties"]["parameter"])
    df = df.where(df != MISSING)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df.rename_axis("date").reset_index()
