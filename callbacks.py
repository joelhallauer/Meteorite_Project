# -------------------- callbacks.py --------------------
"""All Dash callbacks live here. Register them with *register_callbacks()*."""
from typing import List, Tuple

import dash
from dash import Input, Output, State, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from geopy.distance import geodesic

from utils import geocode_location, format_mass_int, format_mass


# The hefty map+stats update callback ---------------------------------------

def register_callbacks(app, df):
    """Attach all callbacks to *app*."""

    # ---------------------------------------------------------------------
    @app.callback(
        [Output("location-input", "value"), Output("radius-dropdown", "value")],
        Input("reset-button", "n_clicks"),
    )
    def reset_location_inputs(n_clicks):
        if n_clicks:
            return "", "unlimited"
        return dash.no_update

    # ---------------------------------------------------------------------
    @app.callback(
        [
            Output("meteor-map", "figure"),
            Output("stats-container", "children"),
            Output("meteor-table", "data"),
        ],
        [
            Input("fall-filter", "value"),
            Input("class-filter", "value"),
            Input("search-button", "n_clicks"),
            Input("reset-button", "n_clicks"),
            Input("mass-slider", "value"),
            Input("year-slider", "value"),
            Input("map-filter", "value"),
            Input("meteor-table", "active_cell"),
        ],
        [State("location-input", "value"), State("radius-dropdown", "value")],
    )
    def update_map(
        selected_falls: List[str],
        selected_classes: List[str],
        search_clicks: int,
        reset_clicks: int,
        selected_mass: Tuple[float, float],
        selected_year: Tuple[int, int],
        map_type: str,
        active_cell: dict,
        location: str,
        radius,
    ):
        """Main callback – filters, builds map figure and statistics."""
        filtered_df = df.copy()

        # ---------- Mass range (log slider!)
        if selected_mass:
            min_mass = 10 ** selected_mass[0] - 1
            max_mass = 10 ** selected_mass[1] - 1
            filtered_df = filtered_df.query("@min_mass <= mass <= @max_mass")

        # ---------- Meteorite class filter
        if selected_classes:
            filtered_df = filtered_df[filtered_df["recclass"].isin(selected_classes)]

        # ---------- Year range
        if selected_year:
            filtered_df = filtered_df.query("@selected_year[0] <= year <= @selected_year[1]")

        # ---------- Fall / Found filter
        if selected_falls:
            filtered_df = filtered_df[filtered_df["fall"].isin(selected_falls)]

        # ---------- Location‑based filter ----------------------------------
        center_lat = center_lon = None
        map_center = dict(lat=20, lon=0)
        zoom_level = 1.5

        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]["prop_id"] == "search-button.n_clicks":
            if location:
                coords = geocode_location(location)
                if coords:
                    center_lat, center_lon = coords
                    map_center = dict(lat=center_lat, lon=center_lon)
                    zoom_level = 5

                    if radius != "unlimited":
                        radius_km = float(radius)
                        filtered_df["distance"] = filtered_df.apply(
                            lambda r: geodesic((center_lat, center_lon), (r["reclat"], r["reclong"])).kilometers,
                            axis=1,
                        )
                        filtered_df = filtered_df[filtered_df["distance"] <= radius_km]

        if "distance" in filtered_df.columns:
            filtered_df.drop(columns=["distance"], inplace=True)

        # ---------- Empty result handling ----------------------------------
        if filtered_df.empty:
            empty_fig = px.scatter_mapbox(
                pd.DataFrame(columns=["reclat", "reclong"]),
                lat="reclat",
                lon="reclong",
                zoom=1,
                mapbox_style="carto-positron",
                title="Keine Ergebnisse gefunden",
            )
            empty_fig.update_layout(height=800)
            return (
                empty_fig,
                html.P("Keine Daten verfügbar für die aktuelle Auswahl.", style={"color": "red"}),
                [],
            )

        # ---------- Statistics --------------------------------------------
        stats = [
            html.P(f"Anzahl Meteoriten: {len(filtered_df)}", style={"margin": "5px 0"}),
            html.P(f"Durchschnittliche Masse: {format_mass(filtered_df['mass'].mean())}", style={"margin": "5px 0"}),
            html.P(f"Grösste Masse: {format_mass(filtered_df['mass'].max())}", style={"margin": "5px 0"}),
            html.P(f"Kleinste Masse: {format_mass(filtered_df['mass'].min())}", style={"margin": "5px 0"}),
        ]
        if not filtered_df["year"].isna().all():
            stats.append(
                html.P(
                    f"Zeitraum: {int(filtered_df['year'].min())} - {int(filtered_df['year'].max())}",
                    style={"margin": "5px 0"},
                )
            )

        # ---------- Zoom to selected table row ----------------------------
        if active_cell and "row" in active_cell and 0 <= active_cell["row"] < len(filtered_df):
            sel = filtered_df.iloc[active_cell["row"]]
            map_center = dict(lat=sel["reclat"], lon=sel["reclong"])
            zoom_level = 6

        # ---------- Build figure ------------------------------------------
        if map_type == "Heatmap":
            fig = px.density_mapbox(
                filtered_df,
                lat="reclat",
                lon="reclong",
                z="mass",
                radius=10,
                opacity=0.8,
                mapbox_style="carto-positron",
                center=map_center,
                zoom=zoom_level,
            )
        else:
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
                    "size_for_plot": False,
                },
                opacity=0.7,
                mapbox_style="carto-positron",
            )

            fig.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>" "Fundjahr: %{customdata[0]}<br>" "Land: %{customdata[4]}<br>" "Breitengrad: %{lat}<br>" "Längengrad: %{lon}<br>" "Masse: %{customdata[1]}<br>" "Meteoritenklasse: %{customdata[2]}<br>" "Beobachteter Fall: %{customdata[3]}<br>",
                marker=dict(sizemode="area"),
            )

        fig.update_layout(
            height=600,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            mapbox=dict(center=map_center, zoom=zoom_level),
            coloraxis_colorbar=dict(title="Fundjahr", thicknessmode="pixels", thickness=20, len=0.6, yanchor="middle", y=0.5),
        )

        # ----- Draw search radius circle
        if center_lat is not None and center_lon is not None and radius != "unlimited":
            radius_km = float(radius)
            circle_lats: List[float] = []
            circle_lons: List[float] = []
            for bearing in np.arange(0, 360, 1):
                point = geodesic(kilometers=radius_km).destination((center_lat, center_lon), bearing)
                circle_lats.append(point.latitude)
                circle_lons.append(point.longitude)
            fig.add_trace(
                go.Scattermapbox(
                    lat=circle_lats,
                    lon=circle_lons,
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba(255,0,0,0.15)",
                    line=dict(color="red", width=2),
                    name="Suchradius",
                )
            )

        table_data = filtered_df[["name", "year", "formatted_mass", "recclass", "country"]].to_dict("records")
        return fig, stats, table_data

    # ---------------------------------------------------------------------
    # Synchronise mass inputs
    @app.callback(
        [Output("mass-slider", "value"), Output("min-mass-input", "value"), Output("max-mass-input", "value"), Output("mass-slider-display", "children")],
        [Input("mass-slider", "value"), Input("min-mass-input", "value"), Input("max-mass-input", "value")],
    )
    def sync_mass_inputs(slider_value, min_mass, max_mass):
        ctx = dash.callback_context
        if not ctx.triggered:
            label = f"{int(10 ** slider_value[0] - 1):,} g – {int(10 ** slider_value[1] - 1):,} g"
            return slider_value, 10 ** slider_value[0] - 1, 10 ** slider_value[1] - 1, label

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "mass-slider":
            min_m = 10 ** slider_value[0] - 1
            max_m = 10 ** slider_value[1] - 1
            label = f"{int(min_m):,} g – {int(max_m):,} g"
            return slider_value, min_m, max_m, label
        elif trigger == "min-mass-input":
            min_mass = min(min_mass, max_mass)
            label = f"{int(min_mass):,} g – {int(max_mass):,} g"
            return [np.log10(min_mass + 1), np.log10(max_mass + 1)], min_mass, max_mass, label
        elif trigger == "max-mass-input":
            max_mass = max(max_mass, min_mass)
            label = f"{int(min_mass):,} g – {int(max_mass):,} g"
            return [np.log10(min_mass + 1), np.log10(max_mass + 1)], min_mass, max_mass, label
        label = f"{int(10 ** slider_value[0])} g – {int(10 ** slider_value[1]):,} g"
        return slider_value, 10 ** slider_value[0], 10 ** slider_value[1], label

    # ---------------------------------------------------------------------
    # Synchronise year inputs
    @app.callback(
        [Output("year-slider", "value"), Output("min-year-input", "value"), Output("max-year-input", "value"), Output("year-slider-display", "children")],
        [Input("year-slider", "value"), Input("min-year-input", "value"), Input("max-year-input", "value")],
    )
    def sync_year_inputs(slider_value, min_year, max_year):
        ctx = dash.callback_context
        if not ctx.triggered:
            label = f"{int(slider_value[0])} – {int(slider_value[1])}"
            return slider_value, slider_value[0], slider_value[1], label
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "year-slider":
            label = f"{int(slider_value[0])} – {int(slider_value[1])}"
            return slider_value, slider_value[0], slider_value[1], label
        elif trigger_id == "min-year-input":
            min_year = min(min_year, max_year)
            label = f"{int(min_year)} – {int(max_year)}"
            return [min_year, max_year], min_year, max_year, label
        elif trigger_id == "max-year-input":
            max_year = max(max_year, min_year)
            label = f"{int(min_year)} – {int(max_year)}"
            return [min_year, max_year], min_year, max_year, label
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label