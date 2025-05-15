import dash                       # for dash.callback_context
import numpy as np
from dash import Input, Output, callback


def register(app, df=None):
    """Registriert die beiden Sync‑Callbacks für Massen‑ und Jahr‑Filter."""

    # ------------------------- Masse ----------------------------------
    @app.callback(
        [Output("mass-slider", "value"),
         Output("min-mass-input", "value"),
         Output("max-mass-input", "value"),
         Output("mass-slider-display", "children")],
        [Input("mass-slider", "value"),
         Input("min-mass-input", "value"),
         Input("max-mass-input", "value")],
    )
    def sync_mass_inputs(slider_value, min_mass, max_mass):
        ctx = dash.callback_context
        if not ctx.triggered:
            label = f"{int(10**slider_value[0]-1):,} g – " \
                    f"{int(10**slider_value[1]-1):,} g"
            return slider_value, 10**slider_value[0]-1, 10**slider_value[1]-1, label

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger == "mass-slider":
            min_m = 10**slider_value[0] - 1
            max_m = 10**slider_value[1] - 1
            label = f"{int(min_m):,} g – {int(max_m):,} g"
            return slider_value, min_m, max_m, label

        if trigger == "min-mass-input":
            min_mass = min(min_mass, max_mass)
            label = f"{int(min_mass):,} g – {int(max_mass):,} g"
            return [np.log10(min_mass + 1), np.log10(max_mass + 1)], \
                   min_mass, max_mass, label

        if trigger == "max-mass-input":
            max_mass = max(max_mass, min_mass)
            label = f"{int(min_mass):,} g – {int(max_mass):,} g"
            return [np.log10(min_mass + 1), np.log10(max_mass + 1)], \
                   min_mass, max_mass, label

        # Fallback
        label = f"{int(10**slider_value[0]):,} g – {int(10**slider_value[1]):,} g"
        return slider_value, 10**slider_value[0], 10**slider_value[1], label

    # ------------------------- Jahr -----------------------------------
    @app.callback(
        [Output("year-slider", "value"),
         Output("min-year-input", "value"),
         Output("max-year-input", "value"),
         Output("year-slider-display", "children")],
        [Input("year-slider", "value"),
         Input("min-year-input", "value"),
         Input("max-year-input", "value")],
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

        if trigger_id == "min-year-input":
            min_year = min(min_year, max_year)
            label = f"{int(min_year)} – {int(max_year)}"
            return [min_year, max_year], min_year, max_year, label

        if trigger_id == "max-year-input":
            max_year = max(max_year, min_year)
            label = f"{int(min_year)} – {int(max_year)}"
            return [min_year, max_year], min_year, max_year, label

        # Fallback
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label
