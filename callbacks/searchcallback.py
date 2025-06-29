from dash import Input, Output, no_update, html
from utils.geocoding import geocode_location

def register_search_callbacks(app):
    @app.callback(
        [Output('location-input','value'),
         Output('radius-dropdown','value')],
        [Input('reset-button','n_clicks')]
    )
    def reset_location(n):
        if n:
            return "", "unlimited"
        return no_update
