import numpy as np
from dash import callback_context, Input, Output, no_update

def register_mass_callbacks(app, df):
    """
    Synchronisiert Slider- und Input-Felder für die Masse.
    """
    @app.callback(
        [
            Output('mass-slider', 'value'),
            Output('min-mass-input', 'value'),
            Output('max-mass-input', 'value'),
            Output('mass-slider-display', 'children')
        ],
        [
            Input('mass-slider', 'value'),
            Input('min-mass-input', 'value'),
            Input('max-mass-input', 'value')
        ]
    )
    def sync_mass_inputs(slider_value, min_mass, max_mass):
        ctx = callback_context
        # Erster Aufruf nach Laden der Seite
        if not ctx.triggered:
            label = f"{int(10**slider_value[0] - 1):,} g – {int(10**slider_value[1] - 1):,} g"
            return slider_value, 10**slider_value[0] - 1, 10**slider_value[1] - 1, label

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'mass-slider':
            min_m = 10**slider_value[0] - 1
            max_m = 10**slider_value[1] - 1
            label = f"{int(min_m):,} g – {int(max_m):,} g"
            return slider_value, min_m, max_m, label

        elif trigger == 'min-mass-input':
            # Falls kein max_mass übergeben, nehmen wir df-Maximum
            current_max = max_mass if max_mass is not None else df['mass'].max()
            min_val = min(min_mass, current_max)
            label = f"{int(min_val):,} g – {int(current_max):,} g"
            return [np.log10(min_val + 1), np.log10(current_max + 1)], min_val, current_max, label

        elif trigger == 'max-mass-input':
            current_min = min_mass if min_mass is not None else df['mass'].min()
            max_val = max(max_mass, current_min)
            label = f"{int(current_min):,} g – {int(max_val):,} g"
            return [np.log10(current_min + 1), np.log10(max_val + 1)], current_min, max_val, label

        # Fallback
        label = f"{int(10**slider_value[0] - 1):,} g – {int(10**slider_value[1] - 1):,} g"
        return slider_value, 10**slider_value[0] - 1, 10**slider_value[1] - 1, label
