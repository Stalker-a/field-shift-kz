"""Field Shift KZ — Streamlit app. Run: streamlit run app.py"""
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from fieldshift import charts
from fieldshift import climate as cl
from fieldshift.crops import CROPS, FAMILY_GROUPS, IRRIGATION_MM, SOILS
from fieldshift.dataset import load_point
from fieldshift.nasa_power import PARAMETERS
from fieldshift.regions import REGIONS
from fieldshift.rotation import CRITERIA, fit_breakdown, recommend, score_rotation, suitability

FUTURE_YEAR = 2035
CUSTOM = "Custom coordinates"
CRITERIA_LABELS = {"soil": "Soil health", "water": "Water saving", "profit": "Income",
                   "resilience": f"Resilience {FUTURE_YEAR}"}
PRESETS = {  # weights in CRITERIA order
    "Balanced": (3, 3, 3, 3),
    "Protect the soil": (5, 2, 2, 3),
    "Save water": (2, 5, 2, 3),
    "Maximise income": (2, 2, 5, 2),
    "Climate-proof": (2, 3, 2, 5),
}
FIT_LABELS = {"temperature": "Temperature", "water": "Water", "season": "Season length",
              "salinity": "Soil salinity"}
TABS = {"climate": ":material/thermostat: Climate shift", "crops": ":material/grass: Crop fit",
        "rotation": ":material/autorenew: Rotation plan", "method": ":material/database: Data & method"}

st.set_page_config(page_title="Field Shift KZ", page_icon="🌾", layout="wide")


@st.cache_data(show_spinner="Loading NASA POWER data…")
def load_climate(lat, lon):
    monthly, yearly = load_point(lat, lon)
    return monthly, yearly, cl.climate_shift(yearly)


@st.cache_data(show_spinner="Searching for the best rotations…")
def best_rotations(now, future, soil_key, irrigated, weights):
    return recommend(dict(now), dict(future), SOILS[soil_key], irrigated, dict(weights),
                     future_year=FUTURE_YEAR)


def doy_label(doy):
    return (date(2001, 1, 1) + timedelta(days=round(doy) - 1)).strftime("%d %b").lstrip("0")


def chart(fig):
    st.plotly_chart(fig, theme=None, config=charts.CONFIG)


SWATCHES = {  # legend key shapes, matching the mark they stand for
    "bar": "width:10px;height:10px;border-radius:2px",
    "dot": "width:10px;height:10px;border-radius:50%",
    "line": "width:16px;height:2px",
    "tick": "width:2px;height:14px",
}


def legend_html(items):
    """Swatch + label pairs; the text stays in ink, the swatch carries the color."""
    parts = [
        f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:18px">'
        f'<span style="{SWATCHES[shape]};background:{color}"></span>{label}</span>'
        for color, label, shape in items
    ]
    return f'<div style="font-size:13px;color:{charts.INK_2};line-height:2">{"".join(parts)}</div>'


def chips_html(rotation):
    """A rotation as one chip per year; the dot color shows the crop family."""
    chips = []
    for i, key in enumerate(rotation):
        color = charts.FAMILY_COLORS[FAMILY_GROUPS[CROPS[key].family]]
        chips.append(
            f'<div style="background:{charts.GRID};border-radius:8px;padding:6px 10px;min-width:112px">'
            f'<div style="font-size:11px;color:{charts.MUTED}">Year {i + 1}</div>'
            f'<div style="display:flex;align-items:center;gap:6px;font-size:14px;color:{charts.INK}">'
            f'<span style="flex:none;width:9px;height:9px;border-radius:50%;background:{color}"></span>'
            f'{CROPS[key].name}</div></div>'
        )
    return f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px">{"".join(chips)}</div>'


def shift_phrases(shift):
    t, p = shift["season_temp"], shift["season_precip"]
    rain_pct = p["delta"] / p["past"]
    if abs(t["delta"]) < 0.15:
        temp = "about as warm"
    else:
        temp = f"{abs(t['delta']):.1f} °C {'warmer' if t['delta'] > 0 else 'cooler'}"
    if abs(rain_pct) < 0.03:
        rain = "gets about the same rain"
    else:
        rain = f"gets {abs(rain_pct):.0%} {'more' if rain_pct > 0 else 'less'} rain"
    return temp, rain


