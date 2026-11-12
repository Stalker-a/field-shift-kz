"""Field Shift KZ — Streamlit app. Run: streamlit run app.py"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fieldshift import climate as cl
from fieldshift.crops import CROPS, SOILS
from fieldshift.nasa_power import fetch_monthly
from fieldshift.regions import REGIONS
from fieldshift.rotation import CRITERIA, recommend, score_rotation, suitability

END_YEAR = 2024
FUTURE_YEAR = 2035
CRITERIA_LABELS = {
    "soil": "Soil health",
    "water": "Water saving",
    "profit": "Income",
    "resilience": f"Climate resilience ({FUTURE_YEAR})",
}

st.set_page_config(page_title="Field Shift KZ", page_icon="🌾", layout="wide")


@st.cache_data(show_spinner="Loading NASA POWER data…")
def load_climate(lat, lon):
    yearly = cl.yearly_table(fetch_monthly(lat, lon, end=END_YEAR))
    return yearly, cl.climate_shift(yearly)


def rotation_label(rot):
    return " → ".join(CROPS[k].name for k in rot)


def trend_line(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    return slope * x + intercept


# ---------- sidebar: inputs ----------
with st.sidebar:
    st.header("1. Your field")
    region = st.selectbox("Region", [*REGIONS, "Custom coordinates"])
    if region == "Custom coordinates":
        lat = st.number_input("Latitude", 40.0, 56.0, 51.0, 0.01)
        lon = st.number_input("Longitude", 46.0, 88.0, 71.0, 0.01)
    else:
        lat, lon = REGIONS[region]
    soil = SOILS[st.selectbox("Soil type", list(SOILS), format_func=lambda k: SOILS[k].name)]
    irrigated = st.toggle("Field is irrigated")

    st.header("2. What matters to you")
    weights = {k: st.slider(CRITERIA_LABELS[k], 0, 5, 3) for k in CRITERIA}

    st.header("3. What you grow now")
    crop_keys = list(CROPS)
    current = tuple(
        st.selectbox(f"Year {i + 1}", crop_keys, index=crop_keys.index(default),
                     format_func=lambda k: CROPS[k].name, key=f"current_{i}")
        for i, default in enumerate(["wheat", "wheat", "wheat", "fallow"])
    )

# ---------- data ----------
st.title("🌾 Field Shift KZ")
st.caption("Crop rotation decision support for Kazakhstan farms, built on NASA Earth observations.")

try:
    yearly, shift = load_climate(lat, lon)
except Exception as exc:  # network problems should not crash the demo
    st.error(f"Could not load NASA POWER data: {exc}")
    st.stop()

past, recent = shift["past_period"], shift["recent_period"]
years_ahead = FUTURE_YEAR - sum(recent) / 2
now = cl.profile(shift)
future = cl.profile(shift, years_ahead=years_ahead)

# ---------- 1. climate shift ----------
st.header("1. How your field's climate has shifted")
st.caption(f"{past[0]}–{past[1]} compared with {recent[0]}–{recent[1]}, growing season April–September.")

t, p, w, a = shift["season_temp"], shift["season_precip"], shift["season_wetness"], shift["annual_temp"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Season temperature", f"{t['recent']:.1f} °C", f"{t['delta']:+.1f} °C")
c2.metric("Season rainfall", f"{p['recent']:.0f} mm", f"{p['delta'] / p['past']:+.0%}")
c3.metric("Root-zone soil wetness", f"{w['recent']:.2f}", f"{w['delta']:+.2f}")
c4.metric("Annual temperature", f"{a['recent']:.1f} °C", f"{a['delta']:+.1f} °C")

col_map, col_chart = st.columns([1, 2])
with col_map:
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=4)
with col_chart:
    fig = go.Figure()
    fig.add_bar(x=yearly.year, y=yearly.season_precip, name="Season rainfall, mm",
                marker_color="rgba(70,130,180,0.45)", yaxis="y2")
    fig.add_scatter(x=yearly.year, y=yearly.season_temp, name="Season temperature, °C",
                    mode="lines+markers", line_color="#d9534f")
    fig.add_scatter(x=yearly.year, y=trend_line(yearly.year, yearly.season_temp),
                    name="Temperature trend", mode="lines", line=dict(dash="dash", color="#d9534f"))
    fig.update_layout(
        height=330, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="°C"), yaxis2=dict(title="mm", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(fig, width="stretch")

# ---------- 2. crop suitability ----------
st.header(f"2. Which crops fit your field now and in {FUTURE_YEAR}")
st.caption(f"{FUTURE_YEAR} = recent climate extended along the {past[0]}–{END_YEAR} trend "
           "(a simple extrapolation, not a climate model).")
suit = pd.DataFrame([
    {"crop": c.name,
     "Now": suitability(c, now, soil, irrigated),
     str(FUTURE_YEAR): suitability(c, future, soil, irrigated)}
    for c in CROPS.values() if c.family != "fallow"
]).sort_values("Now", ascending=False)
fig = go.Figure()
fig.add_bar(x=suit.crop, y=suit.Now, name="Now", marker_color="#5cb85c")
fig.add_bar(x=suit.crop, y=suit[str(FUTURE_YEAR)], name=str(FUTURE_YEAR), marker_color="#f0ad4e")
fig.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=10, b=10),
                  yaxis=dict(title="Suitability", tickformat=".0%", range=[0, 1]))
st.plotly_chart(fig, width="stretch")

# ---------- 3. rotations ----------
st.header("3. Recommended rotations")
baseline = score_rotation(current, now, future, soil, irrigated, weights)
best = recommend(now, future, soil, irrigated, weights, future_year=FUTURE_YEAR)

if not best:
    st.warning("No rotation passes the agronomy rules for this field. Try irrigation or another soil type.")
    st.stop()

compare = go.Figure()
for name, res in [("Your current rotation", baseline)] + [(f"Option {i + 1}", r) for i, r in enumerate(best)]:
    compare.add_bar(x=[CRITERIA_LABELS[k] for k in CRITERIA], y=[res.scores[k] for k in CRITERIA], name=name)
compare.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=10, b=10),
                      yaxis=dict(tickformat=".0%", range=[0, 1]), legend=dict(orientation="h", y=-0.2))
st.plotly_chart(compare, width="stretch")

cols = st.columns(len(best) + 1)
with cols[0]:
    st.subheader("Your current rotation")
    st.markdown(f"**{rotation_label(baseline.rotation)}**")
    st.metric("Overall score", f"{baseline.total:.0%}")
    for _, text in baseline.issues:
        st.markdown(f"⚠️ {text}")
for col, (i, res) in zip(cols[1:], enumerate(best)):
    with col:
        st.subheader(f"Option {i + 1}")
        st.markdown(f"**{rotation_label(res.rotation)}**")
        st.metric("Overall score", f"{res.total:.0%}", f"{res.total - baseline.total:+.0%} vs current")
        for text in res.reasons:
            st.markdown(f"- {text}")
        for _, text in res.issues:
            st.markdown(f"⚠️ {text}")

st.divider()
st.caption(
    "Data: NASA POWER (power.larc.nasa.gov), monthly T2M, PRECTOTCORR and GWETROOT, community AG. "
    "Crop parameters are approximate and for exploration only — talk to a local agronomist before changing your rotation."
)
