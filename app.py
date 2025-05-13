import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# --- Datenvorbereitung ---
df = pd.read_csv("data/meteorite-landings.csv")

# Entferne Zeilen ohne Koordinaten oder mit fehlender Masse
df = df.dropna(subset=['reclat', 'reclong', 'mass', 'year'])

# Entferne ungültige Einträge und konvertiere Jahr in Integer
df = df[(df['year'] <= 2025) & (df['year'] >= 1000)]
df['year'] = df['year'].astype(int)

# Stelle sicher, dass alle Massen positiv sind
df['mass'] = df['mass'].abs()

# Verbesserte Punktgröße - logarithmische Skala für bessere Sichtbarkeit der Unterschiede
df['size_for_plot'] = np.log10(df['mass'] + 1) * 3
df['size_for_plot'] = df['size_for_plot'].clip(lower=0.1, upper=15).fillna(0.1)

# Index zurücksetzen
df = df.reset_index(drop=True)

# Initialisiere den Geocoder
geolocator = Nominatim(user_agent="impact-atlas")

# --- App-Initialisierung ---
app = dash.Dash(__name__)
app.title = "Impact Atlas"

# --- Layout der App ---
app.layout = html.Div([
    html.H1("Impact Atlas – Meteoriten weltweit", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    html.Div(id="main-container", children=[
        
        # Kartenbereich
        html.Div([
            dcc.Graph(id='meteor-map', config={"scrollZoom": True}, style={'height': '85vh'})
        ], style={'flex': '75%', 'padding': '10px'}),

        # Steuerungsbereich
        html.Div([
            html.H4("Karte:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Dropdown(
                options=['Punktekarte','Heatmap'],
                value='Punktekarte',
                multi=False,
                id="map-filter",
                ),
            # Masse-Filter
            html.H4("Masse in Gramm:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.RangeSlider(
                id='mass-slider',
                min=df['mass'].min(),
                max=df['mass'].max(),
                value=[df['mass'].min(), df['mass'].max()],
                marks={int(i): f'{int(i)}' for i in np.linspace(df['mass'].min(), df['mass'].max(), 5)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='drag'
            ),
            html.Br(),
            html.Div([
                html.Label("Minimale Masse:", style={'margin': '10px'}),
                dcc.Input(
                    id='min-mass-input',
                    type='number',
                    value=df['mass'].min(),
                    style={'width': '45%', 'marginRight': '5%'}
                ),
                html.Label("Maximale Masse:", style={'margin': '10px'}),
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
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=[df['year'].min(), df['year'].max()],
                marks={int(i): f'{int(i)}' for i in np.linspace(df['year'].min(), df['year'].max(), 5)},
                tooltip={"placement": "bottom", "always_visible": True},
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
                options=[{"label": i, "value": i} for i in df["fall"].unique()],
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
    [Output('meteor-map', 'figure'),
     Output('stats-container', 'children')],
    [Input('fall-filter', 'value'),
     Input('class-filter', 'value'),
     Input('search-button', 'n_clicks'),
     Input('reset-button', 'n_clicks'),
     Input('mass-slider', 'value'),
     Input('year-slider', 'value')],
    [State('location-input', 'value'),
     State('radius-dropdown', 'value')]
)
def update_map(selected_falls, selected_classes, search_clicks, reset_clicks, selected_mass, selected_year, location, radius):
    # Copy the DataFrame
    filtered_df = df.copy()

    # Filter by mass range
    if selected_mass:
        min_mass, max_mass = selected_mass
        filtered_df = filtered_df[(filtered_df['mass'] >= min_mass) & (filtered_df['mass'] <= max_mass)]

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
                # Geocode the location
                location_info = geolocator.geocode(location)
                if location_info:
                    center_lat, center_lon = location_info.latitude, location_info.longitude
                    map_center = dict(lat=center_lat, lon=center_lon)
                    zoom_level = 5  # Adjust zoom level

                    # Filter meteorites based on distance
                    if radius != 'unlimited':
                        radius_km = float(radius)
                        filtered_df['distance'] = filtered_df.apply(
                            lambda row: geodesic((center_lat, center_lon), (row['reclat'], row['reclong'])).kilometers,
                            axis=1
                        )
                        filtered_df = filtered_df[filtered_df['distance'] <= radius_km]
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
    stats = [
        html.P(f"Anzahl Meteoriten: {len(filtered_df)}", style={'margin': '5px 0'}),
        html.P(f"Durchschnittliche Masse: {filtered_df['mass'].mean():.2f} g", style={'margin': '5px 0'}),
        html.P(f"Grösste Masse: {filtered_df['mass'].max():.2f} g", style={'margin': '5px 0'}),
        html.P(f"Kleinste Masse: {filtered_df['mass'].min():.2f} g", style={'margin': '5px 0'})
    ]

    # Add year statistics only if valid year values exist
    if not filtered_df['year'].isna().all():
        stats.append(
            html.P(f"Zeitraum: {int(filtered_df['year'].min())} - {int(filtered_df['year'].max())}", style={'margin': '5px 0'})
        )

    # Create the map with filtered data
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
            "mass": ':.2f',
            "recclass": True,
            "fall": True,
            "size_for_plot": False
        },
        opacity=0.7,
        mapbox_style="carto-positron"
    )

    fig.update_traces(marker=dict(sizemode="area"))

    # Layout optimization
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=map_center,
            zoom=zoom_level
        ),
        coloraxis_colorbar=dict(
            title="Jahr",
            thicknessmode="pixels",
            thickness=20,
            len=0.6,
            yanchor="middle",
            y=0.5
        ),
    )

    return fig, stats

@app.callback(
    [Output('mass-slider', 'value'),
     Output('min-mass-input', 'value'),
     Output('max-mass-input', 'value')],
    [Input('mass-slider', 'value'),
     Input('min-mass-input', 'value'),
     Input('max-mass-input', 'value')]
)
def sync_mass_inputs(slider_value, min_mass, max_mass):
    # Wenn der Slider geändert wird, aktualisiere die Eingabefelder
    ctx = dash.callback_context
    if not ctx.triggered:
        return slider_value, slider_value[0], slider_value[1]

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'mass-slider':
        return slider_value, slider_value[0], slider_value[1]
    elif trigger_id == 'min-mass-input':
        # Stelle sicher, dass der minimale Wert nicht größer als der maximale ist
        min_mass = min(min_mass, max_mass)
        return [min_mass, max_mass], min_mass, max_mass
    elif trigger_id == 'max-mass-input':
        # Stelle sicher, dass der maximale Wert nicht kleiner als der minimale ist
        max_mass = max(max_mass, min_mass)
        return [min_mass, max_mass], min_mass, max_mass

    return slider_value, slider_value[0], slider_value[1]

@app.callback(
    [Output('year-slider', 'value'),
     Output('min-year-input', 'value'),
     Output('max-year-input', 'value')],
    [Input('year-slider', 'value'),
     Input('min-year-input', 'value'),
     Input('max-year-input', 'value')]
)
def sync_year_inputs(slider_value, min_year, max_year):
    # Wenn der Slider geändert wird, aktualisiere die Eingabefelder
    ctx = dash.callback_context
    if not ctx.triggered:
        return slider_value, slider_value[0], slider_value[1]

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'year-slider':
        return slider_value, slider_value[0], slider_value[1]
    elif trigger_id == 'min-year-input':
        # Stelle sicher, dass der minimale Wert nicht größer als der maximale ist
        min_year = min(min_year, max_year)
        return [min_year, max_year], min_year, max_year
    elif trigger_id == 'max-year-input':
        # Stelle sicher, dass der maximale Wert nicht kleiner als der minimale ist
        max_year = max(max_year, min_year)
        return [min_year, max_year], min_year, max_year

    return slider_value, slider_value[0], slider_value[1]

if __name__ == '__main__':
    app.run(debug=True)