"""
Plotting functions for the South Tyrol page.
Functions return Plotly Figure objects and are cached so reruns are fast.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path("data/south_tyrol/processed")

COLORS = {1997: "#5c0f3b", 2005: "#c44341", 2017: "#ffa600"}
YEARS = [1997, 2005, 2017]

MAP_CENTER = {"lat": 46.75, "lon": 11.2}
MAP_ZOOM = 7.6


# ---------------------------------------------------------------------------
# Data loading (cached — runs once per session)
# ---------------------------------------------------------------------------
@st.cache_data
def load_geojson(name: str) -> dict:
    """Load a GeoJSON file and assign feature IDs."""
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        gj = json.load(f)
    for i, feat in enumerate(gj["features"]):
        feat["id"] = str(i)
    return gj


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


@st.cache_data
def load_change_data() -> tuple[dict, pd.DataFrame]:
    """Load the relative change GeoJSON and build hover text."""
    gj = load_geojson("glaciers_change.geojson")
    df = pd.DataFrame([feat["properties"] for feat in gj["features"]])
    df["feature_id"] = df.index.astype(str)
    df["hover"] = df.apply(
        lambda r: (
            f"<b>{r.get('name_d') or r.get('name_it') or 'Unnamed'}</b><br>"
            f"Region: {r['region']}<br>"
            f"Area 1997: {r['area_97']:.3f} km²<br>"
            f"Area 2017: "
            + (f"{r['area_17']:.3f} km²" if pd.notna(r["area_17"]) else "—")
            + f"<br>Change: {r['change_pct']:.1f}%"
        ),
        axis=1,
    )
    return gj, df


@st.cache_data
def load_year_data(year: int) -> tuple[dict, pd.DataFrame]:
    """Load one year's GeoJSON and build hover text."""
    gj = load_geojson(f"glaciers_{year}.geojson")
    df = pd.DataFrame([feat["properties"] for feat in gj["features"]])
    df["feature_id"] = df.index.astype(str)
    df["hover"] = df.apply(
        lambda r, y=year: (
            f"<b>{r.get('NAME_D') or r.get('NAME_IT') or 'Unnamed'}</b><br>"
            f"Region: {r['REGION']}<br>"
            f"Area {y}: {r['area_km2']:.3f} km²"
        ),
        axis=1,
    )
    return gj, df


# ---------------------------------------------------------------------------
# Map: per-layer trace builders (cached individually)
# ---------------------------------------------------------------------------
@st.cache_data
def build_change_trace() -> go.Choroplethmapbox:
    gj, df = load_change_data()
    return go.Choroplethmapbox(
        geojson=gj,
        locations=df["feature_id"],
        z=df["change_pct"],
        colorscale="RdYlBu",
        zmin=-100,
        zmax=0,
        marker_opacity=0.85,
        marker_line_width=0,
        colorbar=dict(title="Change<br>1997→2017 (%)", thickness=12, len=0.6),
        hovertext=df["hover"],
        hoverinfo="text",
        name="Relative change 1997→2017",
        showlegend=False,
    )


@st.cache_data
def build_year_trace(year: int) -> go.Choroplethmapbox:
    gj, df = load_year_data(year)
    return go.Choroplethmapbox(
        geojson=gj,
        locations=df["feature_id"],
        z=[1] * len(df),
        colorscale=[[0, COLORS[year]], [1, COLORS[year]]],
        showscale=False,
        marker_opacity=0.7,
        marker_line_width=0,
        hovertext=df["hover"],
        hoverinfo="text",
        name=f"Glacier extent {year}",
        showlegend=False,
    )


def make_map(show_change: bool, show_1997: bool,
             show_2005: bool, show_2017: bool) -> go.Figure:
    """Assemble the map figure from cached traces based on user toggles."""
    fig = go.Figure()

    if show_change:
        fig.add_trace(build_change_trace())
    for yr, show in [(1997, show_1997), (2005, show_2005), (2017, show_2017)]:
        if show:
            fig.add_trace(build_year_trace(yr))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center=MAP_CENTER,
        mapbox_zoom=MAP_ZOOM,
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        showlegend=False,
    )

    if not any([show_change, show_1997, show_2005, show_2017]):
        fig.add_trace(go.Scattermapbox())  # empty trace to avoid Plotly error

    return fig


# ---------------------------------------------------------------------------
# Aggregate stats (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def make_aggregate_charts() -> tuple[go.Figure, go.Figure, go.Figure]:
    """Return three bar charts: total area, count, average size."""
    agg = load_csv("aggregate_stats.csv")
    agg["year_str"] = agg["year"].astype(str)
    bar_colors = [COLORS[y] for y in agg["year"]]

    def make_bar(values, title, ylabel, fmt):
        fig = go.Figure(
            go.Bar(
                x=agg["year_str"],
                y=values,
                marker_color=bar_colors,
                text=[fmt.format(v) for v in values],
                textposition="outside",
            )
        )
        fig.update_layout(
            title=title,
            yaxis_title=ylabel,
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
            height=340,
        )
        fig.update_xaxes(type="category")
        return fig

    fig_area = make_bar(agg["total_area"], "Total glacier area (km²)", "km²", "{:.1f}")
    fig_count = make_bar(agg["n_parts"], "Number of glacier parts", "Count", "{:.0f}")
    fig_size = make_bar(agg["avg_size"], "Average part size (km²)", "km²", "{:.3f}")

    return fig_area, fig_count, fig_size


# ---------------------------------------------------------------------------
# Regional change chart (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def make_regional_chart() -> go.Figure:
    regional = load_csv("regional_change.csv")
    regional_sorted = regional.sort_values("change_pct_97_17")

    fig = go.Figure(
        go.Bar(
            x=regional_sorted["change_pct_97_17"],
            y=regional_sorted["REGION"],
            orientation="h",
            marker=dict(
                color=regional_sorted["change_pct_97_17"],
                colorscale="Reds_r",
                cmin=-100,
                cmax=0,
                showscale=False,
            ),
            text=[f"{v:.0f}%" for v in regional_sorted["change_pct_97_17"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Area 1997: %{customdata[0]:.1f} km²<br>"
                "Area 2017: %{customdata[1]:.1f} km²<br>"
                "Change: %{x:.1f}%<extra></extra>"
            ),
            customdata=regional_sorted[["area_97", "area_17"]].values,
        )
    )
    fig.update_layout(
        xaxis_title="Area change 1997→2017 (%)",
        margin=dict(l=10, r=40, t=10, b=40),
        height=380,
    )
    fig.update_xaxes(range=[-100, 100])
    fig.add_vline(x=0, line_width=1, line_color="black")

    return fig