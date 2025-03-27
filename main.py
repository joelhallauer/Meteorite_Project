from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import data as dt

# Daten laden
df = dt.load_and_process_data()

# Histogramm erstellen mit integriertem Range Slider
mass_hist = px.histogram(
    df,
    x="mass",
    nbins=80,  # Anzahl der Balken anpassen
    title="Verteilung der Meteoriten Masse",
    labels={'mass': 'Masse (g)'},
    range_x=[0, 10000000]
)
# Integrierter Range Slider auf der x-Achse
mass_hist.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="linear"
    )
)

# Karte erstellen
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
    height=500
)
fig.update_layout(
    mapbox=dict(
        style="open-street-map"
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

# Dash App erstellen
app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Div(children=[
            html.H1('Impact Atlas'),
        ], style={'width': '75%', 'textAlign': 'left'}),
        html.Div(children=[
            dcc.Input(
                id="input_search",
                type="search",
                placeholder="Ort eingeben",
            ),
            dcc.Input(
                id="input_range",
                type="range",
                placeholder="Radius",
            )
        ], style={'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flexDirection': 'row'}),
    
    html.Div(children=[
        # Karte
        html.Div(children=[
            html.Label('Karte'),
            dcc.Graph(id="graph", figure=fig, config={'scrollZoom': True}),
        ], style={'padding': 10, 'flex': 1}),
        
        # Histogramm mit integriertem Range Slider
        html.Div(children=[
            dcc.Graph(id="mass-histogram", figure=mass_hist),

            dcc.Checklist(
                ['relict', 'valid'],
                ['relict', 'valid'],
                 inline=True,
)

        ], style={'padding': 10, 'flex': 1}),
    ], style={'display': 'flex', 'flexDirection': 'row'})
])

if __name__ == '__main__':
    app.run(debug=True)