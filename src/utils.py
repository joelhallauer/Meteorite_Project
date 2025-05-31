import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from flask_caching import Cache
import dash
import dash.html

# Globaler DataFrame (könnte auch über eine Funktion geladen werden)
# Annahme: 'data/meteorite-landings-cleaned.csv' existiert im selben Verzeichnis oder unter /data/
df = pd.read_csv("data/meteorite-landings-cleaned.csv")

# Log-Spalte (Basis 10) für den Slider
df["log_mass"] = np.log10(df["mass"] + 1)  # +1 g verhindert negative Logs

# Übersetzungen für Fall/Found für die Anzeige
df["fall_de"] = df["fall"].map({"Fell": "Beobachtet", "Found": "Gefunden"})

# Formatierer für die Masse
def format_mass(mass: float) -> str:
    """Formatiert eine Masse in g, kg oder t mit zwei Nachkommastellen."""
    if mass < 1_000:               # < 1 kg
        return f"{mass:.2f} g"
    elif mass < 1_000_000:         # < 1 t
        return f"{mass/1_000:.2f} kg"
    else:
        return f"{mass/1_000_000:.2f} t"

def format_mass_int(mass: float) -> str:
    """Massen schön ohne Nachkommastellen (außer < 1 g) formatieren."""
    if mass < 1:                     # 0,1 g usw. soll eine Nachkomma behalten
        return f"{mass:.1f} g"
    if mass < 1_000:
        return f"{int(round(mass))} g"
    if mass < 1_000_000:
        return f"{int(round(mass/1_000))} kg"
    return f"{int(round(mass/1_000_000))} t"

df["formatted_mass"] = df["mass"].apply(format_mass)
df["size_for_plot"] = np.log10(df["mass"] + 1) * 2 

# Geocoder Initialisierung
geolocator = Nominatim(user_agent="impact-atlas")

# Cache Initialisierung (wird in app.py mit der Dash-App verbunden)
# Hier nur die Instanz, die Konfiguration erfolgt in app.py
_cache = None

def init_cache(server):
    """Initialisiert den Cache mit dem Flask-Server der Dash-App."""
    global _cache
    _cache = Cache(server, config={
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 3600       # 1 h Standard-Timeout
    })

def get_cache():
    """Gibt die Cache-Instanz zurück."""
    if _cache is None:
        raise RuntimeError("Cache wurde nicht initialisiert. Rufen Sie init_cache() in app.py auf.")
    return _cache

def geocode_location(place: str):
    """Gibt (lat, lon) oder None zurück - gecacht."""
    # Check if cache is available, if not, don't use caching
    try:
        cache = get_cache()
        cached_result = cache.get(f"geocode_{place}")
        if cached_result:
            return cached_result
    except RuntimeError:
        # Cache not initialized, proceed without caching
        pass
    
    loc = geolocator.geocode(place)
    result = (loc.latitude, loc.longitude) if loc else None
    
    # Try to cache the result if cache is available
    try:
        cache = get_cache()
        cache.set(f"geocode_{place}", result, timeout=3600)
    except RuntimeError:
        # Cache not available, just return the result
        pass
    
    return result

def apply_caching():
    """Apply caching to functions after cache is initialized."""
    global geocode_location
    try:
        cache = get_cache()
        geocode_location = cache.memoize()(geocode_location)
    except RuntimeError:
        pass  # Cache not available

def filter_dataframe(
    data_frame: pd.DataFrame,
    selected_mass: list,
    selected_classes: list,
    selected_year: list,
    selected_falls: list,
    location_coords: tuple = None,
    radius_km: float = None
) -> pd.DataFrame:
    """Filtert den DataFrame basierend auf den gegebenen Kriterien."""
    filtered_df = data_frame.copy()

    if selected_mass:
        log_min, log_max = selected_mass
        min_mass = 10**log_min - 1
        max_mass = 10**log_max - 1
        filtered_df = filtered_df[(filtered_df['mass'] >= min_mass) &
                                (filtered_df['mass'] <= max_mass)]
    if selected_classes:
        filtered_df = filtered_df[filtered_df["recclass"].isin(selected_classes)]
    if selected_year:
        min_year, max_year = selected_year
        filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['year'] <= max_year)]
    if selected_falls:
        filtered_df = filtered_df[filtered_df["fall"].isin(selected_falls)]

    if location_coords and radius_km is not None and radius_km != 'unlimited':
        center_lat, center_lon = location_coords
        lat1, lon1 = np.radians(center_lat), np.radians(center_lon)
        lat2, lon2 = np.radians(filtered_df['reclat']), np.radians(filtered_df['reclong'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Erdradius in km
        filtered_df['distance'] = r * c

        filtered_df = filtered_df[filtered_df['distance'] <= radius_km]
        filtered_df = filtered_df.drop(columns=['distance']) # Entferne die temporäre Spalte
    
    # Sortiere nach Jahr, um eine konsistente Tabellenanzeige zu haben
    return filtered_df.sort_values(by='year', ascending=False)

def get_stats(df_filtered: pd.DataFrame) -> list:
    """Erzeugt eine Liste von HTML-Elementen für die Statistik."""
    if df_filtered.empty:
        return [html.P("Keine Daten für Statistik verfügbar.", style={'color': 'gray'})]

    avg_mass = df_filtered['mass'].mean()
    max_mass = df_filtered['mass'].max()
    min_mass = df_filtered['mass'].min()
    stats = [
        dash.html.P(f"Anzahl Meteoriten: {len(df_filtered)}", style={'margin': '5px 0'}),
        dash.html.P(f"Durchschnittliche Masse: {format_mass(avg_mass)}", style={'margin': '5px 0'}),
        dash.html.P(f"Grösste Masse: {format_mass(max_mass)}", style={'margin': '5px 0'}),
        dash.html.P(f"Kleinste Masse: {format_mass(min_mass)}", style={'margin': '5px 0'})
    ]
    if not df_filtered['year'].isna().all():
        stats.append(
            dash.html.P(f"Zeitraum: {int(df_filtered['year'].min())} - {int(df_filtered['year'].max())}", style={'margin': '5px 0'})
        )
    return stats

def calculate_zoom_level(radius_km):
    """Berechnet den Zoom-Level basierend auf dem Suchradius."""
    if radius_km == 'unlimited':
        return 1.5
    radius_km = float(radius_km)
    if radius_km <= 50:
        return 8
    elif radius_km <= 100:
        return 7
    elif radius_km <= 200:
        return 6
    elif radius_km <= 500:
        return 4
    else:
        return 3

def get_circle_coords(center_lat, center_lon, radius_km):
    """Gibt Koordinaten für einen Kreis um einen Punkt zurück."""
    circle_lats, circle_lons = [], []
    for bearing in np.arange(0, 360, 1):
        point = geodesic(kilometers=radius_km).destination((center_lat, center_lon), bearing)
        circle_lats.append(point.latitude)
        circle_lons.append(point.longitude)
    return circle_lats, circle_lons