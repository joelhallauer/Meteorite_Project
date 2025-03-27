from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Daten laden
data = pd.read_csv('data/meteorite-landings.csv')

# Karte erstellen
fig = px.scatter_mapbox(
    data,
    lat="reclat",
    lon="reclong",
    color="year",
    hover_name="name",
    hover_data=["mass", "fall", "GeoLocation"],
    center={"lat": 46.8521, "lon": -9.5297},
    color_continuous_scale = px.colors.cyclical.IceFire,
    zoom=1,
    height=500
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Dash App erstellen
app = Dash(__name__)
app.layout = html.Div([
    html.H1('Impact Atlas'),            # Titel oben

    html.Div(children=[
        html.Div(children=[
        html.Label('Karte'),
        dcc.Graph(id="graph", figure=fig),   # Karte direkt darunter

        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[

        ], style={'padding': 10, 'flex': 1}),    

    ], style={'display': 'flex', 'flexDirection': 'row'})
])

if __name__ == '__main__':
    app.run(debug=True)
