import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_glacier_mass_change(df: pd.DataFrame,
                            year_col: str = "year",
                            region_col: str = "region",
                            gt_col: str = "gt"):
    """
    Grafico interattivo della variazione della massa dei ghiacciai.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne year, region, gt (o i nomi passati).
    year_col : str
        Nome colonna anno.
    region_col : str
        Nome colonna regione.
    gt_col : str
        Nome colonna massa.

    Usage
    -----
    fig = plot_glacier_mass_change(df)
    fig.show()
    """

    regions = sorted(df[region_col].unique())
    years   = sorted(df[year_col].unique())
    min_year, max_year = int(years[0]), int(years[-1])

    # Palette colori distinta per ogni paese
    PALETTE = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
    ]
    color_map = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(regions)}

    # ── Trace per ogni paese ─────────────────────────────────────────────────────
    traces = []
    for region in regions:
        sub = df[df[region_col] == region].sort_values(year_col)
        traces.append(go.Scatter(
            x=sub[year_col],
            y=sub[gt_col],
            mode="lines+markers",
            name=region,
            line=dict(color=color_map[region], width=2),
            marker=dict(size=4),
            visible=True,
        ))

    print(regions)
    # ── Bottoni dropdown per selezionare paesi ───────────────────────────────────
    # "Tutti" + uno per ogni paese
    buttons = []

    # Bottone: tutti visibili
    buttons.append(dict(
        label="All regions",
        method="update",
        args=[{"visible": [True] * len(regions)}],
    ))

    # Bottone per ogni singolo paese
    regions_decoded=['Northern Arctic Canada','Southern Arctic Canada','Alaska','Antarctic and Subantarctic', 
                     'Central Asia','Eastern Asia','Northern Asia','Western Asia','Caucasus','Central Europe',
                     'Greenland','Iceland','New Zealand','Russian Arctic', 'Southern Andes 1', 'Southern Andes 2',
                     'Scandinavia','Svalbard and Jan Mayen', 'Tropics','Western North America']
    print(len(regions_decoded))
    for i, region in enumerate(regions_decoded):
        visible = [j == i for j in range(len(regions_decoded))]
        buttons.append(dict(
            label=region,
            method="update",
            args=[{"visible": visible}],
        ))

    # ── Slider anni ──────────────────────────────────────────────────────────────
    # Usa rangeselector + rangeslider sull'asse x per filtrare il range temporale
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=dict(
            text="Glacier mass change, 1960-2025",
            font=dict(size=18, family="Source Sans Pro, sans-serif"),
            x=0.5,
            xanchor='center',
        ),
        xaxis=dict(
            title=dict(
                text="Year",
                font=dict(size=12, family="Source Sans Pro, sans-serif")
                ),
            rangeslider=dict(visible=True, thickness=0.05),
            range=[min_year, max_year],
            type="linear",
        ),
        yaxis=dict(
            title=dict(
                text="Glacier mass change (Gt)",
                font=dict(size=12, family="Source Sans Pro, sans-serif")
                ),
            gridcolor="#e0e0e0",
            gridwidth=1,
        ),
        legend=dict(
            orientation="v",
            x=1.02,          # legenda più a destra
            y=0.95,          # leggermente abbassata
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#cccccc",
            borderwidth=1,
        ),

        updatemenus=[dict(
            type="dropdown",
            direction="down",
            x=0.72,           # was 0.0
            y=1.10,
            xanchor="left",  # was "right"
            yanchor="top",
            bgcolor="white",
            bordercolor="#cccccc",
            font=dict(size=13, family="Source Sans Pro, sans-serif"),
            buttons=buttons,
            showactive=True,
        )],
        # annotations=[dict(
        #     text="Select regions:",
        #     x=0.72,           # was 0.0
        #     y=1.17,
        #     xref="paper",
        #     yref="paper",
        #     showarrow=False,
        #     font=dict(size=13, family="Georgia, serif"),
        # )],


        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        height=550,
        width=1500,
        margin=dict(l=60, r=220, t=100, b=80)
    )

    # Linee griglia orizzontali tratteggiate come OurWorldInData
    fig.update_yaxes(showgrid=True, gridcolor="#e5e5e5", gridwidth=1, griddash="dash")
    fig.update_xaxes(showgrid=False)

    return fig

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.wgms_data_loader import load_wgms_regions_gt

def create_region_gt():
    df_demo=load_wgms_regions_gt()
    fig = plot_glacier_mass_change(df_demo)
    
    return go.Figure(fig)

