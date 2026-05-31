import plotly.express as px



import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.data_loader import  *

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

fig.show()


# bruttino:
# import altair as alt


# chart = alt.Chart(df).mark_bar().encode(
#     x=alt.X('year:O', title='Years'),
#     y=alt.Y('mmsle:Q', title='Change in global mean sea level, mm'),
#     color=alt.condition(
#         alt.datum.mmsle > 0,
#         alt.value('steelblue'),
#         alt.value('lightblue')
#     ),
#     tooltip=['year', 'mmsle']

# ).properties(
#     title='Millimeter sea level equivalent, 1976-2025'
# )

# chart.save('chart.html')
# import webbrowser
# webbrowser.open('chart.html')