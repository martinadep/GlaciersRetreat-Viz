import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.wgms_data_loader import *
import plotly.graph_objects as go
import numpy as np


# WGMS RGI region names (regions 1–19)
REGION_NAMES = {
    1:  'Alaska',
    2:  'Western Canada & US',
    3:  'Arctic Canada North',
    4:  'Arctic Canada South',
    5:  'Greenland',
    6:  'Iceland',
    7:  'Svalbard & Jan Mayen',
    8:  'Scandinavia',
    9:  'Russian Arctic',
    10: 'North Asia',
    11: 'Central Europe',
    12: 'Caucasus & Middle East',
    13: 'Central Asia',
    14: 'South Asia West',
    15: 'South Asia East',
    16: 'Low Latitudes',
    17: 'Southern Andes',
    18: 'New Zealand',
    19: 'Antarctic & Subantarctic',
}

# Distinct color palette — one per region (19 regions)
REGION_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d',
]


def interactive_global_grid_glacier_regions():
    import xarray as xr

    ds = xr.open_dataset(r'.\data\wgms-amce-2026-02-10\global_grid.nc4')

    area   = ds['area_km2'].values   # (time, lat, lon)
    lats   = ds['lat'].values        # (360,)
    lons   = ds['lon'].values        # (720,)

    # ---------- derive region id per cell if available ----------
    # Try loading a 'region' variable from the dataset; fall back to
    # computing from lat/lon using a simple bounding-box lookup.
    if 'region' in ds:
        region_grid = ds['region'].values  # expected shape (lat, lon)
        use_grid_region = True
    else:
        use_grid_region = False

    # Cells that have glacier area in at least one timestep
    valid_mask = np.any(~np.isnan(area), axis=0)   # (lat, lon)
    lat_idx, lon_idx = np.where(valid_mask)
    cell_lats = lats[lat_idx]
    cell_lons = lons[lon_idx]

    # Total area per cell (mean over time, ignoring NaN)
    # mean_area = np.nanmean(area[:, lat_idx, lon_idx], axis=0)

    # Assign region to each cell
    if use_grid_region:
        cell_regions = region_grid[lat_idx, lon_idx].astype(int)
    else:
        cell_regions = assign_rgi_region(cell_lats, cell_lons)

    # ---------- build one trace per region ----------
    traces = []
    region_ids = sorted(REGION_NAMES.keys())

    for i, rid in enumerate(region_ids):
        mask = cell_regions == rid
        if not mask.any():
            continue

        rlats = cell_lats[mask]
        rlons = cell_lons[mask]
        # rareas = mean_area[mask]
        color = REGION_COLORS[i % len(REGION_COLORS)]
        name = REGION_NAMES.get(rid, f'Region {rid}')

        hover = [
            f"<b>{name}</b><br>lat {la:.2f}° lon {lo:.2f}"
            for la, lo in zip(rlats, rlons)
        ]

        traces.append(go.Scattergeo(
            lat=rlats,
            lon=rlons,
            mode='markers',
            name=name,
            text=hover,
            hoverinfo='text',
            marker=dict(
                size=4,
                color=color,
                opacity=0.80,
                line=dict(width=0),
            ),
            legendgroup=str(rid),
            showlegend=True,
        ))

    layout = go.Layout(
        title=dict(
            text='Glacier Locations by RGI Region',
            font=dict(size=18,family="Source Sans Pro, sans-serif"),
            x=0.5,
            xanchor='center',  # ← aggiungi questo
        ),
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#e8e6df',       
            showocean=True,
            oceancolor='#e8f0f5',      
            showlakes=True,
            lakecolor='#a8c8d8',
            showcountries=True,
            countrycolor='#b0a080',
            showcoastlines=True,
            coastlinecolor='#aaa',
            showframe=False,
            bgcolor='rgba(0,0,0,0)',
        ),
        legend=dict(
            title=dict(text='RGI Region', font=dict(size=12, family="Source Sans Pro, sans-serif"),),
            font=dict(size=11, family="Source Sans Pro, sans-serif"),
            itemsizing='constant',
            x=1.01, y=0.5,
            xanchor='left',
            yanchor='middle',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='#ccc',
            borderwidth=1,
        ),
        margin=dict(t=50, b=20, l=0, r=220),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return go.Figure(data=traces, layout=layout)


# ---------------------------------------------------------------
# Simple bounding-box fallback region assignment (RGI-like)
# Used when the NetCDF does not contain a 'region' variable.
# ---------------------------------------------------------------
def assign_rgi_region(lats, lons):
    """
    Assign approximate RGI region IDs based on lat/lon bounding boxes.
    Returns an integer numpy array of the same length as lats/lons.
    """
    regions = np.zeros(len(lats), dtype=int)

    boxes = [
        # (region_id, lat_min, lat_max, lon_min, lon_max)
        (1,  54,  72, -170, -130),   # Alaska
        (2,  40,  60, -140,  -95),   # W Canada & US
        (3,  74,  84,  -95,  -60),   # Arctic Canada N
        (4,  60,  74,  -95,  -60),   # Arctic Canada S
        (5,  60,  85,  -55,   -7),   # Greenland Periphery
        (6,  63,  67,  -25,  -12),   # Iceland
        (7,  74,  81,   10,   35),   # Svalbard
        (8,  57,  72,    4,   32),   # Scandinavia
        (9,  68,  82,   35,   95),   # Russian Arctic
        (10, 46,  68,   80,  180),   # North Asia
        (11, 40,  50,    5,   20),   # Central Europe
        (12, 35,  45,   35,   55),   # Caucasus
        (13, 36,  46,   67,   90),   # Central Asia
        (14, 28,  38,   68,   82),   # S Asia West
        (15, 26,  32,   82,  100),   # S Asia East
        (16,-20,  20, -180,  180),   # Low Latitudes (broad)
        (17,-56, -17,  -76,  -63),   # Southern Andes
        (18,-46, -43,  168,  172),   # New Zealand
        (19,-90, -60, -180,  180),   # Antarctic
    ]

    for rid, lat_min, lat_max, lon_min, lon_max in boxes:
        mask = (
            (lats >= lat_min) & (lats <= lat_max) &
            (lons >= lon_min) & (lons <= lon_max) &
            (regions == 0)   # don't overwrite already-assigned
        )
        regions[mask] = rid

    # Anything unassigned → region 0 → label as 'Unknown'
    return regions


if __name__ == '__main__':
    fig = interactive_global_grid_glacier_regions()
    fig.show()