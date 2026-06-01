import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

TICK_SIZE = 18
TITLE_SIZE = 24
LEGEND_SIZE = 16

@st.cache_data
def load_data():
    df_raw = pd.read_csv("data/italy_glaciers.csv")
    df_raw.order_by = df_raw['ID Code']

    df_italy = df_raw[['Glacier Name', 'ID Code',
                    'Mountain Sector', 'Mountain Group', 'Region', 
                    'Glacier Type', 'Aspect',
                    'Area CGI (km2)','Area WGI (km2)',
                    'Area (km2)','Year', 'Newly Formed']]
    df_italy['Area CGI (km2)'] = pd.to_numeric(df_italy['Area CGI (km2)'], errors='coerce').map("{:.2f}".format)
    df_italy['Area WGI (km2)'] = pd.to_numeric(df_italy['Area WGI (km2)'], errors='coerce').map("{:.2f}".format)
    df_italy['Area (km2)'] = pd.to_numeric(df_italy['Area (km2)'], errors='coerce').map("{:.2f}".format)
    return df_italy


@st.cache_data
def bar_sector_counts(df, region=None):
    if region is not None:
        df = df[df["Region"] == region]
    
    counts = df['Mountain Sector'].value_counts().sort_values(ascending=True) 
    new_counts = df.groupby('Mountain Sector')['Newly Formed'].sum().reindex(counts.index, fill_value=0)

    plot_df = pd.DataFrame({
        'Mountain Sector': counts.index,
        'Total Glaciers': counts.values,
        'Newly Formed Glaciers': new_counts.values
    })

    fig = px.bar(plot_df, x='Total Glaciers', y='Mountain Sector', 
        orientation='h', title='Glacier Count by Mountain Sector',
        labels={'Total Glaciers': 'Number of Glaciers', 'Mountain Sector': ''},
        color_discrete_sequence=['#1f77b4'])
    
    # legend and hover template
    fig.data[0].name = 'Total Glaciers'
    fig.data[0].showlegend = True
    fig.data[0].hovertemplate = '%{x}' 

    # new glaciers bars
    fig.add_trace(go.Bar( x=plot_df['Newly Formed Glaciers'], y=plot_df['Mountain Sector'],
                            orientation='h', name='Newly Formed Glaciers',
                            marker_color='lightblue', opacity=0.7, hovertemplate='%{x}'))

    fig.update_layout(
        barmode='overlay', 
        legend_title_text='', # remove title from legend
        hovermode='y unified', # unify hover on the y-axis
        legend=dict( yanchor="bottom", y=0.1, xanchor="right", x=1)
    )

    fig.update_layout(
        # height=400,
        # width=400,
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        xaxis=dict(
            tickfont=dict(size=TICK_SIZE),        
            title=dict(font=dict(size=TICK_SIZE)) 
        ),
        yaxis=dict(
            tickfont=dict(size=TICK_SIZE)
        )
    )
    

    return fig

@st.cache_data
def compass_aspect(df, region=None):
    # 1. Filtro per regione
    if region is not None:
        df = df[df["Region"] == region]
        
    target_df = df.copy()

    # 2. Pulizia dati e conversione numerica per la sicurezza dei calcoli
    target_df['Area (km2)'] = pd.to_numeric(target_df['Area (km2)'], errors='coerce')
    
    valid_aspect = target_df['Aspect'].notna() & (target_df['Aspect'].str.strip() != "") & (target_df['Aspect'] != "SW / W")
    order = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    aspect_num_cleaned = target_df.loc[valid_aspect, 'Aspect'].value_counts().reindex(order, fill_value=0)
    aspect_area_cleaned = target_df.loc[valid_aspect].groupby('Aspect')['Area (km2)'].sum().reindex(order, fill_value=0)

    # 3. Calcolo Percentuali
    pct_num = (aspect_num_cleaned / aspect_num_cleaned.sum() * 100) if aspect_num_cleaned.sum() > 0 else aspect_num_cleaned
    pct_area = (aspect_area_cleaned / aspect_area_cleaned.sum() * 100) if aspect_area_cleaned.sum() > 0 else aspect_area_cleaned

    # Per chiudere la linea del radar in Plotly, appendiamo il primo elemento alla fine
    order_closed = order + [order[0]]
    values_num_closed = list(pct_num.values) + [pct_num.values[0]]
    values_area_closed = list(pct_area.values) + [pct_area.values[0]]

    # 4. Calcolo del massimo dinamico per la scala del grigliato (minimo 40%)
    max_val = max(max(values_num_closed), max(values_area_closed))
    ymax = max(40, np.ceil(max_val / 10) * 10)

    # 5. Costruzione del Grafico Radar
    fig = go.Figure()

    # Traccia 1: Number of Glaciers (%)
    fig.add_trace(go.Scatterpolar(
        r=values_num_closed,
        theta=order_closed,
        fill='toself',
        fillcolor='rgba(181, 66, 46, 0.12)', # #b5422e con alpha
        line=dict(color='#b5422e', width=2),
        name='Number of Glaciers (%)',
        hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
    ))

    # Traccia 2: Glaciers Area (%)
    fig.add_trace(go.Scatterpolar(
        r=values_area_closed,
        theta=order_closed,
        fill='toself',
        fillcolor='rgba(7, 88, 125, 0.12)', # #07587d con alpha
        line=dict(color='#07587d', width=2),
        name='Glaciers Area (%)',
        hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
    ))

    # 6. Configurazione del Layout e dello stile Octagonale
    fig.update_layout(
        title=dict(
            text='Glacier Aspect Distribution (%)',
            font=dict(size=TITLE_SIZE)
        ),
        font=dict(size=TICK_SIZE), # Font di base grande come richiesto prima
        hovermode='closest',
        # height=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=LEGEND_SIZE)
        ),
        polar=dict(
            gridshape='linear', # Ottagono perfetto
            bgcolor='white',
            angularaxis=dict(
                direction='clockwise', 
                rotation=90,           
                # CORRETTO: size e weight vanno direttamente dentro tickfont
                tickfont=dict(size=TICK_SIZE, weight='bold'),
                gridcolor='grey',
                griddash='dash',
                linewidth=0.6
            ),
        radialaxis=dict(
            visible=True,
            range=[0, ymax],
            tickmode='linear',
            tick0=10,
            dtick=10,
            ticksuffix='%',       
            angle=270,
            tickangle=270, 
            tickfont=dict(size=TICK_SIZE/1.2, color='rgba(0, 0, 0, 0.4)'),
            gridcolor='grey',
            griddash='dash',
            linewidth=0.6
            )
        )
    )

    return fig