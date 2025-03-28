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

# Daten laden und bereinigen
df = load_and_process_data()

# Berechnung von mass_max und mass_min
mass_max = df['mass'].max()
mass_min = df['mass'].min()

# Berechnung von year_max und year_min
year_max = df['year'].max()
year_min = df['year'].min()


# Testen, falls die Datei direkt ausgeführt wird
if __name__ == "__main__":
    df = load_and_process_data()
    print(df.head())

    print(f"Minimale Masse: {mass_min}, Maximale Masse: {mass_max}")
    
    print(f"Frühestes Jahr: {year_min}, Spätestes Jahr: {year_max}")