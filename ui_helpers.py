"""Map selection and readable exports for the Streamlit interface."""
from math import isfinite

import folium

from fieldshift.crops import CROPS

LAT_RANGE = (40.0, 56.0)
LON_RANGE = (46.0, 88.0)


def map_point(clicked):
    """Validate component input before it becomes a NASA point or widget value."""
    if not isinstance(clicked, dict):
        return None
    try:
        lat, lon = float(clicked["lat"]), float(clicked["lng"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if not (isfinite(lat) and isfinite(lon)):
        return None
    if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LON_RANGE[0] <= lon <= LON_RANGE[1]):
        return None
    return round(lat, 2), round(lon, 2)


def field_map(regions, lat, lon):
    """Map clicks are a preview; the app applies them only after confirmation."""
    view = folium.Map(location=[lat, lon], zoom_start=5, min_zoom=3, max_zoom=16,
                      tiles="OpenStreetMap", control_scale=True)
    bounds = [[LAT_RANGE[0], LON_RANGE[0]], [LAT_RANGE[1], LON_RANGE[1]]]
    folium.Rectangle(bounds, color="#8fd9bd", weight=1, dash_array="5 7", fill=False,
                     interactive=False).add_to(view)
    for name, point in regions.items():
        folium.CircleMarker(point, radius=5, color="#c3c2b7", weight=1,
                            fill=True, fill_opacity=0.9, tooltip=name).add_to(view)
    folium.CircleMarker([lat, lon], radius=9, color="#8fd9bd", weight=3,
                        fill=True, fill_color="#199e70", fill_opacity=1,
                        tooltip="Current field").add_to(view)
    folium.LatLngPopup().add_to(view)
    return view


def field_summary(place, lat, lon, soil, irrigated, priority, weights, shift,
                  baseline, options, future_year, criteria_labels):
    """Export the actual scenario, including the baseline and score limitations."""
    def rotation_text(rotation):
        return " → ".join(CROPS[key].name for key in rotation)

    def scores_text(scores):
        return "; ".join(f"{label}: {scores[key]:.0%}" for key, label in criteria_labels.items())

    past, recent = shift["past_period"], shift["recent_period"]
    lines = [
        "# Field Shift KZ — field summary", "",
        f"Field: {place}", f"Coordinates: {lat:.2f}°N, {lon:.2f}°E",
        f"Soil: {soil.name}", f"Irrigated: {'yes' if irrigated else 'no'}",
        f"Priority: {priority}",
        "Weights: " + "; ".join(f"{criteria_labels[key]}: {weight}" for key, weight in weights.items()),
        f"Reference period: {past[0]}–{past[1]}; recent period: {recent[0]}–{recent[1]}",
        "Season: April–September", "", "## Climate shift", "",
    ]
    for key, label, unit in [
        ("season_temp", "Season temperature", "°C"),
        ("season_precip", "Season rainfall", "mm"),
        ("frost_free_days", "Frost-free season", "days"),
    ]:
        item = shift[key]
        lines.append(f"- {label}: {item['past']:.1f} → {item['recent']:.1f} {unit}")
    lines += ["", "## Current rotation", "", rotation_text(baseline.rotation),
              f"Overall score: {baseline.total:.0%}", scores_text(baseline.scores)]
    if baseline.issues:
        lines += [f"- {message}" for _, message in baseline.issues]
    for number, result in enumerate(options, 1):
        lines += ["", f"## Option {number}", "", rotation_text(result.rotation),
                  f"Overall score: {result.total:.0%} "
                  f"({(result.total - baseline.total) * 100:+.0f} points vs current)",
                  scores_text(result.scores)]
        lines += [f"- {reason}" for reason in result.reasons]
        lines += [f"- Caution: {message}" for _, message in result.issues]
    if not options:
        lines += ["", "No rotation passed the model's agronomy rules for this scenario."]
    lines += ["", "## Data and interpretation", "",
              "NASA POWER daily point data: https://power.larc.nasa.gov/",
              "Grid-cell estimates describe the surrounding area, not field measurements.",
              "Crop and soil parameters are approximate prototype assumptions.",
              "Rice water fit includes ETc, soil preparation, percolation and a water layer. "
              "The continuous-flooding scenario is not a measured Kazakhstan irrigation norm; "
              "see https://github.com/Stalker-a/field-shift-kz/blob/main/SOURCES.md.",
              "All scores are relative model indicators; Income is not money or a profit forecast.",
              f"The {future_year} outlook extends the observed trend; it is not a climate model projection.",
              "Review options with a local agronomist before changing a rotation.", ""]
    return "\n".join(lines)