# ---------- sidebar: inputs ----------
with st.sidebar:
    st.subheader("1 · Your field")
    region = st.selectbox("Region", [*REGIONS, CUSTOM],
                          help="Pick the farming region closest to your field, or enter coordinates.")
    if region == CUSTOM:
        c_lat, c_lon = st.columns(2)
        lat = c_lat.number_input("Latitude, °N", 40.0, 56.0, 51.0, 0.01)
        lon = c_lon.number_input("Longitude, °E", 46.0, 88.0, 71.0, 0.01)
        place = f"Your field at {lat:.2f}°N, {lon:.2f}°E"
    else:
        lat, lon = REGIONS[region]
        place = region.split(" (")[0]
    chart(charts.region_map(REGIONS, lat, lon))

    soil_key = st.selectbox("Soil type", list(SOILS), format_func=lambda k: SOILS[k].name)
    soil = SOILS[soil_key]
    st.caption(soil.note)
    irrigated = st.toggle("Field is irrigated",
                          help=f"Adds about {IRRIGATION_MM} mm of water per season and allows cotton and rice.")

    st.subheader("2 · Your priority")
    preset = st.radio("What matters most to you?", list(PRESETS))
    with st.expander("Fine-tune the weights"):
        weights = {k: st.slider(CRITERIA_LABELS[k], 0, 5, PRESETS[preset][i], key=f"weight_{preset}_{k}")
                   for i, k in enumerate(CRITERIA)}

    st.subheader("3 · What you grow now")
    st.caption("Your rotation over four years. We compare every suggestion with it.")
    crop_keys = list(CROPS)
    year_cols = st.columns(2)
    current = tuple(
        year_cols[i % 2].selectbox(f"Year {i + 1}", crop_keys, index=crop_keys.index(default),
                                   format_func=lambda k: CROPS[k].name, key=f"current_{i}")
        for i, default in enumerate(["wheat", "wheat", "wheat", "fallow"])
    )

# ---------- data and model ----------
st.title("🌾 Field Shift KZ")
st.caption("See how your field's climate has changed since 1981 and which crop rotation fits it today. "
           "Built on NASA Earth observations.")

try:
    monthly, yearly, shift = load_climate(lat, lon)
except Exception as exc:  # network problems should not crash the demo
    st.error(f"Could not load NASA POWER data: {exc}")
    st.stop()

past, recent = shift["past_period"], shift["recent_period"]
then_label, now_label = f"{past[0]}–{past[1]}", f"{recent[0]}–{recent[1]}"
now = cl.profile(shift)
future = cl.profile(shift, years_ahead=FUTURE_YEAR - sum(recent) / 2)
baseline = score_rotation(current, now, future, soil, irrigated, weights)
best = best_rotations(tuple(now.items()), tuple(future.items()), soil_key, irrigated,
                      tuple(weights.items()))

# ---------- headline ----------
with st.container(border=True):
    left, right = st.columns([3, 2], gap="large")
    with left:
        temp_phrase, rain_phrase = shift_phrases(shift)
        st.caption(f"CLIMATE SHIFT · {then_label} → {now_label}")
        st.markdown(f"#### {place}: the growing season is {temp_phrase} and {rain_phrase}")
        t, p = shift["season_temp"], shift["season_precip"]
        st.caption(f"April–September average: {t['past']:.1f} → {t['recent']:.1f} °C, "
                   f"{p['past']:.0f} → {p['recent']:.0f} mm of rain.")
    with right:
        st.caption(f"BEST ROTATION FOR “{preset.upper()}”")
        if best:
            st.html(chips_html(best[0].rotation))
            st.markdown(f"Overall score **{best[0].total:.0%}**, against **{baseline.total:.0%}** "
                        "for what you grow now.")
        else:
            st.markdown("No rotation passes the agronomy rules for this field.")

requested = st.query_params.get("tab")
tab_climate, tab_crops, tab_rotation, tab_method = st.tabs(
    list(TABS.values()), default=TABS[requested] if requested in TABS else None)

