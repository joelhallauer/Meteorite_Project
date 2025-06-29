import pandas as pd
import numpy as np
from utils.formatting import format_mass_int


def get_meteorite_df(csv_path: str = None) -> pd.DataFrame:
    """
    Lädt und bereitet den Meteoriten-Datensatz auf.

    Args:
        csv_path (str, optional): Pfad zur CSV-Datei. Standard: 'data/meteorite-landings-cleaned.csv'.

    Returns:
        pd.DataFrame: Vorgefiltertes DataFrame mit zusätzlichen Spalten:
            - year: Numerischer Jahrgang
            - log_mass: Logarithmus (Basis 10) der Masse +1
            - size_for_plot: Skalierte Größe für Marker
            - formatted_mass: Formatierte Masse als String
    """
    # Standardpfad, wenn keiner übergeben
    if csv_path is None:
        csv_path = "data/meteorite-landings-cleaned.csv"

    df = pd.read_csv(csv_path)

    # Jahr als Zahl
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Log-Masse (Basis 10) +1 g, verhindert negative Werte
    df['log_mass'] = np.log10(df['mass'] + 1)

    # Größe für Scatter-Plot: Normierung auf [0, 10]
    log_min = df['log_mass'].min()
    log_max = df['log_mass'].max()
    df['size_for_plot'] = ((df['log_mass'] - log_min) / (log_max - log_min) * 10).fillna(1)

    # Formatiere Masse als String (z.B. "1.234 g")
    df['formatted_mass'] = df['mass'].apply(format_mass_int)

    return df
