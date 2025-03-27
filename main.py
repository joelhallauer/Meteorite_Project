from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import data as dt

# Daten laden
df = dt.load_and_process_data()

# Jahr-Bereich für den Year-Slider berechnen
min_year = int(df['year'].min())
max_year = int(df['year'].max())

# Helper-Funktion, um ein Histogramm ganz minimalistisch zu stylen
def style_hist(fig):
    fig.update_layout(
        title={'x': 0.5},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, title_text="")
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, title_text="")
    return fig

# Histogramm für den Massen-Slider (nur Säulen, zentrierter Titel)
mass_hist = px.histogram(
    df,
    x="mass",
    nbins=80,
    title="Masse",
    template="plotly_dark",
    range_x=[0, 10000000]
)
mass_hist.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="linear"
    )
)
mass_hist = style_hist(mass_hist)

# Histogramm für den Jahr-Slider (analog zum Massen-Slider)
year_hist = px.histogram(
    df,
    x="year",
    nbins=(max_year - min_year + 1),
    title="Jahr",
    template="plotly_dark"
)
year_hist.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="linear"
    )
)
year_hist = style_hist(year_hist)

# Karte erstellen mit Dark Mode (plotly_dark Template)
fig = px.scatter_mapbox(
    df,
    lat="reclat",
    lon="reclong",
    color="year",
    hover_name="name",
    hover_data=["mass", "fall", "GeoLocation"],
    center={"lat": 46.8521, "lon": 9.5297},
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=1,
    height=500,
    template="plotly_dark"
)
fig.update_layout(
    mapbox=dict(
        style="open-street-map"
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

app = Dash(__name__)
app.layout = html.Div(
    [
        # Linke Spalte: Titel, Inputs und Karte (70% Breite)
        html.Div(
            [
                # Obere Zeile: Titel + Inputs
                html.Div(
                    [
                        html.Div(
                            html.H1("Impact Atlas", style={"margin": "0", "padding-right": "20px"}),
                            style={"flex": "0 0 auto"}
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="input_search",
                                    type="search",
                                    placeholder="Ort eingeben",
                                    style={"margin-right": "10px"}
                                ),
                                dcc.Input(
                                    id="input_range",
                                    type="range",
                                    placeholder="Radius"
                                )
                            ],
                            style={"display": "flex", "alignItems": "center", "gap": "10px"}
                        )
                    ],
                    style={"display": "flex", "alignItems": "center", "padding": "10px"}
                ),
                # Karte
                html.Div(
                    [
                        html.Label("Karte", style={"padding": "10px 0"}),
                        dcc.Graph(id="graph", figure=fig, config={"scrollZoom": True})
                    ],
                    style={"padding": "10px"}
                )
            ],
            style={"width": "70%", "display": "inline-block", "verticalAlign": "top"}
        ),
        # Rechte Spalte: Filterbereich (30% Breite)
        html.Div(
            [
                # Massen-Histogramm-Slider
                html.Div(
                    [
                        dcc.Graph(id="mass-histogram", figure=mass_hist, config={'displayModeBar': False})
                    ],
                    style={"padding": "10px"}
                ),
                html.Hr(style={"borderColor": "#555"}),
                # Zustand Checkboxen
                html.Div(
                    [
                        html.Label("Zustand", style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Checklist(
                            id='zustand-checklist',
                            options=[
                                {'label': 'relict', 'value': 'relict'},
                                {'label': 'valid', 'value': 'valid'}
                            ],
                            value=['relict', 'valid'],
                            labelStyle={'display': 'inline-block', 'margin-right': '15px'},
                            inputStyle={'margin-right': '5px'}
                        )
                    ],
                    style={'padding': '10px'}
                ),
                html.Hr(style={"borderColor": "#555"}),
                # Jahr-Histogramm-Slider
                html.Div(
                    [
                        dcc.Graph(id="year-histogram", figure=year_hist, config={'displayModeBar': False})
                    ],
                    style={'padding': '10px'}
                ),
                html.Hr(style={"borderColor": "#555"}),
                # Dropdown für Kategorien (recclass) – angepasstes Styling, damit der Text lesbar ist
                html.Div(
                    [
                        html.Label("Kategorie", style={'font-weight': 'bold', 'font-size': '16px'}),
                        dcc.Dropdown(
                            id='recclass-dropdown',
                            options=[{'label': rec, 'value': rec} for rec in sorted(df['recclass'].unique())],
                            multi=True,
                            placeholder="Kategorie auswählen",
                            style={"backgroundColor": "#444", "color": "white"}
                        )
                    ],
                    style={'padding': '10px'}
                )
            ],
            style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}
        )
    ],
    style={
        "backgroundColor": "#333333",
        "color": "white",
        "minHeight": "100vh",
        "padding": "20px"
    }
)

if __name__ == '__main__':
    app.run(debug=True)
