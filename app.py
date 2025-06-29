import dash

from layout.base_layout import create_layout
from callbacks.registry import register_callbacks
from callbacks.mapcallback import register_map_callbacks
from callbacks.masscallback import register_mass_callbacks
from callbacks.yearcallback import register_year_callbacks
from data.data_loader import get_meteorite_df
from utils.caching import init_cache


df = get_meteorite_df()

# --- App-Initialisierung ---
app = dash.Dash(__name__)
app.title = "Impact Atlas"

# --- Cache-Initialisierung ---
cache = init_cache(app)

# --- Layout der App ---
app.layout = create_layout(df)

# --- Callbacks ---
register_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True)