# ---------- 1. climate shift ----------
with tab_climate:
    st.subheader("Your field now, compared with a generation ago")
    st.caption(f"Each tile shows the {now_label} average and its change from {then_label}. "
               "“Season” means April–September.")

    def s(col):
        return shift[col]["recent"], shift[col]["delta"]

    wet, wet_d = s("season_wetness")
    frost, frost_d = s("last_frost_doy")
    tiles = [
        ("Season temperature", f"{s('season_temp')[0]:.1f} °C", f"{s('season_temp')[1]:+.1f} °C", "off",
         "Average air temperature over the growing season."),
        ("Season rainfall", f"{s('season_precip')[0]:.0f} mm",
         f"{s('season_precip')[1] / shift['season_precip']['past']:+.0%}", "normal",
         "Total rain from April to September."),
        ("Root-zone soil wetness", f"{wet:.0%}", f"{wet_d * 100:+.1f} pts", "normal",
         "How full of water the soil is where roots grow: 0% is bone dry, 100% is saturated."),
        ("Water deficit", f"{s('water_deficit')[0]:.0f} mm", f"{s('water_deficit')[1]:+.0f} mm", "inverse",
         "Evaporative demand minus rain over the season. The larger it is, the more crops depend "
         "on stored soil moisture or irrigation."),
        ("Frost-free season", f"{s('frost_free_days')[0]:.0f} days", f"{s('frost_free_days')[1]:+.0f} days",
         "off", "Days between the last spring frost and the first autumn frost."),
        ("Last spring frost", doy_label(frost), f"{frost_d:+.0f} days", "off",
         "Average date of the last night below 0 °C in spring. A negative change means it comes earlier."),
        ("Hot days per year", f"{s('hot_days')[0]:.0f}", f"{s('hot_days')[1]:+.0f} days", "inverse",
         f"Days when the temperature reaches {cl.HOT_DAY_C:.0f} °C or more. Heat at flowering cuts grain yield."),
        ("Longest dry spell", f"{s('max_dry_spell')[0]:.0f} days", f"{s('max_dry_spell')[1]:+.0f} days",
         "inverse", f"Longest run of season days with less than {cl.DRY_DAY_MM:.0f} mm of rain."),
    ]
    for row in (tiles[:4], tiles[4:]):
        for col, (label, value, delta, delta_color, tip) in zip(st.columns(4), row):
            col.metric(label, value, delta, delta_color=delta_color, help=tip, border=True)

    st.subheader(f"Year by year, against the {then_label} normal")
    st.html(legend_html([
        (charts.HOT_DRY, "Hotter or drier than normal", "bar"),
        (charts.COOL_WET, "Cooler or wetter than normal", "bar"),
        (charts.INK_2, "Trend", "line"),
    ]))
    warm, cool = charts.HOT_DRY, charts.COOL_WET
    anomaly_specs = [
        ("season_temp", "Season temperature", "°C", warm, cool, 1),
        ("season_precip", "Season rainfall", "mm", cool, warm, 0),
        ("water_deficit", "Water deficit (demand minus rain)", "mm", warm, cool, 0),
        ("season_wetness", "Root-zone soil wetness (0–1)", "", cool, warm, 2),
        ("frost_free_days", "Frost-free season", "days", warm, cool, 0),
        ("hot_days", f"Hot days ({cl.HOT_DAY_C:.0f} °C or more)", "days", warm, cool, 0),
    ]
    for i in range(0, len(anomaly_specs), 2):
        for col, spec in zip(st.columns(2), anomaly_specs[i:i + 2]):
            with col:
                chart(charts.anomaly(yearly, shift, *spec))

    st.subheader("Month by month")
    then_normals = cl.monthly_normals(monthly, past)
    now_normals = cl.monthly_normals(monthly, recent)
    m1, m2, m3 = st.columns(3)
    with m1:
        chart(charts.monthly_change(then_normals, now_normals, "temp", "Which months warmed", "°C", warm, cool))
    with m2:
        chart(charts.monthly_change(then_normals, now_normals, "precip", "Which months got wetter or drier",
                                    "mm", cool, warm, digits=0))
    with m3:
        chart(charts.water_balance(now_normals, recent))
    st.caption("When evaporative demand is above rain, crops live on stored soil moisture or irrigation.")

    with st.expander("Show the yearly data as a table"):
        st.dataframe(yearly.round(2), hide_index=True)
        st.download_button("Download CSV", yearly.to_csv(index=False), "fieldshift_yearly.csv", "text/csv")

