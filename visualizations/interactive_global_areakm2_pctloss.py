import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.wgms_data_loader import *

import plotly.graph_objects as go
import numpy as np

def interactive_global_grid_pctloss():
    import xarray as xr
    import numpy as np
    import plotly.graph_objects as go

    ds = xr.open_dataset(r'.\data\wgms-amce-2026-02-10\global_grid.nc4')
    area = ds['area_km2'].values        # (50, 360, 720)
    lats = ds['lat'].values             # (360,)
    lons = ds['lon'].values             # (720,)
    times = ds['time'].values

    years = [str(t)[:4] for t in times]

    # find cells that have data in at least one timestep
    valid_mask = np.any(~np.isnan(area), axis=0)  # (360, 720)
    lat_idx, lon_idx = np.where(valid_mask)

    cell_lats = lats[lat_idx]
    cell_lons = lons[lon_idx]

    # baseline = first non-NaN value per cell across time
    baseline = np.full(len(lat_idx), np.nan)
    for i, (li, lj) in enumerate(zip(lat_idx, lon_idx)):
        series = area[:, li, lj]
        non_nan = series[~np.isnan(series)]
        if len(non_nan) > 0:
            baseline[i] = non_nan[0]

    def get_pct_loss(t_idx):
        vals = area[t_idx, lat_idx, lon_idx]
        pct = np.where(
            baseline > 0,
            (vals - baseline) / baseline * 100,
            np.nan
        )
        return pct

    # get global min for color scale (worst loss across all time)
    all_pct = np.concatenate([get_pct_loss(t) for t in range(len(years))])
    min_val = np.nanmin(all_pct)

    def make_frame(t_idx):
        pct = get_pct_loss(t_idx)
        valid = ~np.isnan(pct)
        return go.Frame(
            name=years[t_idx],
            data=[go.Scattergeo(
                lat=cell_lats[valid],
                lon=cell_lons[valid],
                mode='markers',
                text=[f"{p:.1f}% change" for p in pct[valid]],
                hoverinfo='text+lon+lat',
                marker=dict(
                    size=4,
                    color=pct[valid],
                    colorscale=[[0,'#4d0000'],[0.5,'#cc3300'],[1,'#fff5f0']],
                    cmin=min_val,
                    cmax=0,
                    colorbar=dict(
                        title=dict(text='% change', side='right'),
                        thickness=12, len=0.6,
                        ticksuffix='%'
                    ),
                    line=dict(width=0),
                    opacity=0.85,
                )
            )]
        )

    frames = [make_frame(t) for t in range(len(years))]
    slider_steps = [
        dict(args=[[y], dict(frame=dict(duration=300, redraw=True), mode='immediate')],
             label=y, method='animate')
        for y in years
    ]
    layout = go.Layout(
        title=dict(
        text='Percentage Change in Glacier Surface Area, 1976-2025',
        font=dict(size=18, family="Source Sans Pro, sans-serif"),
        x=0.5,
        xanchor='center',
    ),
        geo=dict(projection_type='natural earth', showland=True, landcolor='#e8e6df',
                 showocean=True, oceancolor='#e8f0f5', coastlinecolor='#aaa', showframe=False, bgcolor='rgba(0,0,0,0)'),
        margin=dict(t=60, b=80, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        updatemenus=[dict(type='buttons', showactive=False, x=0.05, y=-0.08, xanchor='left',
            buttons=[
                dict(label='▶ Play', method='animate',
                     args=[None, dict(frame=dict(duration=600, redraw=True), fromcurrent=True, mode='immediate')]),
                dict(label='⏸ Pause', method='animate',
                     args=[[None], dict(frame=dict(duration=0), mode='immediate')])
            ])],
        sliders=[dict(active=0, steps=slider_steps, x=0.05, len=0.9, y=-0.05,
                      currentvalue=dict(prefix='Year: ', font=dict(size=14, family="Source Sans Pro, sans-serif"), xanchor='center'),
                      transition=dict(duration=300))]
    )

    return go.Figure(data=frames[0].data, layout=layout, frames=frames)

