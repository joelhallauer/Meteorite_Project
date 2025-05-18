import dash
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from flask_caching import Cache

df = pd.read_csv("data/meteorite-landings-cleaned.csv")

# Log-Spalte (Basis 10) für den Slider
df["log_mass"] = np.log10(df["mass"] + 1)  # +1 g verhindert negative Logs

# Formatierer für die Masse
def format_mass(mass: float) -> str:
    if mass < 1_000:               # < 1 kg
        return f"{mass:.2f} g"
    elif mass < 1_000_000:         # < 1 t
        return f"{mass/1_000:.2f} kg"
    else:
        return f"{mass/1_000_000:.2f} t"

def format_mass_int(mass: float) -> str:
    """Massen schön ohne Nachkommastellen (außer < 1 g) formatieren."""
    if mass < 1:                     # 0,1 g usw. soll eine Nachkomma behalten
        return f"{mass:.1f} g"
    if mass < 1_000:
        return f"{int(round(mass))} g"
    if mass < 1_000_000:
        return f"{int(round(mass/1_000))} kg"
    return f"{int(round(mass/1_000_000))} t"

# Initialisiere den Geocoder
geolocator = Nominatim(user_agent="impact-atlas")

# --- App-Initialisierung ---
app = dash.Dash(__name__)
app.title = "Impact Atlas"

# --- Caching-Config ---
cache = Cache(app.server, config={
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 3600       # 1 h Standard-Timeout
})

# --- Hilfs­funktionen mit Cache ---
@cache.memoize()                       # cacht jede Ort-Anfrage
def geocode_location(place: str):
    """Gibt (lat, lon) oder None zurück - gecacht."""
    loc = geolocator.geocode(place)
    return (loc.latitude, loc.longitude) if loc else None

