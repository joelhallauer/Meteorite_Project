from dash import html, dcc
from .map import empty_figure
from .table import MeteorTable

def MapAndTable(df):
    """Linke Hauptspalte: Karte + darunter DataTable."""
    return html.Div(
        [
            # interaktive Karte
            dcc.Graph(
                id="meteor-map",
                figure=empty_figure(),
                config={"scrollZoom": True},
                style={"height": "50vh"},
            ),

            # Ergebnistabelle
            MeteorTable(df),
        ],
        style={
            "flex": "75%",
            "display": "flex",
            "flexDirection": "column",
            "padding": "10px",
        },
    )
