import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
DATA_DIR = Path("data/south_tyrol/processed")

COLORS = {1997: "#5c0f3b", 2005: "#c44341", 2017: "#ffa600"}
YEARS = [1997, 2005, 2017]

# Map centred roughly on South Tyrol's glacierized area
MAP_CENTER = {"lat": 46.75, "lon": 11.2}
MAP_ZOOM = 7.6


# ---------------------------------------------------------------------------
# Data loading (cached so reruns are instant)
# ---------------------------------------------------------------------------
@st.cache_data
def load_geojson(name: str) -> dict:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def geojson_to_df(gj: dict) -> pd.DataFrame:
    """Extract feature properties into a DataFrame, keyed by feature index."""
    rows = [feat["properties"] for feat in gj["features"]]
    df = pd.DataFrame(rows)
    df["feature_id"] = df.index.astype(str)
    return df


# Load everything
gj_change = load_geojson("glaciers_change.geojson")
df_change = geojson_to_df(gj_change)

# Build hover text for the change layer (once, since data is static)
df_change["hover"] = df_change.apply(
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

# Ensure GeoJSON features have a stable id for Plotly's choropleth matching
for i, feat in enumerate(gj_change["features"]):
    feat["id"] = str(i)

gj_years = {}
df_years = {}
for yr in YEARS:
    gj = load_geojson(f"glaciers_{yr}.geojson")
    for i, feat in enumerate(gj["features"]):
        feat["id"] = str(i)
    gj_years[yr] = gj
    df_years[yr] = geojson_to_df(gj)

agg_stats = load_csv("aggregate_stats.csv")
regional = load_csv("regional_change.csv")


# ---------------------------------------------------------------------------
# Page content
# ---------------------------------------------------------------------------
st.title("South Tyrol")

# Intro text block — leave empty for now
st.write("")


# ---------------------------------------------------------------------------
# 1. Interactive map
# ---------------------------------------------------------------------------
st.subheader("Glacier change, 1997–2017")

# User controls — checkboxes for which layers to show
st.markdown("**Show layers:**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    show_change = st.checkbox("Relative change 1997→2017", value=True)
with c2:
    show_1997 = st.checkbox("Glacier extent 1997", value=False)
with c3:
    show_2005 = st.checkbox("Glacier extent 2005", value=False)
with c4:
    show_2017 = st.checkbox("Glacier extent 2017", value=False)

fig_map = go.Figure()

# Layer 1: relative change
if show_change:
    fig_map.add_trace(
        go.Choroplethmapbox(
            geojson=gj_change,
            locations=df_change["feature_id"],
            z=df_change["change_pct"],
            colorscale="RdYlBu",
            zmin=-100,
            zmax=0,
            marker_opacity=0.85,
            marker_line_width=0,
            colorbar=dict(title="Change<br>1997→2017 (%)", thickness=12, len=0.6),
            hovertext=df_change["hover"],
            hoverinfo="text",
            name="Relative change 1997→2017",
            showlegend=False,
        )
    )

# Layers 2–4: per-year extents
year_toggles = {1997: show_1997, 2005: show_2005, 2017: show_2017}
for yr in YEARS:
    if not year_toggles[yr]:
        continue
    df = df_years[yr]
    df["hover"] = df.apply(
        lambda r: (
            f"<b>{r.get('NAME_D') or r.get('NAME_IT') or 'Unnamed'}</b><br>"
            f"Region: {r['REGION']}<br>"
            f"Area {yr}: {r['area_km2']:.3f} km²"
        ),
        axis=1,
    )
    fig_map.add_trace(
        go.Choroplethmapbox(
            geojson=gj_years[yr],
            locations=df["feature_id"],
            z=[1] * len(df),
            colorscale=[[0, COLORS[yr]], [1, COLORS[yr]]],
            showscale=False,
            marker_opacity=0.7,
            marker_line_width=0,
            hovertext=df["hover"],
            hoverinfo="text",
            name=f"Glacier extent {yr}",
            showlegend=False,
        )
    )

fig_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_center=MAP_CENTER,
    mapbox_zoom=MAP_ZOOM,
    margin=dict(l=0, r=0, t=0, b=0),
    height=600,
    showlegend=False,
)

# Handle the case where all checkboxes are off — show empty map
if not any([show_change, show_1997, show_2005, show_2017]):
    fig_map.add_trace(go.Scattermapbox())

st.plotly_chart(fig_map, use_container_width=True)
st.write("")


# ---------------------------------------------------------------------------
# 2. Aggregate stats — area, count, average size
# ---------------------------------------------------------------------------
st.subheader("Total area, fragment count, average size")

agg_stats["year_str"] = agg_stats["year"].astype(str)
bar_colors = [COLORS[y] for y in agg_stats["year"]]

col1, col2, col3 = st.columns(3)

with col1:
    fig = go.Figure(
        go.Bar(
            x=agg_stats["year_str"],
            y=agg_stats["total_area"],
            marker_color=bar_colors,
            text=[f"{v:.1f}" for v in agg_stats["total_area"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Total glacier area (km²)",
        yaxis_title="km²",
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure(
        go.Bar(
            x=agg_stats["year_str"],
            y=agg_stats["n_parts"],
            marker_color=bar_colors,
            text=agg_stats["n_parts"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Number of glacier parts",
        yaxis_title="Count",
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = go.Figure(
        go.Bar(
            x=agg_stats["year_str"],
            y=agg_stats["avg_size"],
            marker_color=bar_colors,
            text=[f"{v:.3f}" for v in agg_stats["avg_size"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Average part size (km²)",
        yaxis_title="km²",
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        height=340,
    )
    st.plotly_chart(fig, use_container_width=True)

st.write("")


# ---------------------------------------------------------------------------
# 3. Relative change by mountain group
# ---------------------------------------------------------------------------
st.subheader("Relative area change by mountain group")

regional_sorted = regional.sort_values("change_pct_97_17")

fig_reg = go.Figure(
    go.Bar(
        x=regional_sorted["change_pct_97_17"],
        y=regional_sorted["REGION"],
        orientation="h",
        marker_color="#c44341",
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
fig_reg.update_layout(
    xaxis_title="Area change 1997→2017 (%)",
    margin=dict(l=10, r=40, t=10, b=40),
    height=380,
)
st.plotly_chart(fig_reg, use_container_width=True)

st.write("")