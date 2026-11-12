"""Plotly figures for the app, styled for the dark theme in .streamlit/config.toml.

Pass them to st.plotly_chart(fig, theme=None, config=CONFIG) so Streamlit keeps these colors.
"""
import numpy as np
import plotly.graph_objects as go

# Each color has one job across the whole app.
SURFACE = "#1a1a19"
INK, INK_2, MUTED = "#f0efec", "#c3c2b7", "#898781"
GRID, AXIS = "#2c2c2a", "#383835"
ACCENT = "#199e70"         # now / the proposed rotation
ACCENT_LIGHT = "#8fd9bd"   # the 2035 outlook
REFERENCE = "#898781"      # the farmer's current rotation
COOL_WET = "#3987e5"       # cooler or wetter than normal; rain
HOT_DRY = "#e66767"        # hotter or drier than normal
DEMAND = "#d95926"         # evaporative demand
FAMILY_COLORS = {
    "Cereals": "#c98500",
    "Legumes": "#9085e9",
    "Oilseeds, row and other crops": "#d55181",
    "Fallow / green manure": "#898781",
}

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_INITIALS = [m[0] for m in MONTHS]
CONFIG = {"displayModeBar": False}


def _style(fig, title, subtitle, height, top=64):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=INK_2, size=12),
        title=dict(
            text=title, x=0, xanchor="left", y=0.97, yanchor="top", pad=dict(l=4),
            font=dict(color=INK, size=15),
            subtitle=dict(text=subtitle, font=dict(color=MUTED, size=12)),
        ),
        height=height,
        margin=dict(l=8, r=12, t=top, b=8),
        showlegend=False,
        barcornerradius=4,
        hoverlabel=dict(bgcolor="#262624", bordercolor=AXIS, font=dict(color=INK, family=FONT)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def _legend_below_title(fig, height):
    """A horizontal legend on its own row, left-aligned under the subtitle."""
    fig.update_layout(showlegend=True, legend=dict(
        orientation="h", xref="container", x=0, xanchor="left",
        yref="container", y=1 - 60 / height, yanchor="top", font=dict(color=INK_2),
    ))


def _month_axis(fig):
    fig.update_xaxes(tickmode="array", tickvals=MONTHS, ticktext=MONTH_INITIALS, tickangle=0)


def anomaly(yearly, shift, col, title, unit, up_color, down_color, digits=1):
    """Year-by-year difference from the baseline mean, with the linear trend on top."""
    past, recent = shift["past_period"], shift["recent_period"]
    diff = yearly[col] - shift[col]["past"]
    fmt = f".{digits}f"

    fig = go.Figure()
    fig.add_bar(
        x=yearly.year, y=diff, customdata=yearly[col],
        marker=dict(color=np.where(diff >= 0, up_color, down_color), line_width=0),
        hovertemplate=f"<b>%{{x}}</b>: %{{customdata:{fmt}}} {unit} (%{{y:+{fmt}}})<extra></extra>",
    )
    trend = np.polyval(np.polyfit(yearly.year, diff, 1), yearly.year)
    fig.add_scatter(x=yearly.year, y=trend, mode="lines", line=dict(color=INK_2, width=2),
                    hoverinfo="skip")
    fig.add_hline(y=0, line_color=MUTED, line_width=1)

    subtitle = (f"{past[0]}–{past[1]}: {shift[col]['past']:{fmt}} {unit}  →  "
                f"{recent[0]}–{recent[1]}: {shift[col]['recent']:{fmt}} {unit}")
    _style(fig, title, subtitle, height=250)
    fig.update_layout(bargap=0.25)
    fig.update_yaxes(tickformat="~g", ticksuffix=f" {unit}", nticks=5)
    return fig


def monthly_change(past, recent, col, title, unit, up_color, down_color, digits=1):
    """Month-by-month difference between two periods' normals."""
    diff = recent[col] - past[col]
    fmt = f".{digits}f"
    fig = go.Figure()
    fig.add_bar(
        x=MONTHS, y=diff, customdata=np.column_stack([past[col], recent[col]]),
        marker=dict(color=np.where(diff >= 0, up_color, down_color), line_width=0),
        hovertemplate=(f"<b>%{{x}}</b>: %{{customdata[0]:{fmt}}} → %{{customdata[1]:{fmt}}} {unit} "
                       f"(%{{y:+{fmt}}})<extra></extra>"),
    )
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    _style(fig, title, "Change from then to now, by month", height=280)
    fig.update_layout(bargap=0.4)
    fig.update_yaxes(tickformat="~g", ticksuffix=f" {unit}", nticks=5)
    _month_axis(fig)
    return fig


def water_balance(recent, period):
    """Monthly rain against evaporative demand (reference evapotranspiration)."""
    fig = go.Figure()
    fig.add_bar(x=MONTHS, y=recent.precip, name="Rain", marker=dict(color=COOL_WET, line_width=0),
                hovertemplate="Rain: %{y:.0f} mm<extra></extra>")
    fig.add_scatter(x=MONTHS, y=recent.et0, name="Evaporative demand", mode="lines+markers",
                    line=dict(color=DEMAND, width=2),
                    marker=dict(size=8, color=DEMAND, line=dict(color=SURFACE, width=2)),
                    hovertemplate="Demand: %{y:.0f} mm<extra></extra>")
    _style(fig, "Rain vs evaporative demand", f"Average month, {period[0]}–{period[1]}", height=280, top=96)
    fig.update_layout(bargap=0.4, hovermode="x unified")
    fig.update_yaxes(ticksuffix=" mm", nticks=5, rangemode="tozero")
    _legend_below_title(fig, 280)
    _month_axis(fig)
    return fig


def suitability_dumbbell(rows, future_year):
    """Crop suitability now and in the future. rows: (name, now, future), best first."""
    names = [r[0] for r in rows][::-1]
    now = [r[1] for r in rows][::-1]
    future = [r[2] for r in rows][::-1]

    xs, ys = [], []
    for name, a, b in zip(names, now, future):
        xs += [a, b, None]
        ys += [name, name, None]

    fig = go.Figure()
    fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=AXIS, width=3),
                    hoverinfo="skip", showlegend=False)
    ring = dict(color=SURFACE, width=2)
    fig.add_scatter(x=future, y=names, mode="markers", name=str(future_year),
                    marker=dict(size=13, color=ACCENT_LIGHT, line=ring),
                    hovertemplate=f"%{{y}} in {future_year}: %{{x:.0%}}<extra></extra>")
    fig.add_scatter(x=now, y=names, mode="markers", name="Now",
                    marker=dict(size=13, color=ACCENT, line=ring),
                    hovertemplate="%{y} now: %{x:.0%}<extra></extra>")
    height = 110 + 27 * len(rows)
    _style(fig, "How well each crop fits your field", "100% = no climate or soil limit",
           height=height, top=96)
    _legend_below_title(fig, height)
    fig.update_layout(legend_traceorder="reversed")
    fig.update_xaxes(range=[-0.03, 1.03], tickformat=".0%", showgrid=True, gridcolor=GRID,
                     side="bottom", showline=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(color=INK_2))
    return fig


