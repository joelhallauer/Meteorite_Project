import pandas as pd

def load_and_process_data():
    # CSV-Datei laden
    data = pd.read_csv("data/meteorite-landings.csv")
    
    # Entfernen von Zeilen ohne GeoLocation
    df = data.dropna(subset=["GeoLocation"])
    
    # Fehlende numerische Werte mit Spaltenmittelwert füllen
    df_clean = df.fillna(df.mean(numeric_only=True))

    # Unrealistische Jahreszahlen löschen
    df_clean = df_clean[df_clean['year'] <= 2025]
    
    return df_clean

def min_max_mass(df):
    mass_max = df['mass'].max()
    mass_min = df['mass'].min()

    return mass_max, mass_min

def min_max_year(df):
    year_max = df['year'].max()
    year_min = df['year'].min()

    return year_max, year_min

# Testen, falls die Datei direkt ausgeführt wird
if __name__ == "__main__":
    df = load_and_process_data()
    print(df.head())

    mass_max, mass_min = min_max_mass(df)
    print(f"Minimale Masse: {mass_min}, Maximale Masse: {mass_max}")
    
    year_max, year_min = min_max_year(df)
    print(f"Frühestes Jahr: {year_min}, Spätestes Jahr: {year_max}")