# meteorite_project/callbacks/map.py
"""Callback‑Registrierung für Karte, Statistik & Tabelle."""

from dash import Input, Output, State, callback, html
import dash
from geopy.distance import geodesic
from ..utils.geocoding import geocode_location
from ..components.map import build_map, empty_figure, add_radius_circle
from ..utils.formatting import format_mass
import pandas as pd


def register(app, cache, df_source):
    """Bindet den grossen Map‑Callback an die Dash‑App."""

    @app.callback(
        [Output("meteor-map", "figure"),
         Output("stats-container", "children"),
         Output("meteor-table", "data")],
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
        [
            State("location-input", "value"),
            State("radius-dropdown", "value"),
        ],
    )
    def update_map(selected_falls, selected_classes, search_clicks, reset_clicks,
                   selected_mass, selected_year, map_type, active_cell,
                   location, radius):
        """Erzeugt Map‑Figure, Statistik‑Div & Tabellen‑Daten entsprechend der Filter."""

        # ---------- Kopie des DF, damit Original unverändert bleibt ----------
        df = df_source.copy()

        # ----------------------------- Filter --------------------------------
        if selected_mass:
            lo, hi = 10 ** selected_mass[0] - 1, 10 ** selected_mass[1] - 1
            df = df[(df.mass >= lo) & (df.mass <= hi)]

        if selected_classes:
            df = df[df.recclass.isin(selected_classes)]

        if selected_year:
            y0, y1 = selected_year
            df = df[(df.year >= y0) & (df.year <= y1)]

        if selected_falls:
            df = df[df.fall.isin(selected_falls)]

        # ------------------------- Geocoding/Radius --------------------------
        map_center = dict(lat=20, lon=0)
        zoom = 1.5
        lat, lon = None, None

        ctx = dash.callback_context  # aktueller Callback‑Kontext von Dash
        if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("search-button"):
            if location:
                coords = geocode_location(location)
                if coords:
                    lat, lon = coords
                    map_center = dict(lat=lat, lon=lon)
                    zoom = 5
                    if radius != "unlimited":
                        r = float(radius)
                        df["distance"] = df.apply(
                            lambda row: geodesic((lat, lon), (row.reclat, row.reclong)).km, axis=1
                        )
                        df = df[df.distance <= r]

        if "distance" in df.columns:
            df.drop(columns="distance", inplace=True)

        # ---------------------- Kein Ergebnis → Platzhalter ------------------
        if df.empty:
            return empty_figure(), html.P("Keine Daten", style={"color": "red"}), []

        # ------------------------- Click‑Zoom über Tabelle -------------------
        if active_cell and "row" in active_cell:
            idx = active_cell["row"]
            if 0 <= idx < len(df):
                sel = df.iloc[idx]
                map_center = dict(lat=sel.reclat, lon=sel.reclong)
                zoom = 6

        # --------------------------- Map‑Figure ------------------------------
        fig = build_map(df, map_type, map_center, zoom)

        if lat is not None and lon is not None and radius != "unlimited":
            add_radius_circle(fig, lat, lon, float(radius))

        # --------------------------- Statistik ------------------------------
        stats = [
            html.P(f"Anzahl: {len(df)}"),
            html.P(f"Ø Masse: {format_mass(df.mass.mean())}"),
            html.P(f"Grösste: {format_mass(df.mass.max())}"),
            html.P(f"Kleinste: {format_mass(df.mass.min())}"),
            html.P(f"Zeitraum: {int(df.year.min())} – {int(df.year.max())}"),
        ]

        table_data = df[["name", "year", "formatted_mass", "recclass", "country"]].to_dict("records")
        return fig, stats, table_data