def score_bars(scores, labels, color, reference=None):
    """Scores of one rotation, with optional tick marks for the rotation it is compared with."""
    keys = list(labels)[::-1]
    names = [labels[k] for k in keys]
    values = [scores[k] for k in keys]

    fig = go.Figure()
    fig.add_bar(
        x=values, y=names, orientation="h", width=0.5,
        marker=dict(color=color, line_width=0),
        hovertemplate="%{y}: %{x:.0%}<extra></extra>",
    )
    # values sit in their own column so a reference tick never covers them
    fig.add_scatter(x=[1.0] * len(names), y=names, mode="text", text=[f"  {v:.0%}" for v in values],
                    textposition="middle right", textfont=dict(color=INK_2, size=12),
                    hoverinfo="skip", cliponaxis=False)
    if reference is not None:
        fig.add_scatter(
            x=[reference[k] for k in keys], y=names, mode="markers",
            marker=dict(symbol="line-ns", size=20, line=dict(color=INK, width=2)),
            hovertemplate="Current rotation: %{x:.0%}<extra></extra>",
        )
    _style(fig, None, None, height=150, top=4)
    fig.update_layout(margin=dict(l=4, r=4, b=4))
    fig.update_xaxes(range=[0, 1.22], visible=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(color=INK_2), ticksuffix="  ")
    return fig


def region_map(regions, lat, lon):
    """Preset regions on an outline of Kazakhstan, with the selected field highlighted."""
    fig = go.Figure()
    fig.add_scattergeo(
        lat=[p[0] for p in regions.values()], lon=[p[1] for p in regions.values()],
        text=list(regions), mode="markers", marker=dict(size=6, color=MUTED),
        hovertemplate="%{text}<extra></extra>",
    )
    fig.add_scattergeo(lat=[lat], lon=[lon], mode="markers",
                       marker=dict(size=13, color=ACCENT, line=dict(color="#0d0d0d", width=2)),
                       hovertemplate=f"Your field: {lat:.2f}°N, {lon:.2f}°E<extra></extra>")
    fig.update_geos(
        resolution=50, projection_type="mercator", lonaxis_range=[45, 89], lataxis_range=[39.5, 56.5],
        showland=True, landcolor=SURFACE, showcountries=True, countrycolor=MUTED,
        showcoastlines=False, showlakes=True, lakecolor="#0d0d0d", showocean=True, oceancolor="#0d0d0d",
        showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=150, showlegend=False, dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="#262624", bordercolor=AXIS, font=dict(color=INK, family=FONT)),
    )
    return fig