# ---------- 2. crop fit ----------
with tab_crops:
    fits = []
    for crop in CROPS.values():
        if crop.family == "fallow":
            continue
        parts = fit_breakdown(crop, now, soil, irrigated)
        if crop.irrigated_only and not irrigated:
            limit = "Needs irrigation"
        elif min(parts.values()) >= 0.999:
            limit = "Nothing"
        else:
            limit = FIT_LABELS[min(parts, key=parts.get)]
        fits.append({
            "crop": crop.name,
            "now": suitability(crop, now, soil, irrigated),
            "future": suitability(crop, future, soil, irrigated),
            "limit": limit, **parts,
        })
    fits.sort(key=lambda f: (f["now"], f["future"]), reverse=True)

    st.subheader(f"Which crops fit your field now and in {FUTURE_YEAR}")
    st.caption(f"{FUTURE_YEAR} extends today's climate along the {past[0]}–{recent[1]} trend. "
               "It is a simple extrapolation, not a climate model.")
    left, right = st.columns([3, 2], gap="large")
    with left:
        chart(charts.suitability_dumbbell([(f["crop"], f["now"], f["future"]) for f in fits], FUTURE_YEAR))
    with right:
        gaining = [f for f in fits if f["future"] - f["now"] >= 0.03]
        losing = [f for f in fits if f["now"] - f["future"] >= 0.03]
        with st.container(border=True):
            st.markdown("**Best fit today**")
            st.markdown("\n".join(f"- {f['crop']} · {f['now']:.0%}" for f in fits[:5]))
        with st.container(border=True):
            st.markdown(f"**Gaining ground by {FUTURE_YEAR}**")
            st.markdown("\n".join(f"- {f['crop']} · {f['now']:.0%} → {f['future']:.0%}" for f in gaining[:5])
                        or "No crop changes by 3 points or more.")
        with st.container(border=True):
            st.markdown(f"**Losing ground by {FUTURE_YEAR}**")
            st.markdown("\n".join(f"- {f['crop']} · {f['now']:.0%} → {f['future']:.0%}" for f in losing[:5])
                        or "No crop changes by 3 points or more.")

    st.subheader("What holds each crop back")
    st.caption("Each factor scores from 0 to 100%. A crop's fit is the product of its factors.")
    factors = [k for k in FIT_LABELS if k != "salinity" or soil.saline]
    table = pd.DataFrame(fits)[["crop", "now", "limit", *factors]]
    table[["now", *factors]] *= 100
    bar = dict(min_value=0, max_value=100, format="%.0f%%", width="small")
    st.dataframe(
        table, hide_index=True, height=35 * (len(table) + 1) + 3,
        column_config={
            "crop": "Crop",
            "now": st.column_config.ProgressColumn("Fit today", **bar),
            "limit": "Held back most by",
            **{k: st.column_config.ProgressColumn(FIT_LABELS[k], **bar) for k in factors},
        },
    )

