import dash
from dash import Input, Output, State, no_update
import plotly.graph_objects as go
import pandas as pd
import numpy as np

app = dash.Dash(__name__)
app.title = "Impact Atlas"

# Cache initialisieren
from src.utils import init_cache
init_cache(app.server)

# Komponenten und Utilities importieren
from src.components import create_layout
from src.utils import (
    df, format_mass_int, get_cache, geocode_location,
    filter_dataframe, get_stats, calculate_zoom_level, get_circle_coords
)
from src.visualizations import (
    create_empty_map_figure, create_cluster_map, create_point_map,
    create_heatmap, create_country_bar_chart, create_class_bar_chart
)

app.layout = create_layout()

# --- Callbacks ---

@app.callback(
    [Output('location-input', 'value'),
     Output('radius-dropdown', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def reset_location_inputs(n_clicks):
    """Setzt die Eingabefelder für Ort und Radius zurück."""
    if n_clicks and n_clicks > 0:
        return '', 'unlimited'
    return no_update, no_update

@app.callback(
    [Output('meteor-map', 'figure'),
     Output('country-diagram-graph', 'figure'),
     Output('class-diagram-graph', 'figure'),
     Output('meteor-table', 'data'),
     Output('map-and-table-container', 'style'),
     Output('diagram-container', 'style'),
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
     Input('meteor-table', 'active_cell')],
    [State('location-input', 'value'),
     State('radius-dropdown', 'value')]
)
def update_content(selected_falls, selected_classes, search_clicks, reset_clicks,
                   selected_mass, selected_year,
                   clu_clicks, pun_clicks, hea_clicks, dia_clicks,
                   active_cell,
                   location, radius):
    """
    Diese Haupt-Callback-Funktion aktualisiert den gesamten Inhalt der App
    (Karte, Diagramme, Tabelle, Statistiken) basierend auf Filterauswahlen und Navigation.
    """
    map_center = dict(lat=20, lon=0)
    zoom_level = 1.5
    center_lat, center_lon = None, None

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Aktiven Modus (Karten-/Diagrammtyp) bestimmen
    active_mode = 'nav-clu' # Standardmäßig Cluster-Karte
    if triggered_id in ['nav-clu', 'nav-pun', 'nav-hea', 'nav-dia']:
        active_mode = triggered_id
    else:
        button_clicks = {
            'nav-clu': clu_clicks or 0, 'nav-pun': pun_clicks or 0,
            'nav-hea': hea_clicks or 0, 'nav-dia': dia_clicks or 0
        }
        if all(click == 0 for click in button_clicks.values()):
            active_mode = 'nav-clu'
        else:
            max_clicks = max(button_clicks.values())
            for mode in ['nav-clu', 'nav-pun', 'nav-hea', 'nav-dia']:
                if button_clicks[mode] == max_clicks:
                    active_mode = mode
                    break

    location_triggered = False
    if triggered_id == 'search-button':
        # Ortssuche durchführen, wenn der Suchbutton geklickt wurde
        if location:
            try:
                coords = geocode_location(location)
                if coords:
                    center_lat, center_lon = coords
                    map_center = dict(lat=center_lat, lon=center_lon)
                    zoom_level = calculate_zoom_level(radius)
                    location_triggered = True
                else:
                    # Fehlermeldung bei nicht gefundenem Ort
                    return create_empty_map_figure(), go.Figure(), go.Figure(), [], \
                        {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
                        {'display': 'none'}, \
                        dash.html.Div([
                            dash.html.P(f"Ort '{location}' konnte nicht gefunden werden.",
                                          style={'color': 'red'}),
                            dash.html.P("Bitte überprüfen Sie die Schreibweise oder versuchen Sie einen anderen Ort.")
                        ])
            except Exception as e:
                # Fehlermeldung bei Geocoding-Fehler
                print(f"Geocoding error: {e}")
                return create_empty_map_figure(), go.Figure(), go.Figure(), [], \
                    {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
                    {'display': 'none'}, \
                    dash.html.Div([
                        dash.html.P(f"Ein Fehler ist bei der Ortssuche aufgetreten: {e}",
                                      style={'color': 'red'}),
                        dash.html.P("Bitte versuchen Sie es später erneut.")
                    ])
    elif location and triggered_id != 'reset-button':
        # Vorhandene Ortssuche beibehalten
        try:
            coords = geocode_location(location)
            if coords:
                center_lat, center_lon = coords
                map_center = dict(lat=center_lat, lon=center_lon)
                zoom_level = calculate_zoom_level(radius)
                location_triggered = True
        except Exception as e:
            print(f"Geocoding error during view change: {e}")
    elif triggered_id == 'reset-button':
        # Filter zurücksetzen
        center_lat, center_lon = None, None
        radius = 'unlimited'
        zoom_level = 1.5
        map_center = dict(lat=20, lon=0)

    # DataFrame filtern
    filtered_df = filter_dataframe(
        df, selected_mass, selected_classes, selected_year, selected_falls,
        (center_lat, center_lon) if center_lat is not None else None,
        radius
    )

    if filtered_df.empty:
        # Fehlermeldung bei leeren Daten nach Filterung
        if location_triggered and center_lat is not None and radius != 'unlimited':
            error_message = dash.html.Div([
                dash.html.P(f"Keine Meteoriten im Umkreis von {radius} km um {location} gefunden!",
                              style={'color': 'red'}),
                dash.html.P("Bitte versuche einen größeren Suchradius oder einen anderen Ort.")
            ])
            empty_fig_with_radius = create_empty_map_figure(center_lat, center_lon, calculate_zoom_level(radius))
            circle_lats, circle_lons = get_circle_coords(center_lat, center_lon, float(radius))
            empty_fig_with_radius.add_trace(go.Scattermapbox(
                lat=circle_lats, lon=circle_lons, mode='lines', fill='toself',
                fillcolor='rgba(255,0,0,0.15)', line=dict(color='red', width=2), name='Suchradius'
            ))
            return empty_fig_with_radius, go.Figure(), go.Figure(), [], \
                {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
                {'display': 'none'}, \
                error_message
        else:
            error_message = dash.html.P("Keine Daten verfügbar für die aktuelle Auswahl.", style={'color': 'red'})
            return create_empty_map_figure(), go.Figure(), go.Figure(), [], \
                {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}, \
                {'display': 'none'}, \
                error_message

    stats = get_stats(filtered_df)

    # Kartenmittelpunkt basierend auf Tabellenzellenauswahl anpassen
    if active_cell and 'row' in active_cell and active_mode != 'nav-dia':
        idx = active_cell['row']
        if 0 <= idx < len(filtered_df):
            sel = filtered_df.iloc[idx]
            map_center = dict(lat=sel['reclat'], lon=sel['reclong'])
            zoom_level = 6

    # Ansicht basierend auf dem aktiven Modus umschalten (Diagramme oder Karte/Tabelle)
    if active_mode == 'nav-dia':
        # Diagramm-Ansicht
        map_and_table_container_style = {'display': 'none'}
        diagram_container_style = {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}
        country_diagram_fig = create_country_bar_chart(filtered_df)
        class_diagram_fig = create_class_bar_chart(filtered_df)
        return go.Figure(), country_diagram_fig, class_diagram_fig, [], \
            map_and_table_container_style, diagram_container_style, stats
    else:
        # Karten- und Tabellenansicht
        map_and_table_container_style = {'flex': '75%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}
        diagram_container_style = {'display': 'none'}
        map_fig = go.Figure()
        if active_mode == 'nav-clu':
            map_fig = create_cluster_map(filtered_df, map_center, zoom_level, center_lat, center_lon, radius)
        elif active_mode == 'nav-pun':
            map_fig = create_point_map(filtered_df, map_center, zoom_level, center_lat, center_lon, radius)
        elif active_mode == 'nav-hea':
            map_fig = create_heatmap(filtered_df, map_center, zoom_level, center_lat, center_lon, radius)
        else:
            map_fig = create_cluster_map(filtered_df, map_center, zoom_level, center_lat, center_lon, radius)

        table_data = filtered_df[['name', 'year', 'formatted_mass', 'recclass', 'country']].to_dict('records')
        return map_fig, go.Figure(), go.Figure(), table_data, \
            map_and_table_container_style, diagram_container_style, stats

@app.callback(
    [Output('mass-slider', 'value'),
     Output('min-mass-input', 'value'),
     Output('max-mass-input', 'value'),
     Output('mass-slider-display', 'children')],
    [Input('mass-slider', 'value'),
     Input('min-mass-input', 'value'),
     Input('max-mass-input', 'value')],
    [State('mass-slider', 'min'), State('mass-slider', 'max')]
)
def sync_mass_inputs(slider_value, min_mass_input, max_mass_input, slider_min_log, slider_max_log):
    """Synchronisiert den Massen-Range-Slider mit den Min/Max-Eingabefeldern."""
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'initial_load'

    if trigger_id == 'mass-slider':
        current_min_mass = 10**slider_value[0] - 1
        current_max_mass = 10**slider_value[1] - 1
        return slider_value, current_min_mass, current_max_mass, \
               f"{format_mass_int(current_min_mass)} – {format_mass_int(current_max_mass)}"
    elif trigger_id == 'min-mass-input':
        if min_mass_input is None: min_mass_input = df['mass'].min()
        current_max_mass_val = max_mass_input if max_mass_input is not None else df['mass'].max()
        min_mass_input = min(min_mass_input, current_max_mass_val)
        new_slider_min = np.log10(min_mass_input + 1)
        new_slider_max = np.log10(current_max_mass_val + 1)
        new_slider_min = max(new_slider_min, slider_min_log)
        new_slider_max = min(new_slider_max, slider_max_log)
        return [new_slider_min, new_slider_max], min_mass_input, current_max_mass_val, \
               f"{format_mass_int(min_mass_input)} – {format_mass_int(current_max_mass_val)}"
    elif trigger_id == 'max-mass-input':
        if max_mass_input is None: max_mass_input = df['mass'].max()
        current_min_mass_val = min_mass_input if min_mass_input is not None else df['mass'].min()
        max_mass_input = max(max_mass_input, current_min_mass_val)
        new_slider_min = np.log10(current_min_mass_val + 1)
        new_slider_max = np.log10(max_mass_input + 1)
        new_slider_min = max(new_slider_min, slider_min_log)
        new_slider_max = min(new_slider_max, slider_max_log)
        return [new_slider_min, new_slider_max], current_min_mass_val, max_mass_input, \
               f"{format_mass_int(current_min_mass_val)} – {format_mass_int(max_mass_input)}"
    min_m_init = 10**slider_value[0] - 1
    max_m_init = 10**slider_value[1] - 1
    return slider_value, min_m_init, max_m_init, \
           f"{format_mass_int(min_m_init)} – {format_mass_int(max_m_init)}"


@app.callback(
    [Output('year-slider', 'value'),
     Output('min-year-input', 'value'),
     Output('max-year-input', 'value'),
     Output('year-slider-display', 'children')],
    [Input('year-slider', 'value'),
     Input('min-year-input', 'value'),
     Input('max-year-input', 'value')],
    [State('year-slider', 'min'), State('year-slider', 'max')]
)
def sync_year_inputs(slider_value, min_year_input, max_year_input, slider_min, slider_max):
    """Synchronisiert den Jahres-Range-Slider mit den Min/Max-Eingabefeldern."""
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'initial_load'

    if trigger_id == 'year-slider':
        return slider_value, slider_value[0], slider_value[1], \
               f"{int(slider_value[0])} – {int(slider_value[1])}"
    elif trigger_id == 'min-year-input':
        if min_year_input is None: min_year_input = df['year'].min()
        current_max_year = max_year_input if max_year_input is not None else df['year'].max()
        min_year_input = min(min_year_input, current_max_year)
        min_year_input = max(min_year_input, slider_min)
        return [min_year_input, current_max_year], min_year_input, current_max_year, \
               f"{int(min_year_input)} – {int(current_max_year)}"
    elif trigger_id == 'max-year-input':
        if max_year_input is None: max_year_input = df['year'].max()
        current_min_year = min_year_input if min_year_input is not None else df['year'].min()
        max_year_input = max(max_year_input, current_min_year)
        max_year_input = min(max_year_input, slider_max)
        return [current_min_year, max_year_input], current_min_year, max_year_input, \
               f"{int(current_min_year)} – {int(max_year_input)}"
    return slider_value, slider_value[0], slider_value[1], \
           f"{int(slider_value[0])} – {int(slider_value[1])}"

if __name__ == '__main__':
    app.run_server(debug=True)