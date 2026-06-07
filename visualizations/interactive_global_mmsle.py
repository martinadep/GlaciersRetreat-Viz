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
            (0.0, '#fff5f0'),   
            (1.0, '#cc3300'),   

        ],
        range_color=[df['mmsle'].min(), df['mmsle'].max()]  
    )

    fig.update_layout(
        font=dict(size=18,family="Source Sans Pro, sans-serif"),
        coloraxis_showscale=False,
        hovermode='x unified',
        title_x=0.5,
        title_xanchor='center',
    )


    return go.Figure(fig)  

