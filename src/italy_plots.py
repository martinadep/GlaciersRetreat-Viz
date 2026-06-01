import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        font=dict(size=20),
        title=dict(font=dict(size=20)),
        xaxis=dict(
            tickfont=dict(size=16),        
            title=dict(font=dict(size=18)) 
        ),
        yaxis=dict(
            tickfont=dict(size=18)
        )
    )
    

    return fig