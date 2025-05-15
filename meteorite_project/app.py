from dash import Dash
from flask_caching import Cache
from .config import CACHE_CONFIG
from .utils.data import load_data
from .utils.geocoding import init_cache
from .layout import create_layout
from .callbacks import register_callbacks

def create_app() -> Dash:
    app = Dash(__name__, title="Impact Atlas")
    app.server.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

    df = load_data()
    cache = Cache(app.server, config=CACHE_CONFIG)
    init_cache(cache)

    app.layout = create_layout(df)
    register_callbacks(app, cache, df)

    return app

if __name__ == "__main__":
    create_app().run_server(debug=True)
