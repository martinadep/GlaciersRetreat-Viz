import plotly.express as px
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.wgms_data_loader import  *

def interactive_global_mmsle():
    df= load_wgms_global_mmsle()


    fig = px.bar(
        df,
        x='year',
        y='mmsle',
        title='Millimeter sea level equivalent, 1976-2025',
        labels={'mmsle': 'Change in global mean sea level, mm', 'year': 'Years'},
        color='mmsle',
        color_continuous_scale=[
            (0.0, '#d6e9f8'),   # chiaro → valori bassi/negativi
            (1.0, '#08306b'),   # scuro  → valori alti

        ],
        range_color=[df['mmsle'].min(), df['mmsle'].max()]  # ancora la scala ai dati reali
    )

    fig.update_layout(
        coloraxis_showscale=False,
        hovermode='x unified'
    )


    return go.Figure(fig)  # <-- return invece di write_html

