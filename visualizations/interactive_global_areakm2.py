import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.wgms_data_loader import *

import plotly.graph_objects as go
import numpy as np

df=load_wgms_regions_areakm2()
# se voglio prendere tutti gli anni:
# RAW_DATA = df.pivot(index='year', columns='region', values='gt').to_dict(orient='index')

pivot = df.pivot(index='year', columns='region', values='area_km2')
pivot = pivot.dropna()

RAW_DATA = pivot.to_dict(orient='index')

regions=['ACN','ACS','ALA','ANT',
         'ASC','ASE','ASN','ASW','CAU','CEU',
         'GRL','ISL','NZL','RUA','SA1','SA2',
         'SCA','SJM','TRP','WNA']
regions_decoded=['Northern Arctic Canada','Southern Arctic Canada','Alaska','Antarctic and Subantarctic', 
                     'Central Asia','Eastern Asia','Northern Asia','Western Asia','Caucasus','Central Europe',
                     'Greenland','Iceland','New Zealand','Russian Arctic', 'Southern Andes 1', 'Southern Andes 2',
                     'Scandinavia','Svalbard and Jan Mayen', 'Tropics','Western North America']

coords = {
    'ACN': (78,  -95),  'ACS': (68,  -80),  'ALA': (63, -153),  'ANT': (-72,   0),
    'ASC': (38,   75),  'ASE': (30,   90),  'ASN': (47,   82),  'ASW': (42,   44),
    'CAU': (42,   43),  'CEU': (47,   11),  'GRL': (72,  -40),  'ISL': (65,  -18),
    'NZL': (-44, 170),  'RUA': (75,   65),  'SA1': (-35, -70),  'SA2': (-50, -73),
    'SCA': (62,   14),  'SJM': (78,   20),  'TRP': (-4,  -77),  'WNA': (52, -120),
}

REGIONS = {
    code: {'name': name, 'lat': coords[code][0], 'lon': coords[code][1]}
    for code, name in zip(regions, regions_decoded)
}


years = sorted(RAW_DATA.keys())
codes = list(REGIONS.keys())

all_vals = [abs(v) for year_data in RAW_DATA.values() for v in year_data.values()]
max_val = max(all_vals)
max_size = 60

def make_frame(year):
    data = RAW_DATA[year]
    
    def safe_val(c):
        v = data.get(c, 0)
        return 0 if (v is None or np.isnan(v)) else v

    return go.Frame(
        name=str(year),
        data=[go.Scattergeo(
            lat=[REGIONS[c]['lat'] for c in codes],
            lon=[REGIONS[c]['lon'] for c in codes],
            text=[f"<b>{REGIONS[c]['name']}</b><br>{safe_val(c):.1f} km²" for c in codes],
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=[np.sqrt(abs(safe_val(c)) / max_val) * max_size for c in codes],
                color=[safe_val(c) for c in codes],
                colorscale=[
                    [0,   '#d0e8f5'],
                    [0.5, '#378ADD'],
                    [1,   '#042C53']
                ],
                cmin=-max_val,
                cmax=0,
                colorbar=dict(title=dict(text='km²', side='right'), thickness=12, len=0.6),
                line=dict(width=0.5, color='white'),
                sizemode='diameter'
            )
        )]
    )
frames = [make_frame(y) for y in years]

slider_steps = [
    dict(
        args=[[str(y)], dict(frame=dict(duration=300, redraw=True), mode='immediate')],
        label=str(y),
        method='animate'
    )
    for y in years
]

layout = go.Layout(
    geo=dict(
        projection_type='natural earth',
        showland=True,
        landcolor='#e8e6df',
        showocean=True,
        oceancolor='#d0e8f5',
        showcoastlines=True,
        coastlinecolor='#aaa',
        showframe=False,
        bgcolor='rgba(0,0,0,0)'
    ),
    margin=dict(t=10, b=80, l=0, r=0),
    paper_bgcolor='#f5f4f0',
    plot_bgcolor='#f5f4f0',
    updatemenus=[dict(
        type='buttons',
        showactive=False,
        x=0.05, y=-0.08,
        xanchor='left',
        buttons=[
            dict(
                label='▶ Play',
                method='animate',
                args=[None, dict(frame=dict(duration=600, redraw=True), fromcurrent=True, mode='immediate')]
            ),
            dict(
                label='⏸ Pausa',
                method='animate',
                args=[[None], dict(frame=dict(duration=0), mode='immediate')]
            )
        ]
    )],
    sliders=[dict(
        active=len(years) - 1,
        steps=slider_steps,
        x=0.05, len=0.9,
        y=-0.05,
        currentvalue=dict(prefix='Anno: ', font=dict(size=14), xanchor='center'),
        transition=dict(duration=300)
    )]
)

fig = go.Figure(data=frames[-1].data, layout=layout, frames=frames)
fig.show()