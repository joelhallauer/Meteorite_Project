from callbacks.mapcallback  import register_map_callbacks
from callbacks.masscallback import register_mass_callbacks
from callbacks.yearcallback import register_year_callbacks
from callbacks.searchcallback import register_search_callbacks  # (s.u.)

def register_callbacks(app, df):
    register_map_callbacks(app, df)
    register_mass_callbacks(app, df)
    register_year_callbacks(app, df)
    register_search_callbacks(app)
