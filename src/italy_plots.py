import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

TICK_SIZE = 16
TITLE_SIZE = 22
LEGEND_SIZE = 14

COLOR_COUNT_MAIN = '#900d12'        
COLOR_COUNT_LIGHT = "#fcae91" 
COLOR_MAP_COUNTS = {
    "Porro (1925)": '#fcae91',
    "CGI (1959-1962)": '#fb6a4a',
    "WGI (1979-1989)": '#cb181d',
    "New Glacier Inventory (2005-2012)": "#900d12"
}

COLOR_AREA_MAIN = '#07587d'  
PALETTE_AREA_TREND = ['#aec7e8', '#1f77b4', '#07587d']

# ----------------------- Data Loading Functions -----------------------
@st.cache_data
def load_data():
    df_raw = pd.read_csv("data/italy_glaciers.csv")
    
    df_italy = df_raw[['Glacier Name', 'Mountain Sector', 'Mountain Group', 'Region', 
                        'Glacier Type', 'Aspect', 'Area CGI (km2)', 'Area WGI (km2)',
                        'Area (km2)', 'Year', 'Newly Formed']].copy()
    df_italy['Area CGI (km2)'] = pd.to_numeric(df_italy['Area CGI (km2)'], errors='coerce')
    df_italy['Area WGI (km2)'] = pd.to_numeric(df_italy['Area WGI (km2)'], errors='coerce')
    df_italy['Area (km2)'] = pd.to_numeric(df_italy['Area (km2)'], errors='coerce')
    
    return df_italy

@st.cache_data
def load_porro_data():
    df_porro = pd.read_csv("data/porro1925/porro_1925_mapped_soiusa.csv")
    return df_porro

# ----------------------- Plotting Functions -----------------------
@st.cache_data
def region_counts_map(df):
    geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
    region_name_map = {
        "Lombardy": "Lombardia", "Trentino": "Trentino-Alto Adige/Südtirol",
        "South Tyrol": "Trentino-Alto Adige/Südtirol", "Piedmont": "Piemonte",
        "Aosta Valley": "Valle d'Aosta/Vallée d'Aoste", "Veneto": "Veneto",
        "Friuli Venezia Giulia": "Friuli-Venezia Giulia", "Abruzzo": "Abruzzo"
    }
    
    df_geo = df.copy()
    df_geo['Region_geo'] = df_geo['Region'].map(region_name_map)
    region_counts = df_geo['Region_geo'].value_counts().reset_index()
    region_counts.columns = ['Region_geo', 'Glacier Count']

    all_italy_regions = {'Liguria', 'Emilia-Romagna', 'Toscana', 'Umbria', 'Marche', 'Lazio'}
    missing_df = pd.DataFrame({'Region_geo': list(all_italy_regions), 'Glacier Count': 0})
    region_counts = pd.concat([region_counts, missing_df], ignore_index=True)

    custom_reds = [
        [0.0, "rgb(255, 255, 255)"],
        [0.0001, "rgb(254, 224, 210)"],
        [1.0, COLOR_COUNT_MAIN]
    ]

    fig = px.choropleth(
        region_counts, geojson=geojson_url, locations='Region_geo',
        featureidkey='properties.reg_name', color='Glacier Count',
        color_continuous_scale=custom_reds, title='Glacier Count by Region',
        labels={'Glacier Count': 'Glacier Count', "Region_geo": 'Region'}
    )
    fig.update_geos(visible=False, projection_type="mercator", fitbounds="locations")
    fig.update_layout(font=dict(size=TICK_SIZE), title=dict(font=dict(size=TITLE_SIZE)), margin={"r":0,"t":70,"l":0,"b":0}, height=550)
    return fig

