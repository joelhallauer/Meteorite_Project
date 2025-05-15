# meteorite_project/components/controls.py
from dash import html, dcc
import numpy as np


def _human_mass(m: float) -> str:
    """Hilfsfunktion für Slider‑Marks ohne Nachkommastellen."""
    if m < 1:
        return f"{m:.1f} g"
    if m < 1_000:
        return f"{int(round(m))} g"
    if m < 1_000_000:
        return f"{int(round(m / 1_000))} kg"
    return f"{int(round(m / 1_000_000))} t"


def Filters(df):
    """Rechtes Steuer‑Panel: Karten‑Optionen, Filter & Eingabefelder."""

    # ---------------------- Masse-Markierungen -----------------------
    log_min, log_max = df["log_mass"].min(), df["log_mass"].max()
    mass_marks = {
        float(f"{tick:.2f}"): _human_mass(10 ** tick - 1)
        for tick in np.linspace(log_min, log_max, 5)  # exakt 5 gleichmäßige Marker
    }

    # ---------------------- Jahr-Markierungen ------------------------
    year_min, year_max = int(df.year.min()), int(df.year.max())
    year_marks = {int(y): str(int(y)) for y in np.linspace(year_min, year_max, 5)}

    # ---------------------- Layout‑Baum ------------------------------
    return html.Div(
        [
            # -------------------------------------------------- Karte‑Typ
            html.H4("Karte:"),
            dcc.Dropdown(id="map-filter", options=["Punktekarte", "Heatmap"], value="Punktekarte"),
            html.Hr(),

            # -------------------------------------------------- Masse‑Filter
            html.H4("Masse (g)"),
            html.Div(id="mass-slider-display", style={"textAlign": "center", "marginTop": "4px"}),
            dcc.RangeSlider(
                id="mass-slider",
                min=log_min,
                max=log_max,
                value=[log_min, log_max],
                marks=mass_marks,
                step=0.05,
                updatemode="drag",
            ),
            html.Div(
                [
                    html.Label("Min:", style={"margin": "4px"}),
                    dcc.Input(id="min-mass-input", type="number", value=float(df.mass.min()),
                              style={"width": "45%", "marginRight": "4%"}),
                    html.Label("Max:", style={"margin": "4px"}),
                    dcc.Input(id="max-mass-input", type="number", value=float(df.mass.max()),
                              style={"width": "45%"}),
                ],
                style={"display": "flex", "justifyContent": "space-between", "marginTop": "6px"},
            ),
            html.Hr(),

            # -------------------------------------------------- Jahr‑Filter
            html.H4("Jahr"),            
            html.Div(id="year-slider-display", style={"textAlign": "center", "marginTop": "4px"}),
            dcc.RangeSlider(
                id="year-slider",
                min=year_min,
                max=year_max,
                value=[year_min, year_max],
                marks=year_marks,
                updatemode="drag",
            ),
            html.Div(
                [
                    html.Label("Von:", style={"margin": "4px"}),
                    dcc.Input(id="min-year-input", type="number", value=year_min,
                              style={"width": "45%", "marginRight": "4%"}),
                    html.Label("Bis:", style={"margin": "4px"}),
                    dcc.Input(id="max-year-input", type="number", value=year_max,
                              style={"width": "45%"}),
                ],
                style={"display": "flex", "justifyContent": "space-between", "marginTop": "6px"},
            ),
            html.Hr(),

            # -------------------------------------------------- Meteoriten‑Typ
            html.H4("Meteoritentyp"),
            dcc.Dropdown(id="class-filter", options=[{"label": c, "value": c} for c in sorted(df.recclass.unique())], multi=True),
            html.Hr(),

            # -------------------------------------------------- Status (Fall/Found)
            html.H4("Status"),
            dcc.Checklist(
                id="fall-filter",
                options=[
                    {"label": "Beobachtet", "value": "Fell"},
                    {"label": "Gefunden", "value": "Found"},
                ],
                value=df.fall.unique().tolist(),
                labelStyle={"display": "inline-block", "margin": "3px 0"},
            ),
        ],
        style={"overflowY": "auto"},
    )
