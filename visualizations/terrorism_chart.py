import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_terrorism_deaths(df: pd.DataFrame,
                          year_col: str = "year",
                          country_col: str = "country",
                          deaths_col: str = "deaths"):
    """
    Grafico interattivo delle morti per terrorismo.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne year, country, deaths (o i nomi passati).
    year_col : str
        Nome colonna anno.
    country_col : str
        Nome colonna paese/regione.
    deaths_col : str
        Nome colonna morti.

    Usage
    -----
    fig = plot_terrorism_deaths(df)
    fig.show()
    """

    countries = sorted(df[country_col].unique())
    years     = sorted(df[year_col].unique())
    min_year, max_year = int(years[0]), int(years[-1])

    # Palette colori distinta per ogni paese
    PALETTE = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
    ]
    color_map = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(countries)}

    # ── Trace per ogni paese ─────────────────────────────────────────────────────
    traces = []
    for country in countries:
        sub = df[df[country_col] == country].sort_values(year_col)
        traces.append(go.Scatter(
            x=sub[year_col],
            y=sub[deaths_col],
            mode="lines+markers",
            name=country,
            line=dict(color=color_map[country], width=2),
            marker=dict(size=4),
            visible=True,
        ))

    # ── Bottoni dropdown per selezionare paesi ───────────────────────────────────
    # "Tutti" + uno per ogni paese
    buttons = []

    # Bottone: tutti visibili
    buttons.append(dict(
        label="All regions",
        method="update",
        args=[{"visible": [True] * len(countries)}],
    ))

    # Bottone per ogni singolo paese
    for i, country in enumerate(countries):
        visible = [j == i for j in range(len(countries))]
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visible}],
        ))

    # ── Slider anni ──────────────────────────────────────────────────────────────
    # Usa rangeselector + rangeslider sull'asse x per filtrare il range temporale
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=dict(
            text="Terrorism Deaths",
            font=dict(size=22, family="Georgia, serif"),
            x=0.02,
        ),
        xaxis=dict(
            title="Year",
            rangeslider=dict(visible=True, thickness=0.05),
            range=[min_year, max_year],
            type="linear",
        ),
        yaxis=dict(
            title="Confirmed deaths",
            gridcolor="#e0e0e0",
            gridwidth=1,
        ),
        legend=dict(
            orientation="v",
            x=1.01,
            y=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#cccccc",
            borderwidth=1,
        ),
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            x=0.0,
            y=1.12,
            xanchor="left",
            yanchor="top",
            bgcolor="white",
            bordercolor="#cccccc",
            font=dict(size=13),
            buttons=buttons,
            showactive=True,
        )],
        annotations=[dict(
            text="Select region:",
            x=0.0,
            y=1.17,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=13),
        )],
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        height=550,
        margin=dict(l=60, r=160, t=100, b=80),
    )

    # Linee griglia orizzontali tratteggiate come OurWorldInData
    fig.update_yaxes(showgrid=True, gridcolor="#e5e5e5", gridwidth=1, griddash="dash")
    fig.update_xaxes(showgrid=False)

    return fig


# ── Demo con dati sintetici ──────────────────────────────────────────────────
if __name__ == "__main__":
    np.random.seed(42)
    years     = list(range(1970, 2022))
    countries = ["Afghanistan", "Iraq", "Syria", "Nigeria", "Colombia", "Yemen"]

    rows = []
    # Profili realistici per ogni paese
    profiles = {
        "Afghanistan": lambda y: max(0, int(500  * max(0, (y-2005)/5)**1.8 + np.random.normal(0,200))),
        "Iraq":        lambda y: max(0, int(800  * np.exp(-((y-2006)**2)/18) + np.random.normal(0,150))),
        "Syria":       lambda y: max(0, int(1200 * np.exp(-((y-2014)**2)/10) + np.random.normal(0,100))),
        "Nigeria":     lambda y: max(0, int(600  * max(0, (y-2010)/4)**1.5  + np.random.normal(0,100))),
        "Colombia":    lambda y: max(0, int(400  * np.exp(-((y-1990)**2)/80) + np.random.normal(0,80))),
        "Yemen":       lambda y: max(0, int(500  * max(0, (y-2014)/3)**1.4  + np.random.normal(0,80))),
    }

    for country, fn in profiles.items():
        for y in years:
            rows.append({
                "year": y,
                "country": country,
                "deaths": fn(y),
            })

    df_demo = pd.DataFrame(rows)

    fig = plot_terrorism_deaths(df_demo)
    fig.show()