@st.cache_data
def region_area_map(df):
    geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
    region_name_map = {
        "Lombardy": "Lombardia", "Trentino": "Trentino-Alto Adige/Südtirol",
        "South Tyrol": "Trentino-Alto Adige/Südtirol", "Piedmont": "Piemonte",
        "Aosta Valley": "Valle d'Aosta/Vallée d'Aoste", "Veneto": "Veneto",
        "Friuli Venezia Giulia": "Friuli-Venezia Giulia", "Abruzzo": "Abruzzo"
    }
    
    df_geo = df.copy()
    df_geo['Region_geo'] = df_geo['Region'].map(region_name_map)
    region_area = df_geo.groupby('Region_geo')['Area (km2)'].sum().reset_index()
    region_area.columns = ['Region_geo', 'Total Glacier Area (km2)']

    all_italy_regions = {'Liguria', 'Emilia-Romagna', 'Toscana', 'Umbria', 'Marche', 'Lazio'}
    missing_df = pd.DataFrame({'Region_geo': list(all_italy_regions), 'Total Glacier Area (km2)': 0.0})
    region_area = pd.concat([region_area, missing_df], ignore_index=True)

    custom_blues = [
        [0.0, "rgb(255, 255, 255)"],
        [0.0001, "rgb(222, 235, 247)"],
        [1.0, COLOR_AREA_MAIN]
    ]

    fig = px.choropleth(
        region_area, geojson=geojson_url, locations='Region_geo',
        featureidkey='properties.reg_name', color='Total Glacier Area (km2)',
        color_continuous_scale=custom_blues, title='Total Glacier Area by Region',
        labels={'Total Glacier Area (km2)': 'Area (km2)', "Region_geo": 'Region'},
        hover_data={'Total Glacier Area (km2)': ':.2f'}
    )
    fig.update_geos(visible=False, projection_type="mercator", fitbounds="locations")
    fig.update_layout(font=dict(size=TICK_SIZE), title=dict(font=dict(size=TITLE_SIZE)), margin={"r":0,"t":70,"l":0,"b":0}, height=550)
    return fig

@st.cache_data
def historical_area(df, region=None):
    df_clean = df.copy()
    
    if region is not None:
        group_col = 'Mountain Group'
        title_text = f'Glacier Area Shrinkage by Mountain Group in {region}'
    else:
        group_col = 'Mountain Sector'
        title_text = 'Glacier Area Shrinkage by Mountain Sector'

    df_clean['Area CGI (km2)'] = df_clean['Area CGI (km2)'].fillna(0)
    df_clean['Area WGI (km2)'] = df_clean['Area WGI (km2)'].fillna(0)
    df_clean['Area (km2)'] = df_clean['Area (km2)'].fillna(0)

    df_grouped = df_clean.groupby(group_col)[['Area CGI (km2)', 'Area WGI (km2)', 'Area (km2)']].sum().reset_index()
    df_grouped = df_grouped.sort_values(by='Area (km2)', ascending=False)
    
    df_melt = df_grouped.melt(
        id_vars=group_col,
        value_vars=['Area CGI (km2)', 'Area WGI (km2)', 'Area (km2)'],
        var_name='Inventory Period',
        value_name='Total Area (km2)'
    )
    
    period_mapping = {
        'Area CGI (km2)': "CGI (1959-1962)",
        'Area WGI (km2)': "WGI (1979-1989)",
        'Area (km2)': "New Glacier Inventory (2005-2012)"
    }
    df_melt['Inventory Period'] = df_melt['Inventory Period'].map(period_mapping)
    
    fig = px.bar(
        df_melt, x=group_col, y='Total Area (km2)',
        color='Inventory Period', barmode='group', title=title_text,
        labels={'Total Area (km2)': 'Total Area (km2)', group_col: ''},
        color_discrete_sequence=PALETTE_AREA_TREND
    )
    
    fig.update_layout(
        font=dict(size=TICK_SIZE), title=dict(font=dict(size=TITLE_SIZE)),
        legend=dict(font=dict(size=LEGEND_SIZE), title_text=''), hovermode='x unified')
    
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='<br>Total Area: %{y:.2f} km²')
    fig.update_layout(hoverlabel=dict(font=dict(size=12)))
    return fig

