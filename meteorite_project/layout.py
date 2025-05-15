# meteorite_project/layout.py
from dash import html, dcc
from .components.map_table import MapAndTable
from .components.controls import Filters


def create_layout(df):
    """Statisches Grund-Layout für die Dash-App."""
    return html.Div(
        [
            html.H1(
                "Impact Atlas – Meteoriten weltweit",
                style={"textAlign": "center"},
            ),
            html.Div(
                [
                    # linke Spalte: Karte + Tabelle
                    MapAndTable(df),

                    # rechte Spalte: Filter, Ortssuche, Statistik
                    html.Div(
                        [
                            Filters(df),
                            html.Hr(),
                            html.H4("Ortssuche", style={"marginBottom": "10px"}),
                            # ---------------------- Ortssuche-Inputs ----------------------
                            html.Label("Ort:", style={"margin": "5px 0"}),
                            dcc.Input(
                                id="location-input",
                                type="text",
                                placeholder="z. B. Berlin, Paris, New York",
                                style={
                                    "width": "100%",
                                    "padding": "8px",
                                    "borderRadius": "4px",
                                    "border": "1px solid #ccc",
                                },
                            ),
                            html.Br(),
                            html.Label(
                                "Suchradius (km):", style={"margin": "10px 0 5px"}
                            ),
                            dcc.Dropdown(
                                id="radius-dropdown",
                                options=[
                                    {"label": "50 km", "value": 50},
                                    {"label": "100 km", "value": 100},
                                    {"label": "200 km", "value": 200},
                                    {"label": "500 km", "value": 500},
                                    {"label": "1000 km", "value": 1000},
                                    {"label": "Unbegrenzt", "value": "unlimited"},
                                ],
                                value="unlimited",
                                style={"width": "100%", "marginBottom": "10px"},
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Ortssuche starten",
                                        id="search-button",
                                        n_clicks=0,
                                        style={
                                            "width": "48%",
                                            "padding": "10px",
                                            "backgroundColor": "#4CAF50",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "4px",
                                            "cursor": "pointer",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    html.Button(
                                        "Zurücksetzen",
                                        id="reset-button",
                                        n_clicks=0,
                                        style={
                                            "width": "48%",
                                            "padding": "10px",
                                            "backgroundColor": "#f44336",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "4px",
                                            "cursor": "pointer",
                                            "fontWeight": "bold",
                                            "marginLeft": "4%",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "marginTop": "10px",
                                },
                            ),
                            # ----------------------------------------------------------------
                            html.Hr(),
                            html.Div(id="stats-container"),
                        ],
                        style={
                            "flex": "25%",
                            "padding": "20px",
                            "backgroundColor": "#f9f9f9",
                            "borderLeft": "1px solid #ccc",
                            "overflowY": "auto",
                        },
                    ),
                ],
                style={"display": "flex", "height": "85vh"},
            ),
        ],
        style={"maxWidth": "1600px", "margin": "0 auto", "padding": "20px"},
    )
