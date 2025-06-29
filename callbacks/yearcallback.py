from dash import callback_context, Input, Output
import numpy as np

def register_year_callbacks(app, df):
    """
    Synchronisiert Slider- und Input-Felder für das Jahr.
    """
    @app.callback(
        [
            Output('year-slider', 'value'),
            Output('min-year-input', 'value'),
            Output('max-year-input', 'value'),
            Output('year-slider-display', 'children')
        ],
        [
            Input('year-slider', 'value'),
            Input('min-year-input', 'value'),
            Input('max-year-input', 'value')
        ]
    )
    def sync_year_inputs(slider_value, min_year, max_year):
        ctx = callback_context

        # Erster Aufruf: Initial-Beschriftung
        if not ctx.triggered:
            label = f"{int(slider_value[0])} – {int(slider_value[1])}"
            return slider_value, slider_value[0], slider_value[1], label

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'year-slider':
            label = f"{int(slider_value[0])} – {int(slider_value[1])}"
            return slider_value, slider_value[0], slider_value[1], label

        elif trigger == 'min-year-input':
            # Wenn kein max_year übergeben, nimm df-Maximum
            current_max = max_year if max_year is not None else int(df['year'].max())
            min_val = min(min_year, current_max)
            label = f"{min_val} – {current_max}"
            return [min_val, current_max], min_val, current_max, label

        elif trigger == 'max-year-input':
            # Wenn kein min_year übergeben, nimm df-Minimum
            current_min = min_year if min_year is not None else int(df['year'].min())
            max_val = max(max_year, current_min)
            label = f"{current_min} – {max_val}"
            return [current_min, max_val], current_min, max_val, label

        # Fallback
        label = f"{int(slider_value[0])} – {int(slider_value[1])}"
        return slider_value, slider_value[0], slider_value[1], label