@st.cache_data
def historical_counts(df, df_porro, region=None):
    df_m_clean = df.copy()
    
    df_m_clean['CGI Count'] = df_m_clean['Area CGI (km2)'].notna().astype(int)
    df_m_clean['WGI Count'] = df_m_clean['Area WGI (km2)'].notna().astype(int)
    df_m_clean['Recent Count'] = 1 
    
    if region is not None:
        group_col = 'Mountain Group'
        title_text = f'Glacier Count Evolution by Mountain Group in {region}'
        
        df_merged = df_m_clean.groupby(group_col).agg({
            'CGI Count': 'sum', 'WGI Count': 'sum', 'Recent Count': 'sum'
        }).reset_index()
        df_merged.columns = [group_col, "CGI (1959-1962)", "WGI (1979-1989)", "New Glacier Inventory (2005-2012)"]
        value_vars_list = ["CGI (1959-1962)", "WGI (1979-1989)", "New Glacier Inventory (2005-2012)"]
    else:
        df_p_clean = df_porro.copy()
        group_col = 'Mountain Sector'
        title_text = 'Glacier Count Evolution by Mountain Sector'
        
        porro_counts = df_p_clean[group_col].value_counts().reset_index()
        porro_counts.columns = [group_col, "Porro (1925)"]
        
        modern_grouped = df_m_clean.groupby(group_col).agg({
            'CGI Count': 'sum', 'WGI Count': 'sum', 'Recent Count': 'sum'
        }).reset_index()
        modern_grouped.columns = [group_col, "CGI (1959-1962)", "WGI (1979-1989)", "New Glacier Inventory (2005-2012)"]
        
        df_merged = pd.merge(porro_counts, modern_grouped, on=group_col, how='outer').fillna(0)
        value_vars_list = ["Porro (1925)", "CGI (1959-1962)", "WGI (1979-1989)", "New Glacier Inventory (2005-2012)"]

    df_merged = df_merged.sort_values(by="New Glacier Inventory (2005-2012)", ascending=False)
    
    df_melt = df_merged.melt(
        id_vars=group_col, value_vars=value_vars_list,
        var_name='Inventory', value_name='Glacier Count'
    )
    
    fig = px.bar(
        df_melt, x=group_col, y='Glacier Count',
        color='Inventory', barmode='group', title=title_text,
        labels={'Glacier Count': 'Number of Glaciers', group_col: ''},
        color_discrete_map=COLOR_MAP_COUNTS 
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE), title=dict(font=dict(size=TITLE_SIZE)),
        legend=dict(font=dict(size=LEGEND_SIZE), title_text=''), hovermode='x unified'
    )
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate='<br>Count: %{y}')
    fig.update_layout(hoverlabel=dict(font=dict(size=12)))
    return fig

@st.cache_data
def newly_formed_barchart(df, region=None):
    columns_to_group = 'Mountain Sector'
    if region is not None:
        columns_to_group = 'Mountain Group'
    
    counts = df[columns_to_group].value_counts().sort_values(ascending=True) 
    new_counts = df.groupby(columns_to_group)['Newly Formed'].sum().reindex(counts.index, fill_value=0)

    plot_df = pd.DataFrame({
         columns_to_group: counts.index,
        'Total Glaciers': counts.values,
        'Newly Formed Glaciers': new_counts.values
    })

    fig = px.bar(plot_df, x='Total Glaciers', y=columns_to_group, 
        orientation='h', title='Newly formed glaciers in ' + columns_to_group,
        labels={'Total Glaciers': 'Number of Glaciers', columns_to_group: ''},
        color_discrete_sequence=[COLOR_COUNT_MAIN]) 
    
    fig.data[0].name = 'Total Glaciers'
    fig.data[0].showlegend = True
    fig.data[0].hovertemplate = '%{x}' 

    fig.add_trace(go.Bar(x=plot_df['Newly Formed Glaciers'], y=plot_df[columns_to_group],
                          orientation='h', name='Newly Formed Glaciers',
                          marker_color=COLOR_COUNT_LIGHT, opacity=0.7, hovertemplate='%{x}')) 

    fig.update_layout(
        barmode='overlay', 
        legend_title_text='', 
        hovermode='y unified', 
        legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=1, font=dict(size=LEGEND_SIZE))
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE), 
        title=dict(font=dict(size=TITLE_SIZE)), 
        xaxis=dict(tickfont=dict(size=TICK_SIZE)), 
        yaxis=dict(tickfont=dict(size=TICK_SIZE))
    )
    return fig
