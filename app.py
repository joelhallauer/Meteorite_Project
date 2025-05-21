import dash
from dash import html, dcc, Input, Output, State, dash_table, no_update
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

    # Neue Navigationsleiste
    html.Div([
        html.Button(
            "Cluster Karte",
            id='nav-clu',
            className='nav-button',
            n_clicks=1,  # Set an initial click to make this the default
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Punktekarte",
            id='nav-pun',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#2196F3',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Heatmap",
            id='nav-hea',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#ff9800',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Diagramm",
            id='nav-dia',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#9c27b0',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'marginBottom': '20px',
        'gap': '10px',
        'padding': '0 20px'
    }),

    html.Div(id="main-container", children=[

        # Kartenbereich und Tabelle
        html.Div(id="map-and-table-container", children=[
            dcc.Graph(id='meteor-map', config={"scrollZoom": True},
                    style={'height': '50vh'}),

            dash_table.DataTable(
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
                    'tableLayout': 'fixed',
                },
                style_cell={
                    'fontFamily': 'Arial',
                    'fontSize': '12px',
                    'padding': '3px',
                    'textAlign': 'left',
                    'width': '20%',
                    'minWidth': '20%',
                    'maxWidth': '20%',
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
            ),
        ], style={ # Standard-Style: sichtbar, wenn App geladen wird
            'flex': '75%', 'padding': '10px',
            'display': 'flex', 'flexDirection': 'column'
        }),

        # Bereich für die Diagramme (initially hidden)
        html.Div(id="diagram-container", children=[
            html.H3("Meteoritenfunde pro Land", style={'textAlign': 'center', 'marginTop': '10px'}),
            dcc.Graph(id='country-diagram-graph', config={"scrollZoom": True},
                      style={'height': '40vh', 'width': '100%', 'marginBottom': '20px'}), # Etwas kleiner

            html.H3("Meteoritenfunde pro Meteoritenklasse", style={'textAlign': 'center', 'marginTop': '10px'}),
            dcc.Graph(id='class-diagram-graph', config={"scrollZoom": True},
                      style={'height': '40vh', 'width': '100%'})
        ], style={ # Standard-Style: versteckt
            'flex': '75%', 'padding': '10px',
            'display': 'none', 'flexDirection': 'column'
        }),


        # Steuerungsbereich
        html.Div([
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
    return no_update

# Add client-side callback for default map on app load
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            // Trigger initial click on the nav-clu button
            return 1;
        }
        return undefined;
    }
    """,
    Output('nav-clu', 'n_clicks'),
    [Input('app-container', 'children')]
)

@app.callback(
    [Output('meteor-map', 'figure'),
     Output('country-diagram-graph', 'figure'), # Output für Länder-Diagramm
     Output('class-diagram-graph', 'figure'),   # Output für Klassen-Diagramm
     Output('meteor-table', 'data'),
     Output('map-and-table-container', 'style'), # Output für Sichtbarkeit des Karten-Containers
     Output('diagram-container', 'style'),       # Output für Sichtbarkeit des Diagramm-Containers
     Output('stats-container', 'children')],
    [Input('fall-filter', 'value'),
     Input('class-filter', 'value'),
     Input('search-button', 'n_clicks'),
     Input('reset-button', 'n_clicks'),
     Input('mass-slider', 'value'),
     Input('year-slider', 'value'),
     Input('nav-clu', 'n_clicks'),
     Input('nav-pun', 'n_clicks'),
     Input('nav-hea', 'n_clicks'),
     Input('nav-dia', 'n_clicks'),
     Input('meteor-table', 'active_cell')], # active_cell als Input
    [State('location-input', 'value'),
     State('radius-dropdown', 'value')]
)
def update_content(selected_falls, selected_classes, search_clicks, reset_clicks,
                   selected_mass, selected_year,
                   clu_clicks, pun_clicks, hea_clicks, dia_clicks,
                   active_cell, # active_cell hier als Input
                   location, radius):

    # Copy the DataFrame
    filtered_df = df.copy()

    # --- FILTERING LOGIC (unverändert) ---
    if selected_mass:
        log_min, log_max = selected_mass
        min_mass = 10**log_min - 1
        max_mass = 10**log_max - 1
        filtered_df = filtered_df[(filtered_df['mass'] >= min_mass) &
                                (filtered_df['mass'] <= max_mass)]
    if selected_classes:
        filtered_df = filtered_df[filtered_df["recclass"].isin(selected_classes)]
    if selected_year:
        min_year, max_year = selected_year
        filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['year'] <= max_year)]
    if selected_falls:
        filtered_df = filtered_df[filtered_df["fall"].isin(selected_falls)]

    center_lat, center_lon = None, None
    zoom_level = 1.5
    map_center = dict(lat=20, lon=0)

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'search-button.n_clicks':
        if location:
            try:
                coords = geocode_location(location)
                if coords:
                    center_lat, center_lon = coords
                    map_center = dict(lat=center_lat, lon=center_lon)
                    zoom_level=5
                    if radius != 'unlimited':
                        radius_km = float(radius)
                        if radius_km <= 50:
                            zoom_level = 8
                        elif radius_km <= 100:
                            zoom_level = 7
                        elif radius_km <= 200:
                            zoom_level = 6
                        elif radius_km <= 500:
                            zoom_level = 4
                        else:
                            zoom_level = 3

                        lat1, lon1 = np.radians(center_lat), np.radians(center_lon)
                        lat2, lon2 = np.radians(filtered_df['reclat']), np.radians(filtered_df['reclong'])

                        dlat = lat2 - lat1
                        dlon = lon2 - lon1

                        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
                        c = 2 * np.arcsin(np.sqrt(a))
                        r = 6371
                        filtered_df['distance'] = r * c

                        filtered_df_before = len(filtered_df)
                        filtered_df = filtered_df[filtered_df['distance'] <= radius_km]

                        if len(filtered_df) == 0 and filtered_df_before > 0:
                            empty_fig = px.scatter_mapbox(
                                pd.DataFrame([{'reclat': center_lat, 'reclong': center_lon}]),
                                lat="reclat",
                                lon="reclong",
                                zoom=zoom_level,
                                mapbox_style="carto-positron"
                            )
                            empty_fig.update_layout(height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
                            circle_lats, circle_lons = [], []
                            for bearing in np.arange(0, 360, 1):
                                point = geodesic(kilometers=radius_km).destination(
                                    (center_lat, center_lon), bearing
                                )
                                circle_lats.append(point.latitude)
                                circle_lons.append(point.longitude)
                            empty_fig.add_trace(go.Scattermapbox(
                                lat=circle_lats, lon=circle_lons, mode='lines', fill='toself',
                                fillcolor='rgba(255,0,0,0.15)', line=dict(color='red', width=2), name='Suchradius'
                            ))
                            error_message = html.Div([
                                html.P(f"Keine Meteoriten im Umkreis von {radius_km} km um {location} gefunden!",
                                          style={'color': 'red', 'fontWeight': 'bold', 'fontSize': '16px'}),
                                html.P("Bitte versuche einen größeren Suchradius oder einen anderen Ort.")
                            ], style={'marginTop': '10px', 'padding': '15px', 'backgroundColor': '#ffeeee',
                                          'border': '1px solid #ff0000', 'borderRadius': '5px'})
                            # Bei Fehlermeldung: Karte sichtbar, Diagramme unsichtbar
                            return empty_fig, go.Figure(), go.Figure(), no_update, \
                                {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
                                {'display': 'none'}, \
                                error_message
            except Exception as e:
                print(f"Geocoding error: {e}")

    if 'distance' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['distance'])

    # Handle empty results (for all views)
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
        error_message = html.P("Keine Daten verfügbar für die aktuelle Auswahl.", style={'color': 'red'})
        # Bei leeren Ergebnissen: Karte sichtbar, Diagramme unsichtbar
        return empty_fig, go.Figure(), go.Figure(), no_update, \
            {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
            {'display': 'none'}, \
            error_message

    # Create statistics
    avg_mass = filtered_df['mass'].mean()
    max_mass = filtered_df['mass'].max()
    min_mass = filtered_df['mass'].min()
    stats = [
        html.P(f"Anzahl Meteoriten: {len(filtered_df)}", style={'margin': '5px 0'}),
        html.P(f"Durchschnittliche Masse: {format_mass(avg_mass)}", style={'margin': '5px 0'}),
        html.P(f"Grösste Masse: {format_mass(max_mass)}", style={'margin': '5px 0'}),
        html.P(f"Kleinste Masse: {format_mass(min_mass)}", style={'margin': '5px 0'})
    ]
    if not filtered_df['year'].isna().all():
        stats.append(
            html.P(f"Zeitraum: {int(filtered_df['year'].min())} - {int(filtered_df['year'].max())}", style={'margin': '5px 0'})
        )

    # Determine which view to show
    ctx1 = dash.callback_context
    if not ctx1.triggered:
        button_id = "nav-clu"
    else:
        button_id = ctx1.triggered[0]['prop_id'].split('.')[0]
        if button_id not in ['nav-clu', 'nav-pun', 'nav-hea', 'nav-dia']:
            button_ids = ['nav-clu', 'nav-pun', 'nav-hea', 'nav-dia']
            clicks = [clu_clicks or 0, pun_clicks or 0, hea_clicks or 0, dia_clicks or 0]
            if any(clicks):
                max_clicks_idx = clicks.index(max(clicks))
                button_id = button_ids[max_clicks_idx]
            else:
                button_id = "nav-clu"


    # Initialisiere die Figuren
    map_fig = go.Figure()
    country_diagram_fig = go.Figure()
    class_diagram_fig = go.Figure()

    # Bestimme die anzuzeigenden Container-Styles
    map_and_table_container_style = {} # Wird unten überschrieben
    diagram_container_style = {}       # Wird unten überschrieben


    # Erstelle die richtige Karte/Diagramm basierend auf dem Kartentyp
    if button_id == 'nav-dia':
        map_and_table_container_style = {'display': 'none'} # Karte und Tabelle verstecken
        diagram_container_style = {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'} # Diagramme anzeigen

        # Diagramm für Länder
        country_counts = filtered_df.groupby('country').size().reset_index(name='count')
        country_counts = country_counts.sort_values('count', ascending=False)
        # Optional: Limitiere auf Top N Länder
        if len(country_counts) > 20: # Beispiel: Top 20 Länder
            country_counts = country_counts.head(20)
            country_title = "Top 20 Länder nach Meteoritenfunden"
        else:
            country_title = "Länder nach Meteoritenfunden"


        country_diagram_fig = px.bar(
            country_counts,
            x="country",
            y="count",
            title=country_title,
            labels={
                "country": "Land",
                "count": "Anzahl der Meteoriten"
            },
            color_discrete_sequence=["#9c27b0"]
        )
        country_diagram_fig.update_layout(
            xaxis=dict(tickangle=-45),
            height=400, # Angepasste Höhe für zwei Diagramme
            margin={"r": 20, "t": 50, "l": 20, "b": 100}
        )

        # Diagramm für Klassen
        class_counts = filtered_df.groupby('recclass').size().reset_index(name='count')
        class_counts = class_counts.sort_values('count', ascending=False)
        # Optional: Limitiere auf Top N Klassen
        if len(class_counts) > 20: # Beispiel: Top 20 Klassen
            class_counts = class_counts.head(20)
            class_title = "Top 20 Meteoritenklassen nach Funden"
        else:
            class_title = "Meteoritenklassen nach Funden"

        class_diagram_fig = px.bar(
            class_counts,
            x="recclass",
            y="count",
            title=class_title,
            labels={
                "recclass": "Meteoritenklasse",
                "count": "Anzahl der Meteoriten"
            },
            color_discrete_sequence=["#9c27b0"]
        )
        class_diagram_fig.update_layout(
            xaxis=dict(tickangle=-45),
            height=400, # Angepasste Höhe für zwei Diagramme
            margin={"r": 20, "t": 50, "l": 20, "b": 100}
        )

        # Rückgabe für den Diagramm-Modus
        # meteor-map bekommt eine leere Figur, meteor-table.data no_update
        return go.Figure(), country_diagram_fig, class_diagram_fig, no_update, \
            map_and_table_container_style, diagram_container_style, stats

    else: # Für Karten-Modi (nav-clu, nav-pun, nav-hea)
        map_and_table_container_style = {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'} # Karte und Tabelle anzeigen
        diagram_container_style = {'display': 'none'} # Diagramme verstecken

        # Click-Zoom: falls eine Tabellenzeile aktiv ist (nur für Karten)
        if active_cell and 'row' in active_cell:
            idx = active_cell['row']
            if 0 <= idx < len(filtered_df):
                sel = filtered_df.iloc[idx]
                map_center = dict(lat=sel['reclat'], lon=sel['reclong'])
                zoom_level = 6

        if button_id == 'nav-clu':
            map_fig = px.scatter_mapbox(
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
                    "year": "Fundjahr"
                }
            )
            for trace in map_fig.data:
                if isinstance(trace, go.Scattermapbox):
                    trace.update(cluster=dict(
                        enabled=True, maxzoom=8, step=60, size=20,
                        color='rgb(0, 123, 255)', opacity=0.6
                    ))
            map_fig.update_traces(
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
        elif button_id == 'nav-pun':
            map_fig = px.scatter_mapbox(
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
                    "year": "Fundjahr"
                }
            )
            map_fig.update_traces(
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
        elif button_id == 'nav-hea':
            map_fig = px.density_mapbox(
                filtered_df,
                lat="reclat",
                lon="reclong",
                radius=15,
                opacity=0.8,
                mapbox_style="carto-positron",
                zoom=zoom_level,
                center=map_center,
                color_continuous_scale="Viridis",
            )

        # Layout optimization for map_fig
        map_fig.update_layout(
            height=600,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox=dict(
                center=map_center,
                zoom=zoom_level
            )
        )

        # Add search radius to map_fig if applicable
        if center_lat is not None and center_lon is not None and radius != 'unlimited':
            radius_km = float(radius)
            circle_lats, circle_lons = [], []
            for bearing in np.arange(0, 360, 1):
                point = geodesic(kilometers=radius_km).destination((center_lat, center_lon), bearing)
                circle_lats.append(point.latitude)
                circle_lons.append(point.longitude)
            map_fig.add_trace(go.Scattermapbox(
                lat=circle_lats, lon=circle_lons, mode='lines', fill='toself',
                fillcolor='rgba(255,0,0,0.15)', line=dict(color='red', width=2), name='Suchradius'
            ))

        table_data = filtered_df[['name', 'year', 'formatted_mass', 'recclass', 'country']].to_dict('records')

        # Rückgabe für den Karten-Modus
        # country-diagram-graph und class-diagram-graph bekommen leere Figuren
        return map_fig, go.Figure(), go.Figure(), table_data, \
            map_and_table_container_style, diagram_container_style, stats


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
        current_max_mass = max_mass if max_mass is not None else df['mass'].max()
        min_mass = min(min_mass, current_max_mass)
        label = f"{int(min_mass):,} g – {int(current_max_mass):,} g"
        return [np.log10(min_mass + 1), np.log10(current_max_mass + 1)], \
               min_mass, current_max_mass, label

    elif trigger == 'max-mass-input':
        current_min_mass = min_mass if min_mass is not None else df['mass'].min()
        max_mass = max(max_mass, current_min_mass)
        label = f"{int(current_min_mass):,} g – {int(max_mass):,} g"
        return [np.log10(current_min_mass + 1), np.log10(max_mass + 1)], \
               current_min_mass, max_mass, label

    label = f"{int(10**slider_value[0]-1):,} g – {int(10**slider_value[1]-1):,} g"
    return slider_value, 10**slider_value[0]-1, 10**slider_value[1]-1, label

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
    ctx = dash.callback_context
    if not ctx.triggered:
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'year-slider':
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label
    elif trigger_id == 'min-year-input':
        current_max_year = max_year if max_year is not None else df['year'].max()
        min_year = min(min_year, current_max_year)
        label = f"{int(min_year)} – {int(current_max_year)}"
        return [min_year, current_max_year], min_year, current_max_year, label
    elif trigger_id == 'max-year-input':
        current_min_year = min_year if min_year is not None else df['year'].min()
        max_year = max(max_year, current_min_year)
        label = f"{int(current_min_year)} – {int(max_year)}"
        return [current_min_year, max_year], current_min_year, max_year, label

    label = f"{int(slider_value[0])} – {int(slider_value[1])}"

    return slider_value, slider_value[0], slider_value[1], label


if __name__ == '__main__':
    app.run(debug=True)