# --- Layout der App ---
app.layout = html.Div([
    html.H1("Impact Atlas - Meteoriten weltweit", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    html.Div(id="main-container", children=[
        
        # Kartenbereich
        html.Div([
            dcc.Graph(id='meteor-map', config={"scrollZoom": True},
                    style={'height': '50vh'}),

            dash_table.DataTable(                      # Tabelle direkt DARUNTER
                id='meteor-table',
                columns=[
                    {"name": "Name", "id": "name"},
                    {"name": "Jahr", "id": "year"},
                    {"name": "Masse", "id": "formatted_mass"},
                    {"name": "Klasse", "id": "recclass"},
                    {"name": "Land", "id": "country"},
                ],
                page_size=10,
                style_table={
                    'height': '35vh',
                    'overflowY': 'auto',
                    'marginTop': '8px',
                    'tableLayout': 'fixed',    # wichtig für feste Spaltenbreite
                },
                style_cell={
                    'fontFamily': 'Arial',
                    'fontSize': '12px',
                    'padding': '3px',
                    'textAlign': 'left',
                    # jede Spalte genau gleich breit
                    'width': '20%',
                    'minWidth': '20%',
                    'maxWidth': '20%',
                    # bei langen Einträgen nichts verschieben lassen
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
            ),
        ], style={'flex': '75%', 'padding': '10px',          # bleibt linker Bereich
                'display': 'flex', 'flexDirection': 'column'}),

        # Steuerungsbereich
        html.Div([
            html.H4("Karte:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Tabs(
                id="map-tabs",
                value="Punktekarte",  # Standardwert
                children=[
                    dcc.Tab(label="Punktekarte", value="Punktekarte"),
                    dcc.Tab(label="Heatmap", value="Heatmap"),
                ],
                style={'marginBottom': '15px'}
            ),

            # NEU: Marker-Clustering On/Off
            html.Div([
                dcc.Checklist(
                    options=[{'label': 'Marker-Clustering', 'value': 'on'}],
                    value=['on'],                # standardmäßig eingeschaltet
                    id='cluster-switch',
                    labelStyle={'display': 'inline-block'}
                )
            ], style={'marginBottom': '20px'}),

            # Masse-Filter
            html.H4("Masse in Gramm:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='mass-slider-display',
                    style={'textAlign':'center', 'fontSize':'12px', 'marginTop':'-6px'}),
            dcc.RangeSlider(
                id='mass-slider',
                min=df['log_mass'].min(),      
                max=df['log_mass'].max(),
                value=[df['log_mass'].min(), df['log_mass'].max()],
                marks={
                    float(f"{tick:.2f}"): format_mass_int(10**tick - 1)
                    for tick in np.linspace(df['log_mass'].min(),
                                            df['log_mass'].max(),
                                            8)
                },
                step=0.05,
                updatemode='drag',
            ),
            html.Br(),
            html.Div([
                html.Label("min:", style={'margin': '10px'}),
                dcc.Input(
                    id='min-mass-input',
                    type='number',
                    value=df['mass'].min(),
                    style={'width': '45%', 'marginRight': '5%'}
                ),
                html.Label("max:", style={'margin': '10px'}),
                dcc.Input(
                    id='max-mass-input',
                    type='number',
                    value=df['mass'].max(),
                    style={'width': '45%'}
                )
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),

            # Meteoritentyp-Filter
            html.H4("Meteoritentyp:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Dropdown(
                options=[{"label": i, "value": i} for i in sorted(df["recclass"].unique())],
                value=None,
                multi=True,
                id="class-filter",
                placeholder="Typ auswählen (mehrere möglich)"
            ),

            # Jahr-Filter
            html.H4("Jahr:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='year-slider-display',
                style={'textAlign':'center', 'fontSize':'12px','marginTop':'-6px'}),
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=[df['year'].min(), df['year'].max()],
                marks={int(i): f'{int(i)}' for i in np.linspace(df['year'].min(), df['year'].max(), 5)},
                updatemode='drag'
            ),
            html.Br(),
            html.Div([
                html.Label("Von:", style={'margin': '10px'}),
                dcc.Input(
                    id='min-year-input',
                    type='number',
                    value=df['year'].min(),
                    style={'width': '45%', 'marginRight': '5%'}
                ),
                html.Label("Bis:", style={'margin': '10px'}),
                dcc.Input(
                    id='max-year-input',
                    type='number',
                    value=df['year'].max(),
                    style={'width': '45%'}
                )
            ], style={'display': 'flex', 'gap': '10px'}),

            # Fall/Found-Filter
            html.H4("Status (Fall/Found):", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Checklist(
                options=[
                    {"label": "Beobachtet", "value": "Fell"},
                    {"label": "Gefunden", "value": "Found"}
                ],
                value=df["fall"].unique().tolist(),
                id="fall-filter",
                labelStyle={'display': 'inline-block', 'margin': '3px 0'}
            ),

            # Ortssuche
            html.H4("Ortssuche:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Label("Ort:", style={'margin': '10px'}),
            dcc.Input(
                id='location-input',
                type='text',
                placeholder='z. B. Berlin, Paris, New York',
                style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ccc'}
            ),
            html.Br(),
            html.Label("Suchradius (km):", style={'margin': '10px'}),
            dcc.Dropdown(
                id='radius-dropdown',
                options=[
                    {'label': '50 km', 'value': 50},
                    {'label': '100 km', 'value': 100},
                    {'label': '200 km', 'value': 200},
                    {'label': '500 km', 'value': 500},
                    {'label': '1000 km', 'value': 1000},
                    {'label': 'Unbegrenzt', 'value': 'unlimited'}
                ],
                value='unlimited',
                style={'width': '100%', 'marginBottom': '15px'}
            ),
            html.Div([
                html.Button(
                    'Ortssuche starten',
                    id='search-button',
                    style={
                        'width': '48%',
                        'padding': '10px',
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'marginTop': '10px'
                    }
                ),
                html.Button(
                    'Zurücksetzen',
                    id='reset-button',
                    style={
                        'width': '48%',
                        'padding': '10px',
                        'backgroundColor': '#f44336',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'marginTop': '10px',
                        'marginLeft': '4%'
                    }
                )
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),

            # Statistik
            html.H4("Statistik", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='stats-container')
        ], style={
            'flex': '25%',
            'padding': '20px',
            'backgroundColor': '#f9f9f9',
            'borderLeft': '1px solid #ccc',
            'borderRadius': '0 5px 5px 0',
            'overflowY': 'auto',
            'maxHeight': '85vh'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-between',
        'border': '1px solid #ddd',
        'borderRadius': '5px',
        'boxShadow': '0 0 10px rgba(0,0,0,0.1)',
        'height': '85vh'
    })
], id="app-container", style={
    'maxWidth': '1600px',
    'margin': '0 auto',
    'padding': '20px',
    'boxSizing': 'border-box',
    'fontFamily': 'Arial, sans-serif'
})

# --- Callbacks ---
@app.callback(
    [Output('location-input', 'value'),
     Output('radius-dropdown', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def reset_location_inputs(n_clicks):
    if n_clicks:
        return '', 'unlimited'
    return dash.no_update

@app.callback(
    [Output('meteor-map',   'figure'),
     Output('stats-container', 'children'),
     Output('meteor-table', 'data')],
    [Input('fall-filter',   'value'),
     Input('class-filter',  'value'),
     Input('search-button', 'n_clicks'),
     Input('reset-button',  'n_clicks'),
     Input('mass-slider',   'value'),
     Input('year-slider',   'value'),
     Input('map-tabs',      'value'),
     Input('cluster-switch','value'),
     Input('meteor-table',  'active_cell')],
    [State('location-input','value'),
     State('radius-dropdown','value')]
)

def update_map(selected_falls, selected_classes, search_clicks, reset_clicks,
               selected_mass, selected_year, map_type, cluster_switch,
               active_cell, location, radius):
    # Copy the DataFrame
    filtered_df = df.copy()

    # Slider gibt log10(mass+1) zurück → zurückrechnen
    if selected_mass:
        log_min, log_max = selected_mass
        min_mass = 10**log_min - 1
        max_mass = 10**log_max - 1
        filtered_df = filtered_df[(filtered_df['mass'] >= min_mass) &
                                (filtered_df['mass'] <= max_mass)]
    # Filter by meteorite type
    if selected_classes:
        filtered_df = filtered_df[filtered_df["recclass"].isin(selected_classes)]

    # Filter by year range
    if selected_year:
        min_year, max_year = selected_year
        filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['year'] <= max_year)]

    # Filter by fall status (Fall/Found)
    if selected_falls:
        filtered_df = filtered_df[filtered_df["fall"].isin(selected_falls)]

    # Location-based filtering
    center_lat, center_lon = None, None
    zoom_level = 1.5  # Default zoom level
    map_center = dict(lat=20, lon=0)  # Default map center

    # Check if the search button or reset button was clicked
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'search-button.n_clicks':
        if location:
            try:
                # Caching-aware Geocoding
                coords = geocode_location(location)
                if coords:
                    center_lat, center_lon = coords
                    map_center = dict(lat=center_lat, lon=center_lon)
                    zoom_level=5

                    # Filter meteorites based on distance
                    if radius != 'unlimited':
                        radius_km = float(radius)
                        # Dynamischen Zoom basierend auf dem Radius setzen
                        # Kleinere Radien benötigen höheren Zoom
                        if radius_km <= 50:
                            zoom_level = 8
                        elif radius_km <= 100:
                            zoom_level = 7
                        elif radius_km <= 200:
                            zoom_level = 6
                        elif radius_km <= 500:
                            zoom_level = 4
                        else:  # 1000 km und mehr
                            zoom_level = 3
                            
                        # Vektorisierte Distanzberechnung
                        lat1, lon1 = np.radians(center_lat), np.radians(center_lon)
                        lat2, lon2 = np.radians(filtered_df['reclat']), np.radians(filtered_df['reclong'])
                        
                        # Differenzen berechnen
                        dlat = lat2 - lat1
                        dlon = lon2 - lon1
                        
                        # Haversine-Formel
                        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
                        c = 2 * np.arcsin(np.sqrt(a))
                        # Erdradius in Kilometern
                        r = 6371
                        # Distanz in Kilometern
                        filtered_df['distance'] = r * c
                        
                        # Filtern auf Basis der Distanz
                        filtered_df_before = len(filtered_df)
                        filtered_df = filtered_df[filtered_df['distance'] <= radius_km]
                        
                        # Prüfen ob Meteoriten gefunden wurden
                        if len(filtered_df) == 0 and filtered_df_before > 0:
                            empty_fig = px.scatter_mapbox(
                                pd.DataFrame([{'reclat': center_lat, 'reclong': center_lon}]),
                                lat="reclat",
                                lon="reclong",
                                zoom=zoom_level,
                                mapbox_style="carto-positron"
                            )
                            empty_fig.update_layout(height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
                            
                            # Zeige den Suchkreis trotzdem an
                            circle_lats, circle_lons = [], []        
                            for bearing in np.arange(0, 360, 1):
                                point = geodesic(kilometers=radius_km).destination(
                                    (center_lat, center_lon),
                                    bearing
                                )
                                circle_lats.append(point.latitude)
                                circle_lons.append(point.longitude)

                            empty_fig.add_trace(go.Scattermapbox(
                                lat=circle_lats,
                                lon=circle_lons,
                                mode='lines',
                                fill='toself',
                                fillcolor='rgba(255,0,0,0.15)',
                                line=dict(color='red', width=2),
                                name='Suchradius'
                            ))
                            
                            error_message = [
                                html.Div([
                                    html.P(f"Keine Meteoriten im Umkreis von {radius_km} km um {location} gefunden!", 
                                          style={'color': 'red', 'fontWeight': 'bold', 'fontSize': '16px'}),
                                    html.P("Bitte versuche einen größeren Suchradius oder einen anderen Ort.")
                                ], style={'marginTop': '10px', 'padding': '15px', 'backgroundColor': '#ffeeee', 
                                          'border': '1px solid #ff0000', 'borderRadius': '5px'})
                            ]
                            return empty_fig, error_message, []
                    else:
                        # Wenn 'unlimited' ausgewählt wurde, nutze einen mittleren Zoom
                        zoom_level = 5
                        
            except Exception as e:
                print(f"Geocoding error: {e}")

    # Remove the temporary 'distance' column if it exists
    if 'distance' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['distance'])

    # Handle empty results
    if filtered_df.empty:
        empty_fig = px.scatter_mapbox(
            pd.DataFrame(columns=["reclat", "reclong"]),
            lat="reclat",
            lon="reclong",
            zoom=1,
            mapbox_style="carto-positron",
            title="Keine Ergebnisse gefunden"
        )
        empty_fig.update_layout(height=800)
        return empty_fig, html.P("Keine Daten verfügbar für die aktuelle Auswahl.", style={'color': 'red'})

    # Create statistics
    avg_mass = filtered_df['mass'].mean()
    max_mass = filtered_df['mass'].max()
    min_mass = filtered_df['mass'].min()

    # Formatierte Masse für die Statistik nutzen (dieselbe Formatierung wie am Anfang definiert)
    def format_mass(mass):
        if mass < 1000:
            return f"{mass:.2f} g"
        elif mass < 1000000:
            return f"{mass/1000:.2f} kg"
        else:
            return f"{mass/1000000:.2f} t"
    
    stats = [
        html.P(f"Anzahl Meteoriten: {len(filtered_df)}", style={'margin': '5px 0'}),
        html.P(f"Durchschnittliche Masse: {format_mass(avg_mass)}", style={'margin': '5px 0'}),
        html.P(f"Grösste Masse: {format_mass(max_mass)}", style={'margin': '5px 0'}),
        html.P(f"Kleinste Masse: {format_mass(min_mass)}", style={'margin': '5px 0'})
    ]

    # Add year statistics only if valid year values exist
    if not filtered_df['year'].isna().all():
        stats.append(
            html.P(f"Zeitraum: {int(filtered_df['year'].min())} - {int(filtered_df['year'].max())}", style={'margin': '5px 0'})
        )

    # Click-Zoom: falls eine Tabellenzeile aktiv ist
    if active_cell and 'row' in active_cell:
        idx = active_cell['row']
        if 0 <= idx < len(filtered_df):
            sel = filtered_df.iloc[idx]
            map_center = dict(lat=sel['reclat'], lon=sel['reclong'])
            zoom_level = 6

    # Erstelle die richtige Karte basierend auf dem Kartentyp
    if map_type == 'Heatmap':
        fig = px.density_mapbox(
            filtered_df,
            lat="reclat",
            lon="reclong",
            radius=15,  # Radius für die Clusterbildung (in Pixeln)
            opacity=0.8,
            mapbox_style="carto-positron",
            zoom=zoom_level,
            center=map_center,
            color_continuous_scale="Viridis",  # Farbskala für die Dichte
        )
        
    elif map_type == 'Punktekarte':  # Sicherstellen, dass dieser Wert korrekt geprüft wird
        fig = px.scatter_mapbox(
            filtered_df,
            lat="reclat",
            lon="reclong",
            color="year",
            size="size_for_plot",
            size_max=15,
            color_continuous_scale="Viridis",
            hover_name="name",
            hover_data={
                "year": True,
                "formatted_mass": True,
                "recclass": True,
                "fall_de": True,
                "country": True,
                "mass": False,
                "fall": False,
                "size_for_plot": False
            },
            opacity=0.7,
            mapbox_style="carto-positron",
            labels={
                "year": "Fundjahr",
                "formatted_mass": "Masse",
                "recclass": "Meteoritenklasse",
                "fall_de": "Beobachteter Fall",
                "country": "Land"
            }
        )
    else:
        # Fallback für unerwartete Werte
        fig = px.scatter_mapbox(
            pd.DataFrame(columns=["reclat", "reclong"]),
            lat="reclat",
            lon="reclong",
            zoom=1,
            mapbox_style="carto-positron",
            title="Keine Ergebnisse gefunden"
        )

        # Customizing hover template to show friendlier labels with country information
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>" +
                          "Fundjahr: %{customdata[0]}<br>" +
                          "Land: %{customdata[4]}<br>" +
                          "Breitengrad: %{lat}<br>" +
                          "Längengrad: %{lon}<br>" +
                          "Masse: %{customdata[1]}<br>" +
                          "Meteoritenklasse: %{customdata[2]}<br>" +
                          "Beobachteter Fall: %{customdata[3]}<br>",
            marker=dict(sizemode="area")
        )

    # Layout optimization
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=map_center,
            zoom=zoom_level
        )
    )

    # Marker-Clustering nur wenn Switch angehakt
    for trace in fig.data:
        if isinstance(trace, go.Scattermapbox) and trace.mode == 'markers':
            if 'on' in cluster_switch:
                trace.update(cluster=dict(
                    enabled=True,
                    maxzoom=8,
                    step=60,
                    size=20,
                    color='rgb(0, 123, 255)',
                    opacity=0.6
                ))
            else:
                # Clustering komplett aus
                trace.update(cluster=dict(enabled=False))

    # Füge den Suchradius hinzu, wenn ein Ort eingegeben wurde
    if center_lat is not None and center_lon is not None and radius != 'unlimited':
        radius_km = float(radius)

        circle_lats, circle_lons = [], []        
        for bearing in np.arange(0, 360, 1):
            point = geodesic(kilometers=radius_km).destination(
                (center_lat, center_lon),
                bearing
            )
            circle_lats.append(point.latitude)
            circle_lons.append(point.longitude)

        fig.add_trace(go.Scattermapbox(
            lat=circle_lats,
            lon=circle_lons,
            mode='lines',
            fill='toself',
            fillcolor='rgba(255,0,0,0.15)',
            line=dict(color='red', width=2),
            name='Suchradius'
        ))

    table_data = filtered_df[
        ['name', 'year', 'formatted_mass', 'recclass', 'country']
    ].to_dict('records')

    return fig, stats, table_data 

@app.callback(
    [Output('mass-slider', 'value'),
     Output('min-mass-input', 'value'),
     Output('max-mass-input', 'value'),
     Output('mass-slider-display', 'children')],
    [Input('mass-slider', 'value'),
     Input('min-mass-input', 'value'),
     Input('max-mass-input', 'value')]
)
def sync_mass_inputs(slider_value, min_mass, max_mass):
    ctx = dash.callback_context
    if not ctx.triggered:
        label = f"{int(10**slider_value[0]-1):,} g – " \
                f"{int(10**slider_value[1]-1):,} g"
        return slider_value, 10**slider_value[0]-1, 10**slider_value[1]-1, label

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'mass-slider':
        min_m = 10**slider_value[0] - 1
        max_m = 10**slider_value[1] - 1
        label = f"{int(min_m):,} g – {int(max_m):,} g"
        return slider_value, min_m, max_m, label

    elif trigger == 'min-mass-input':
        min_mass = min(min_mass, max_mass)
        label = f"{int(min_mass):,} g – {int(max_mass):,} g"
        return [np.log10(min_mass + 1), np.log10(max_mass + 1)], \
               min_mass, max_mass, label

    elif trigger == 'max-mass-input':
        max_mass = max(max_mass, min_mass)
        label = f"{int(min_mass):,} g – {int(max_mass):,} g"
        return [np.log10(min_mass + 1), np.log10(max_mass + 1)], \
               min_mass, max_mass, label

    # Fallback
    label = f"{int(10**slider_value[0])} g – {int(10**slider_value[1]):,} g"
    return slider_value, 10**slider_value[0], 10**slider_value[1], label

@app.callback(
    [Output('year-slider', 'value'),
     Output('min-year-input', 'value'),
     Output('max-year-input', 'value'),
     Output('year-slider-display', 'children')],
    [Input('year-slider', 'value'),
     Input('min-year-input', 'value'),
     Input('max-year-input', 'value')]
)
def sync_year_inputs(slider_value, min_year, max_year):
    # Wenn der Slider geändert wird, aktualisiere die Eingabefelder
    ctx = dash.callback_context
    if not ctx.triggered:
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'year-slider':
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label
    elif trigger_id == 'min-year-input':
        label = f"{int(min_year)} – {int(max_year)}"
        min_year = min(min_year, max_year)
        return [min_year, max_year], min_year, max_year, label
    elif trigger_id == 'max-year-input':
        label = f"{int(min_year)} – {int(max_year)}"
        max_year = max(max_year, min_year)
        return [min_year, max_year], min_year, max_year, label

    # Fallback
    label = f"{int(slider_value[0])} – {int(slider_value[1])}"
    
    return slider_value, slider_value[0], slider_value[1], label

if __name__ == '__main__':
    app.run(debug=True)