@st.cache_data
def compass_aspect(df): 
    target_df = df.copy()
    
    valid_aspect = target_df['Aspect'].notna() & (target_df['Aspect'].str.strip() != "") & (target_df['Aspect'] != "SW / W")
    order = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    aspect_num_cleaned = target_df.loc[valid_aspect, 'Aspect'].value_counts().reindex(order, fill_value=0)
    aspect_area_cleaned = target_df.loc[valid_aspect].groupby('Aspect')['Area (km2)'].sum().reindex(order, fill_value=0)

    pct_num = (aspect_num_cleaned / aspect_num_cleaned.sum() * 100) if aspect_num_cleaned.sum() > 0 else aspect_num_cleaned
    pct_area = (aspect_area_cleaned / aspect_area_cleaned.sum() * 100) if aspect_area_cleaned.sum() > 0 else aspect_area_cleaned

    order_closed = order + [order[0]]
    values_num_closed = list(pct_num.values) + [pct_num.values[0]]
    values_area_closed = list(pct_area.values) + [pct_area.values[0]]

    max_val = max(max(values_num_closed), max(values_area_closed))
    ymax = max(40, np.ceil(max_val / 10) * 10)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_num_closed, theta=order_closed, fill='toself', fillcolor='rgba(181, 66, 46, 0.15)', 
        line=dict(color=COLOR_COUNT_MAIN, width=2.5), name='Number of Glaciers (%)', 
        hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_area_closed, theta=order_closed, fill='toself', fillcolor='rgba(7, 88, 125, 0.15)', 
        line=dict(color=COLOR_AREA_MAIN, width=2.5), name='Glaciers Area (%)',
        hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text='Glacier Aspect Distribution (%)', font=dict(size=TITLE_SIZE)),
        font=dict(size=TICK_SIZE), hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=LEGEND_SIZE)),
        polar=dict(
            gridshape='linear', bgcolor='white',
            angularaxis=dict(
                direction='clockwise', rotation=90, tickfont=dict(size=TICK_SIZE, weight='bold'),
                gridcolor='grey', griddash='dash', linewidth=0.6),
            radialaxis=dict(
                visible=True, range=[0, ymax], tickmode='linear', tick0=10, dtick=10, ticksuffix='%', 
                angle=270, tickangle=270, tickfont=dict(size=int(TICK_SIZE/1.2), color='rgba(0, 0, 0, 0.4)'),
                gridcolor='grey', griddash='dash', linewidth=0.6)
        )
    )
    return fig

@st.cache_data
def pie_glacier_types(df, region=None, by_area=False):
    color_map = {
        'Mountain': "#4f88b1",
        'Glacieret': "#9fc3dd",
        'Valley': "#797f84"
    }

    if region is not None:
        prefix = "Area " if by_area else ""
        title_text = f"Glacier Type {prefix}Distribution in {region}"
    else:
        title_text = 'Glacier Type Area Distribution' if by_area else 'Glacier Type Distribution'

    if by_area:
        type_df = df.groupby('Glacier Type')['Area (km2)'].sum().reset_index()
        type_df.columns = ['Glacier Type', 'Total Area (km2)']
        value_col = 'Total Area (km2)'
    else:
        type_df = df['Glacier Type'].value_counts().reset_index()
        type_df.columns = ['Glacier Type', 'Count']
        value_col = 'Count'

    fig = px.pie(
        type_df, values=value_col, names='Glacier Type', color='Glacier Type',
        color_discrete_map=color_map, title=title_text
    )

    if by_area:
        hovertemplate = "%{label}<br>Total Area: %{value:.2f} km²<br>%{percent}"
    else:
        hovertemplate = "%{label}<br>Count: %{value}<br>%{percent}"

    fig.update_traces(
        textposition='inside', textinfo='percent+label', textfont_size=14,
        hovertemplate=hovertemplate
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        legend=dict(font=dict(size=LEGEND_SIZE)),
        hoverlabel=dict(font=dict(size=12))
    )
    return fig

@st.cache_data
def pie_glacier_types_area(df, region=None):
    return pie_glacier_types(df, region=region, by_area=True)