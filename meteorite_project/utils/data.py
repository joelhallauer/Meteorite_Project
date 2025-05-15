from pathlib import Path
import pandas as pd
import numpy as np
from .formatting import format_mass_int   # benötigt für Spalte

DATA_FILE = Path(__file__).parent.parent / "data" / "meteorite-landings-cleaned.csv"
_df: pd.DataFrame | None = None

def load_data() -> pd.DataFrame:
    """Lädt CSV einmalig & rechnet Log-Spalte."""
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_FILE)
        _df["log_mass"] = np.log10(_df["mass"] + 1)
        _df["formatted_mass"] = _df["mass"].apply(format_mass_int)
        # Größe für Scatter-Bubble:
        _df["size_for_plot"] = np.cbrt(_df["mass"]).clip(1, 60)
    return _df.copy()
