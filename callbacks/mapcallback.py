# callbacks/map_callbacks.py
import dash
from dash import html, dcc, Input, Output, State, dash_table, no_update, callback_context
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from utils.geocoding import geocode_location
from utils.formatting import format_mass, format_mass_int

def register_map_callbacks(app, df: pd.DataFrame):
    @app.callback(
        [Output('meteor-map', 'figure'),
        Output('country-diagram-graph', 'figure'), # Output für Länder-Diagramm
        Output('class-diagram-graph', 'figure'),   # Output für Klassen-Diagramm
        Output('meteor-table', 'data'),
        Output('map-and-table-container', 'style'), # Output für Sichtbarkeit des Karten-Containers
        Output('diagram-container', 'style'),       # Output für Sichtbarkeit des Diagramm-Containers
        Output('map-type', 'data'), # Output für den Kartentyp
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
        State('radius-dropdown', 'value'),
        State('map-type', 'data')]  # State für den Kartentyp
    )
    def update_content(selected_falls, selected_classes, search_clicks, reset_clicks,
                    selected_mass, selected_year,
                    clu_clicks, pun_clicks, hea_clicks, dia_clicks,
                    active_cell, # active_cell hier als Input
                    location, radius, map_type):

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
                                return empty_fig, go.Figure(), go.Figure(), no_update, map_and_table_container_style,{'display':'none'},new_view, stats
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
            return empty_fig, go.Figure(), go.Figure(), no_update, map_and_table_container_style,{'display':'none'},new_view, stats

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
        triggered_id = callback_context.triggered_id

        if triggered_id in ['nav-clu','nav-pun','nav-hea','nav-dia']:
            # Nutzer hat die Karte gewechselt → neuen View in Store schreiben
            button_id = triggered_id
            new_view = triggered_id
        else:
            # Filter, Search, Reset, Table-Click → View bleibt, was im Store stand
            new_view = map_type
            button_id = map_type


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
                map_and_table_container_style, diagram_container_style, new_view, stats

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
                    size_max=10,
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
                    size_max=10,
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
                map_and_table_container_style, diagram_container_style, new_view, stats,
