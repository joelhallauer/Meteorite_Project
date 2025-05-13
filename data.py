import pandas as pd
import numpy as np
import reverse_geocoder as rg
import pycountry
from babel import Locale

df = pd.read_csv("data/meteorite-landings.csv")

# Entferne Zeilen ohne Koordinaten oder mit fehlender Masse
df = df.dropna(subset=['reclat', 'reclong', 'mass', 'year'])

# Entferne ungültige Einträge und konvertiere Jahr in Integer
df = df[(df['year'] <= 2025) & (df['year'] >= 1000)]
df['year'] = df['year'].astype(int)

# Stelle sicher, dass alle Massen positiv sind
df['mass'] = df['mass'].abs()

# Füge formatierte Massenspalte hinzu
def format_mass(mass):
    if mass < 1000:
        return f"{mass:.2f} g"
    elif mass < 1000000:
        return f"{mass/1000:.2f} kg"
    else:
        return f"{mass/1000000:.2f} t"

df['formatted_mass'] = df['mass'].apply(format_mass)

# Verbesserte Punktgröße - logarithmische Skala für bessere Sichtbarkeit der Unterschiede
df['size_for_plot'] = np.log10(df['mass'] + 1) * 3
df['size_for_plot'] = df['size_for_plot'].clip(lower=0.1, upper=15).fillna(0.1)

# Übersetzung für "Fall" Status (Fell/Found)
fall_translation = {
    'Fell': 'Beobachtet',
    'Found': 'Gefunden'
}
df['fall_de'] = df['fall'].map(fall_translation)

# Länderinformationen für jeden Meteoriten hinzufügen
def get_country_batch(coordinates):
    try:
        results = rg.search(coordinates)
        
        def code_to_country_de(cc):
            try:
                return Locale('de').territories[cc.upper()]
            except:
                return "Unbekannt"
        
        return [code_to_country_de(result['cc']) for result in results]
    
    except Exception as e:
        print(f"Fehler beim Abrufen der Länderinformationen: {e}")
        return ["Unbekannt"] * len(coordinates)

# Koordinaten aus deinem DataFrame extrahieren
coordinates = list(zip(df['reclat'], df['reclong']))

# Länderinformationen dem DataFrame hinzufügen
df['country'] = get_country_batch(coordinates)


# Index zurücksetzen
df = df.reset_index(drop=True)

# Speichere den bereinigten DataFrame als CSV im data-Ordner
df.to_csv("data/meteorite-landings-cleaned.csv", index=False)