# ---------- 3. rotation plan ----------
with tab_rotation:
    st.subheader("Your rotation and three better-fitting options")
    st.html(legend_html([(color, name, "dot") for name, color in charts.FAMILY_COLORS.items()]))

    with st.container(border=True):
        left, right = st.columns([3, 2], gap="large")
        with left:
            st.markdown("**What you grow now**")
            st.html(chips_html(baseline.rotation))
            for _, text in baseline.issues:
                st.markdown(f":material/warning: {text}")
        with right:
            st.metric("Overall score", f"{baseline.total:.0%}")
            chart(charts.score_bars(baseline.scores, CRITERIA_LABELS, charts.REFERENCE))

    if not best:
        st.warning("No rotation passes the agronomy rules for this field. "
                   "Try turning irrigation on or choosing another soil type.")
    else:
        st.html(legend_html([
            (charts.ACCENT, "This option", "bar"),
            (charts.INK, "Your current rotation", "tick"),
        ]))
        for col, (i, res) in zip(st.columns(len(best)), enumerate(best)):
            with col, st.container(border=True):
                st.markdown(f"**Option {i + 1}**" + (" · best match" if i == 0 else ""))
                st.html(chips_html(res.rotation))
                st.metric("Overall score", f"{res.total:.0%}",
                          f"{(res.total - baseline.total) * 100:+.0f} pts vs now")
                chart(charts.score_bars(res.scores, CRITERIA_LABELS, charts.ACCENT, baseline.scores))
                st.markdown("**Why it works**")
                st.markdown("\n".join(f"- {text}" for text in res.reasons))
                for _, text in res.issues:
                    st.markdown(f":material/warning: {text}")

        with st.expander("Show all scores as a table"):
            rows = [{"Rotation": "Current", "Crops": " → ".join(CROPS[k].name for k in baseline.rotation),
                     "Overall": baseline.total, **{CRITERIA_LABELS[k]: baseline.scores[k] for k in CRITERIA}}]
            rows += [{"Rotation": f"Option {i + 1}", "Crops": " → ".join(CROPS[k].name for k in r.rotation),
                      "Overall": r.total, **{CRITERIA_LABELS[k]: r.scores[k] for k in CRITERIA}}
                     for i, r in enumerate(best)]
            percent = st.column_config.NumberColumn(format="percent")
            st.dataframe(pd.DataFrame(rows), hide_index=True,
                         column_config={name: percent for name in ["Overall", *CRITERIA_LABELS.values()]})

# ---------- 4. data and method ----------
with tab_method:
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Data")
        st.markdown(
            "**NASA POWER** daily point data, community AG "
            f"([power.larc.nasa.gov](https://power.larc.nasa.gov)), {past[0]}–{recent[1]}, "
            f"at {lat:.2f}°N, {lon:.2f}°E:"
        )
        st.markdown("\n".join(f"- `{code}`: {text}" for code, text in PARAMETERS.items()))
        st.markdown(
            "From these we compute, for every year:\n"
            "- growing-season temperature, rainfall and root-zone soil wetness;\n"
            "- evaporative demand (reference evapotranspiration, Hargreaves method, FAO-56) "
            "and the water deficit, demand minus rain;\n"
            "- the frost-free season and the date of the last spring frost;\n"
            f"- hot days ({cl.HOT_DAY_C:.0f} °C or more) and the longest dry spell."
        )
        st.download_button("Download monthly data (CSV)", monthly.to_csv(index=False),
                           "fieldshift_monthly.csv", "text/csv")
    with right:
        st.subheader("How the scores work")
        st.markdown(
            "- **Crop fit** multiplies four factors: season temperature, water available "
            "(rain + stored soil moisture + irrigation) against the crop's need, frost-free days "
            "against the crop's season, and salt tolerance on saline soil.\n"
            "- **Rotations** are every four-year sequence of the best-fitting crops that passes basic "
            "agronomy rules: no crop straight after itself, no two legumes or two oilseeds in a row.\n"
            "- **Soil health** rewards legumes, crop diversity and soil-building crops, and penalises "
            "cereal after cereal.\n"
            "- **Water saving** rewards crops whose need fits the water available.\n"
            "- **Income** combines relative crop value, crop fit, soil fertility and the benefit of "
            "following a legume or fallow.\n"
            f"- **Resilience {FUTURE_YEAR}** is the crop fit under the trend climate of {FUTURE_YEAR}.\n"
            "- The **overall score** is the average of the four, weighted by your priorities."
        )
        st.subheader("Limits")
        st.markdown(
            "- NASA POWER describes a grid cell of about 50 km, not a single field.\n"
            "- Crop and soil parameters are approximate. Use the results to explore options, "
            "and talk to a local agronomist before changing your rotation.\n"
            f"- The {FUTURE_YEAR} outlook extends the observed trend. It is not a climate model projection."
        )

    with st.expander("Show the crop parameters used"):
        st.dataframe(pd.DataFrame([vars(c) for c in CROPS.values()]).drop(columns="key"), hide_index=True)
