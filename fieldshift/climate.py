"""Turn monthly NASA POWER data into a growing-season climate profile and its shift."""
import calendar

import numpy as np
import pandas as pd

SEASON_MONTHS = range(4, 10)  # April–September: main growing season in Kazakhstan
PAST = (1981, 2000)
RECENT_YEARS = 20


def yearly_table(monthly):
    """One row per year with growing-season and annual indicators."""
    df = monthly.copy()
    df["days"] = [calendar.monthrange(y, m)[1] for y, m in zip(df.year, df.month)]
    df["precip_mm"] = df.PRECTOTCORR * df.days
    season = df[df.month.isin(SEASON_MONTHS)]

    out = pd.DataFrame({
        "annual_temp": df.groupby("year").T2M.mean(),
        "annual_precip": df.groupby("year").precip_mm.sum(min_count=12),
        "season_temp": season.groupby("year").T2M.mean(),
        "season_precip": season.groupby("year").precip_mm.sum(min_count=6),
        "season_wetness": season.groupby("year").GWETROOT.mean(),
    })
    return out.dropna().reset_index()


def _trend_per_decade(years, values):
    slope = np.polyfit(years, values, 1)[0]
    return slope * 10


def climate_shift(yearly):
    """Compare the 1981–2000 baseline with the most recent 20 years."""
    last = int(yearly.year.max())
    recent = (last - RECENT_YEARS + 1, last)
    past_df = yearly[yearly.year.between(*PAST)]
    recent_df = yearly[yearly.year.between(*recent)]

    shift = {"past_period": PAST, "recent_period": recent}
    for col in ["annual_temp", "annual_precip", "season_temp", "season_precip", "season_wetness"]:
        shift[col] = {
            "past": past_df[col].mean(),
            "recent": recent_df[col].mean(),
            "delta": recent_df[col].mean() - past_df[col].mean(),
            "trend_per_decade": _trend_per_decade(yearly.year, yearly[col]),
        }
    return shift


def profile(shift, years_ahead=0):
    """Growing-season climate used for crop scoring.

    years_ahead > 0 extends the recent mean along the 1981–now linear trend.
    This is a simple extrapolation, not a climate model projection.
    """
    k = years_ahead / 10
    return {
        "season_temp": shift["season_temp"]["recent"] + k * shift["season_temp"]["trend_per_decade"],
        "season_precip": max(0.0, shift["season_precip"]["recent"]
                             + k * shift["season_precip"]["trend_per_decade"]),
        "season_wetness": min(1.0, max(0.0, shift["season_wetness"]["recent"]
                                       + k * shift["season_wetness"]["trend_per_decade"])),
    }
