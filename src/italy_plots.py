import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

TICK_SIZE = 16
TITLE_SIZE = 22
LEGEND_SIZE = 14

@st.cache_data
def load_data():
    df_raw = pd.read_csv("data/italy_glaciers.csv")
    df_raw.order_by = df_raw['ID Code']

    df_italy = df_raw[['Glacier Name', #'ID Code',
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
    columns_to_group = 'Mountain Sector'
    if region is not None:
        df = df[df["Region"] == region]
        columns_to_group = 'Mountain Group'
    
    counts = df[columns_to_group].value_counts().sort_values(ascending=True) 
    new_counts = df.groupby(columns_to_group)['Newly Formed'].sum().reindex(counts.index, fill_value=0)

    plot_df = pd.DataFrame({
         columns_to_group: counts.index,
        'Total Glaciers': counts.values,
        'Newly Formed Glaciers': new_counts.values
    })

    fig = px.bar(plot_df, x='Total Glaciers', y=columns_to_group, 
        orientation='h', title='Glacier Count by ' + columns_to_group,
        labels={'Total Glaciers': 'Number of Glaciers', columns_to_group: ''},
        color_discrete_sequence=['#1f77b4'])
    
    # legend and hover template
    fig.data[0].name = 'Total Glaciers'
    fig.data[0].showlegend = True
    fig.data[0].hovertemplate = '%{x}' 

    # new glaciers bars
    fig.add_trace(go.Bar( x=plot_df['Newly Formed Glaciers'], y=plot_df[columns_to_group],
                            orientation='h', name='Newly Formed Glaciers',
                            marker_color='lightblue', opacity=0.7, hovertemplate='%{x}'))

    fig.update_layout(
        barmode='overlay', 
        legend_title_text='', # remove title from legend
        hovermode='y unified', # unify hover on the y-axis
        legend=dict( yanchor="bottom", y=0.1, xanchor="right", x=1, font=dict(size=LEGEND_SIZE) )
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
def compass_aspect(df): 
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

@st.cache_data
def sunburst_counts(df):

    df['Count'] = 1

    fig = px.sunburst(
        df,
        path=['Mountain Sector', 'Mountain Group'],
        values='Count',
        color='Mountain Sector',
    )

    fig.update_layout(
        title=dict(
            text="<b> Mountain Sector Distribution</b>",
            x=0.5, y=0.95, font=dict(size=TITLE_SIZE)
        ),
        margin=dict(t=80, l=20, r=20, b=20),
        paper_bgcolor="#ffffff"
    )

    return fig

@st.cache_data
def tree(df):
    df['Count'] = 1 

    fig = px.treemap(
        df, 
        path=['Mountain Sector', 'Mountain Group'], 
        values='Count',
        color='Mountain Sector',
    )

    # Configurazione del testo
    fig.update_traces(
        textinfo="label+value",
        textfont=dict(size=15, family="Arial, sans-serif", color="white"), 
        hoverlabel=dict(bgcolor="#f8fafc", font_size=14, font_family="Arial"),
        hovertemplate="<b>%{label}</b><br>Numero Ghiacciai: %{value}<extra></extra>"
    )

    # Layout e impostazioni per bloccare la dimensione minima del testo
    fig.update_layout(
        # title=dict(
        #     text="<b>CATASTO DEI GHIACCIAI ITALIANI (1925)</b><br>"
        #         "<span style='font-size:14px; color:#64748b; font-weight:normal;'>"
        #         "Distribuzione gerarchica delle masse glaciali censite per Macro-Settore e Gruppo</span>",
        #     x=0.02, y=0.95,
        #     font=dict(size=)
        # ),
        margin=dict(t=100, l=15, r=15, b=15),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        
        # Mantiene il font leggibile ora che il testo si sviluppa in verticale
        uniformtext=dict(
            minsize=12,      
            mode='hide'      
        )
    )

    return fig

@st.cache_data
def map_glaciers_by_region(df):
    geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"

    region_name_map = {
        "Lombardy": "Lombardia", "Trentino": "Trentino-Alto Adige/Südtirol",
        "South Tyrol": "Trentino-Alto Adige/Südtirol", "Piedmont": "Piemonte",
        "Aosta Valley": "Valle d'Aosta/Vallée d'Aoste", "Veneto": "Veneto",
        "Friuli Venezia Giulia": "Friuli-Venezia Giulia", "Abruzzo": "Abruzzo"
    }
    
    df_geo = df.copy()
    df_geo['Region_geo'] = df_geo['Region'].map(region_name_map)
    
    # Calcolo del conteggio dei ghiacciai
    region_counts = df_geo['Region_geo'].value_counts().reset_index()
    region_counts.columns = ['Region_geo', 'Glacier Count']

    # Inseriamo TUTTE le restanti regioni italiane a 0
    all_italy_regions = {
        'Liguria', 'Emilia-Romagna', 'Toscana', 'Umbria', 'Marche', 'Lazio', 
        # 'Campania', 'Molise', 'Puglia', 'Basilicata', 'Calabria', 'Sicilia', 'Sardegna'
    }
    missing_df = pd.DataFrame({'Region_geo': list(all_italy_regions), 'Glacier Count': 0})
    region_counts = pd.concat([region_counts, missing_df], ignore_index=True)

    # TRUCCO SCALA COLORI: 0 è Bianco puro, da 0.0001 a 1 usiamo la palette dei Rossi (Reds)
    custom_reds = [
        [0.0, "rgb(255, 255, 255)"],       # Forza il valore minimo (0) a Bianco
        [0.0001, "rgb(254, 224, 210)"],    # Appena sopra lo zero parte con un rosa/rosso molto chiaro
        [1.0, "rgb(165, 15, 21)"]          # Rosso scuro per il valore massimo
    ]

    fig = px.choropleth(
        region_counts,
        geojson=geojson_url,
        locations='Region_geo',
        featureidkey='properties.reg_name',
        color='Glacier Count',
        color_continuous_scale=custom_reds, # Applica la scala personalizzata
        labels={'Glacier Count': 'Glacier Count', "Region_geo": 'Regione'},
        title='Glacier Count by Region in Italy',
        hover_data={'Region_geo': True, 'Glacier Count': True} 
    )

    fig.update_geos(
        visible=False,
        projection_type="mercator",
        fitbounds="locations"
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        margin={"r":0,"t":70,"l":0,"b":0},
        height=850 # Altezza ottimale per l'intera penisola
    )

    return fig

@st.cache_data
def map_glaciers_area_by_region(df, area_col='Area (km2)'):
    geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"

    # 1. Mapping corretto dei nomi del tuo df con i nomi esatti del GeoJSON di OpenPolis
    region_name_map = {
        "Lombardy": "Lombardia", "Trentino": "Trentino-Alto Adige/Südtirol",
        "South Tyrol": "Trentino-Alto Adige/Südtirol", "Piedmont": "Piemonte",
        "Aosta Valley": "Valle d'Aosta/Vallée d'Aoste", "Veneto": "Veneto",
        "Friuli Venezia Giulia": "Friuli-Venezia Giulia", "Abruzzo": "Abruzzo"
    }
    
    df_geo = df.copy()
    df_geo['Region_geo'] = df_geo['Region'].map(region_name_map)
    df_geo[area_col] = pd.to_numeric(df_geo[area_col], errors='coerce')
    
    # Aggregazione area
    region_area = df_geo.groupby('Region_geo').agg({area_col: 'sum'}).reset_index()
    region_area.columns = ['Region_geo', 'Total Glacier Area (km2)']

    # 2. Inseriamo TUTTE le restanti regioni italiane a 0 per unire l'Abruzzo al Nord
    all_italy_regions = {
        'Liguria', 'Emilia-Romagna', 'Toscana', 'Umbria', 'Marche', 'Lazio', 
        #'Campania', 'Molise', 'Puglia', 'Basilicata', 'Calabria', 'Sicilia', 'Sardegna'
    }
    missing_df = pd.DataFrame({'Region_geo': list(all_italy_regions), 'Total Glacier Area (km2)': 0.0})
    region_area = pd.concat([region_area, missing_df], ignore_index=True)

    # 3. TRUCCO SCALA COLORI: 0 è Bianco puro, da 0.0001 a 1 usiamo la palette Blues
    custom_blues = [
        [0.0, "rgb(255, 255, 255)"],       # Forza il valore minimo (0) a Bianco
        [0.0001, "rgb(222, 235, 247)"],    # Appena sopra lo zero parte con un azzurro visibile
        [1.0, "rgb(8, 48, 107)"]           # Blu scuro per il valore massimo
    ]

    fig = px.choropleth(
        region_area,
        geojson=geojson_url,
        locations='Region_geo',
        featureidkey='properties.reg_name',
        color='Total Glacier Area (km2)',
        color_continuous_scale=custom_blues, # Applica la scala personalizzata
        labels={'Total Glacier Area (km2)': 'Area (km2)', "Region_geo": 'Regione'},
        title='Total Glacier Area by Region in Italy',
        hover_data={'Region_geo': True, 'Total Glacier Area (km2)': ':.2f'} # Arrotonda a 2 decimali l'hover
    )

    fig.update_geos(
        visible=False,
        projection_type="mercator",
        fitbounds="locations"
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        margin={"r":0,"t":70,"l":0,"b":0},
        height=850 # Alzata a 850 per far stare tutta l'Italia intera senza stringerla
    )

    return fig

@st.cache_data
def line_count_trend(df):
    area_cols = ['Area CGI (km2)', 'Area WGI (km2)', 'Area (km2)']

    # Count 1 for each glacier when the corresponding area value is present
    count_df = df.copy()
    for c in area_cols:
        count_df[c] = pd.to_numeric(count_df[c], errors='coerce')

    count_df['CGI Count'] = count_df['Area CGI (km2)'].notna().astype(int)
    count_df['WGI Count'] = count_df['Area WGI (km2)'].notna().astype(int)
    count_df['Area Count'] = count_df['Area (km2)'].notna().astype(int)

    region_counts = count_df.groupby('Region')[['CGI Count', 'WGI Count', 'Area Count']].sum().reset_index()
    df_melt = region_counts.melt(
        id_vars='Region',
        value_vars=['CGI Count', 'WGI Count', 'Area Count'],
        var_name='Measure',
        value_name='Glacier Count'
    )

    measure_to_year = {
        'CGI Count': 1960,
        'WGI Count': 1980,
        'Area Count': 2010,
    }
    df_melt['Year'] = df_melt['Measure'].map(measure_to_year)
    df_melt = df_melt.sort_values(['Region', 'Year'])

    fig = px.line(
        df_melt,
        x='Year',
        y='Glacier Count',
        color='Region',
        markers=True,
        labels={'Glacier Count': 'Glacier Count', 'Year': 'Year'},
        title='Glacier Count Trend by Region'
    )

    fig.update_layout(
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        legend=dict(font=dict(size=LEGEND_SIZE)),
        xaxis=dict(tickmode='array', tickvals=[1960, 1980, 2010])
    )

    return fig

def line_area_trend(df):
    area_cols = ['Area CGI (km2)', 'Area WGI (km2)', 'Area (km2)']
    for c in area_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    region_area = df.groupby('Region')[area_cols].sum().reset_index()

    df_melt = region_area.melt(id_vars='Region', value_vars=area_cols,
                               var_name='Measure', value_name='TotalArea')

    measure_to_year = {'Area CGI (km2)': 1960, 'Area WGI (km2)': 1980, 'Area (km2)': 2010}
    df_melt['Year'] = df_melt['Measure'].map(measure_to_year)

    # Sort so lines connect in chronological order
    df_melt = df_melt.sort_values(['Region', 'Year'])

    # Plot: x = Year, y = TotalArea, one line per Region
    fig = px.line(df_melt, x='Year', y='TotalArea', color='Region', markers=True,
                  labels={'TotalArea': 'Total Glacier Area (km2)', 'Year': 'Year'},
                  title='Glacier Area Trend by Region')

    fig.update_layout(
        font=dict(size=TICK_SIZE),
        title=dict(font=dict(size=TITLE_SIZE)),
        legend=dict(font=dict(size=LEGEND_SIZE)),
        xaxis=dict(tickmode='array', tickvals=[1960, 1980, 2010])
    )

    return fig