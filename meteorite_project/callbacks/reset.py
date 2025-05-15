from dash import Input, Output, callback

def register(app):
    @app.callback(
        [Output("location-input", "value"),
         Output("radius-dropdown", "value")],
        Input("reset-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def _(_):
        return "", "unlimited"
