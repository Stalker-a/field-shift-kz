"""Turn daily NASA POWER data into monthly and yearly field indicators and their shift."""
import numpy as np
import pandas as pd

SEASON_MONTHS = range(4, 10)  # April–September: main growing season in Kazakhstan
PAST = (1981, 2000)
RECENT_YEARS = 20
HOT_DAY_C = 30.0       # a daily maximum at or above this counts as a hot day
DRY_DAY_MM = 1.0       # daily rain below this counts as a dry day
MIDSUMMER_DOY = 196    # 15 July splits spring frosts from autumn frosts

INDICATORS = [
    "annual_temp", "annual_precip", "season_temp", "season_precip", "season_wetness",
    "season_et0", "water_deficit", "frost_free_days", "last_frost_doy", "hot_days", "max_dry_spell",
]


def _extraterrestrial_radiation(lat, doy):
    """Radiation at the top of the atmosphere as mm/day of evaporation (FAO-56 eq. 21)."""
    phi = np.radians(lat)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (
        ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws)
    )
    return 0.408 * ra


def _prepare(daily, lat):
    """Add calendar columns and reference evapotranspiration (Hargreaves, FAO-56 eq. 52)."""
    df = daily.copy()
    df["year"] = df.date.dt.year
    df["month"] = df.date.dt.month
    df["doy"] = df.date.dt.dayofyear
    spread = (df.T2M_MAX - df.T2M_MIN).clip(lower=0)
    ra = _extraterrestrial_radiation(lat, df.doy)
    df["et0"] = (0.0023 * (df.T2M + 17.8) * np.sqrt(spread) * ra).clip(lower=0)
    return df


def monthly_table(daily, lat):
    """One row per month: mean temperature and wetness, rain and ET0 totals in mm."""
    df = _prepare(daily, lat)
    return df.groupby(["year", "month"]).agg(
        temp=("T2M", "mean"),
        precip=("PRECTOTCORR", "sum"),
        wetness=("GWETROOT", "mean"),
        et0=("et0", "sum"),
    ).reset_index()


def _longest_run(flags):
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


def _frost_and_drought(df):
    rows = []
    for year, g in df.groupby("year"):
        frost_doys = g.doy[g.T2M_MIN <= 0]
        spring = frost_doys[frost_doys <= MIDSUMMER_DOY]
        autumn = frost_doys[frost_doys > MIDSUMMER_DOY]
        last_spring = int(spring.max()) if len(spring) else 0
        first_autumn = int(autumn.min()) if len(autumn) else len(g) + 1
        season = g[g.month.isin(SEASON_MONTHS)]
        rows.append({
            "year": year,
            "frost_free_days": first_autumn - last_spring - 1,
            "last_frost_doy": last_spring,
            "max_dry_spell": _longest_run(season.PRECTOTCORR < DRY_DAY_MM),
        })
    return pd.DataFrame(rows).set_index("year")


def yearly_table(daily, lat):
    """One row per year with growing-season and annual indicators."""
    df = _prepare(daily, lat)
    season = df[df.month.isin(SEASON_MONTHS)]

    out = pd.DataFrame({
        "annual_temp": df.groupby("year").T2M.mean(),
        "annual_precip": df.groupby("year").PRECTOTCORR.sum(),
        "season_temp": season.groupby("year").T2M.mean(),
        "season_precip": season.groupby("year").PRECTOTCORR.sum(),
        "season_wetness": season.groupby("year").GWETROOT.mean(),
        "season_et0": season.groupby("year").et0.sum(),
        "hot_days": (df.T2M_MAX >= HOT_DAY_C).groupby(df.year).sum(),
    })
    out["water_deficit"] = out.season_et0 - out.season_precip
    out = out.join(_frost_and_drought(df))
    return out[INDICATORS].dropna().reset_index()


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
    for col in INDICATORS:
        shift[col] = {
            "past": float(past_df[col].mean()),
            "recent": float(recent_df[col].mean()),
            "delta": float(recent_df[col].mean() - past_df[col].mean()),
            "trend_per_decade": float(_trend_per_decade(yearly.year, yearly[col])),
        }
    return shift


def monthly_normals(monthly, period):
    """Average month-by-month climate over a (first_year, last_year) period."""
    return monthly[monthly.year.between(*period)].groupby("month")[
        ["temp", "precip", "wetness", "et0"]
    ].mean()


def profile(shift, years_ahead=0):
    """Growing-season climate used for crop scoring.

    years_ahead > 0 extends the recent mean along the linear trend of the whole record.
    This is a simple extrapolation, not a climate model projection.
    """
    k = years_ahead / 10

    def value(col, low, high):
        v = shift[col]["recent"] + k * shift[col]["trend_per_decade"]
        return min(high, max(low, v))

    return {
        "season_temp": value("season_temp", -50.0, 60.0),
        "season_precip": value("season_precip", 0.0, float("inf")),
        "season_wetness": value("season_wetness", 0.0, 1.0),
        "frost_free_days": value("frost_free_days", 0.0, 366.0),
    }
