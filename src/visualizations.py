import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .utils import format_mass, calculate_zoom_level, get_circle_coords

def create_empty_map_figure(center_lat=20, center_lon=0, zoom=1):
    """
    Erstellt eine leere Plotly-Karte mit einem Standard-Mittelpunkt und Zoomlevel.
    Wird verwendet, wenn keine Daten für die Anzeige auf der Karte vorhanden sind.
    """
    empty_fig = px.scatter_mapbox(
        pd.DataFrame(columns=["reclat", "reclong"]), # Leerer DataFrame
        lat="reclat",
        lon="reclong",
        zoom=zoom,
        center=dict(lat=center_lat, lon=center_lon),
        mapbox_style="carto-positron" # Kartenstil
    )
    empty_fig.update_layout(height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return empty_fig

def create_cluster_map(
    filtered_df: pd.DataFrame,
    map_center: dict,
    zoom_level: float,
    center_lat: float = None,
    center_lon: float = None,
    radius: str = 'unlimited'
) -> go.Figure:
    """
    Erstellt eine Cluster-Karte der Meteoritenfunde.
    Meteoriten werden gruppiert, wenn der Zoomlevel niedrig ist.
    """
    fig = px.scatter_mapbox(
        filtered_df,
        lat="reclat",
        lon="reclong",
        color="year", # Farben basierend auf dem Fundjahr
        size="size_for_plot", # Größe der Punkte basierend auf logarithmischer Masse
        size_max=10,
        color_continuous_scale="Viridis", # Farbskala für das Jahr
        hover_name="name", # Name des Meteoriten beim Hovern
        hover_data={ # Zusätzliche Daten, die beim Hovern angezeigt werden
            "year": True,
            "formatted_mass": True,
            "recclass": True,
            "fall_de": True,
            "country": True,
            "mass": False, # Rohmasse nicht anzeigen
            "fall": False, # Roh-Fall-Status nicht anzeigen
            "size_for_plot": False # Plot-Größe nicht anzeigen
        },
        opacity=0.7,
        mapbox_style="carto-positron",
        labels={ # Beschriftungen für die Legende
            "year": "Fundjahr"
        }
    )
    # Cluster-Einstellungen für die Karte
    for trace in fig.data:
        if isinstance(trace, go.Scattermapbox):
            trace.update(cluster=dict(
                enabled=True, maxzoom=8, step=60, size=20, # Cluster-Einstellungen
                color='rgb(0, 123, 255)', opacity=0.6
            ))
    # Hover-Template anpassen
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Fundjahr: %{customdata[0]}<br>" +
                      "Land: %{customdata[4]}<br>" +
                      "Breitengrad: %{lat}<br>" +
                      "Längengrad: %{lon}<br>" +
                      "Masse: %{customdata[1]}<br>" +
                      "Meteoritenklasse: %{customdata[2]}<br>" +
                      "Beobachteter Fall: %{customdata[3]}<br>",
        marker=dict(sizemode="area")
    )
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=map_center, # Kartenmittelpunkt
            zoom=zoom_level # Zoomlevel
        )
    )

    # Suchradius und Mittelpunktmarker hinzufügen
    _add_search_radius_to_map(fig, center_lat, center_lon, radius)
    _add_search_center_marker(fig, center_lat, center_lon)
    return fig

def create_point_map(
    filtered_df: pd.DataFrame,
    map_center: dict,
    zoom_level: float,
    center_lat: float = None,
    center_lon: float = None,
    radius: str = 'unlimited'
) -> go.Figure:
    """
    Erstellt eine Punktekarte der Meteoritenfunde.
    Jeder Meteorit wird als einzelner Punkt dargestellt.
    """
    fig = px.scatter_mapbox(
        filtered_df,
        lat="reclat",
        lon="reclong",
        color="year",
        size="size_for_plot",
        size_max=10,
        color_continuous_scale="Viridis",
        hover_name="name",
        hover_data={
            "year": True,
            "formatted_mass": True,
            "recclass": True,
            "fall_de": True,
            "country": True,
            "mass": False,
            "fall": False,
            "size_for_plot": False
        },
        opacity=0.7,
        mapbox_style="carto-positron",
        labels={
            "year": "Fundjahr"
        }
    )
    # Hover-Template anpassen
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Fundjahr: %{customdata[0]}<br>" +
                      "Land: %{customdata[4]}<br>" +
                      "Breitengrad: %{lat}<br>" +
                      "Längengrad: %{lon}<br>" +
                      "Masse: %{customdata[1]}<br>" +
                      "Meteoritenklasse: %{customdata[2]}<br>" +
                      "Beobachteter Fall: %{customdata[3]}<br>",
        marker=dict(sizemode="area")
    )
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=map_center,
            zoom=zoom_level
        )
    )

    # Suchradius und Mittelpunktmarker hinzufügen
    _add_search_radius_to_map(fig, center_lat, center_lon, radius)
    _add_search_center_marker(fig, center_lat, center_lon)
    return fig

def create_heatmap(
    filtered_df: pd.DataFrame,
    map_center: dict,
    zoom_level: float,
    center_lat: float = None,
    center_lon: float = None,
    radius: str = 'unlimited'
) -> go.Figure:
    """
    Erstellt eine Heatmap der Meteoritenfunde.
    Die Heatmap zeigt die Dichte der Funde an.
    """
    fig = px.density_mapbox(
        filtered_df,
        lat="reclat",
        lon="reclong",
        radius=15, # Radius der Heatmap-Punkte
        opacity=0.8,
        mapbox_style="carto-positron",
        zoom=zoom_level,
        center=map_center,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=map_center,
            zoom=zoom_level
        )
    )

    # Suchradius und Mittelpunktmarker hinzufügen
    _add_search_radius_to_map(fig, center_lat, center_lon, radius)
    _add_search_center_marker(fig, center_lat, center_lon)
    return fig

def _add_search_radius_to_map(fig: go.Figure, center_lat, center_lon, radius):
    """
    Fügt einen roten Kreis hinzu, der den Suchradius auf der Karte darstellt,
    wenn ein Ort und ein Radius ausgewählt wurden.
    """
    if center_lat is not None and center_lon is not None and radius != 'unlimited':
        radius_km = float(radius)
        # Koordinaten für den Kreis abrufen
        circle_lats, circle_lons = get_circle_coords(center_lat, center_lon, radius_km)
        fig.add_trace(go.Scattermapbox(
            lat=circle_lats, lon=circle_lons, mode='lines', fill='toself', # Als Linienzug mit Füllung
            fillcolor='rgba(255,0,0,0.15)', line=dict(color='red', width=2),
            name=f'Suchradius ({radius_km} km)', # Legendenname
            showlegend=True
        ))

def _add_search_center_marker(fig: go.Figure, center_lat, center_lon):
    """
    Fügt einen roten Marker hinzu, der das Zentrum des Suchradius auf der Karte darstellt.
    """
    if center_lat is not None and center_lon is not None:
        fig.add_trace(go.Scattermapbox(
            lat=[center_lat], lon=[center_lon], mode='markers',
            marker=dict(size=12, color='red', symbol='circle'), # Marker-Stil
            name='Suchzentrum', # Legendenname
            showlegend=True,
            hovertemplate="<b>Suchzentrum</b><br>" + # Hover-Text
                         f"Breitengrad: {center_lat:.4f}<br>" +
                         f"Längengrad: {center_lon:.4f}<br>" +
                         "<extra></extra>" # Entfernt die Standard-Info des Hover-Templates
        ))


def create_country_bar_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Erstellt ein Balkendiagramm, das die Anzahl der Meteoritenfunde pro Land anzeigt.
    Begrenzt die Anzeige auf die Top 20 Länder, falls mehr vorhanden sind.
    """
    # Zähle Funde pro Land und sortiere absteigend
    country_counts = filtered_df.groupby('country').size().reset_index(name='count')
    country_counts = country_counts.sort_values('count', ascending=False)

    if len(country_counts) > 20:
        country_counts = country_counts.head(20) # Auf Top 20 begrenzen
        country_title = "Top 20 Länder nach Meteoritenfunden"
    else:
        country_title = "Länder nach Meteoritenfunden"

    fig = px.bar(
        country_counts,
        x="country",
        y="count",
        title=country_title,
        labels={ # Beschriftungen für Achsen
            "country": "Land",
            "count": "Anzahl der Meteoriten"
        },
        color_discrete_sequence=["#9c27b0"] # Farbe der Balken
    )
    fig.update_layout(
        xaxis=dict(tickangle=-45), # Achsenbeschriftungen neigen
        height=400,
        margin={"r": 20, "t": 50, "l": 20, "b": 100} # Ränder anpassen
    )
    return fig

def create_class_bar_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Erstellt ein Balkendiagramm, das die Anzahl der Meteoritenfunde pro Meteoritenklasse anzeigt.
    Begrenzt die Anzeige auf die Top 20 Klassen, falls mehr vorhanden sind.
    """
    # Zähle Funde pro Klasse und sortiere absteigend
    class_counts = filtered_df.groupby('recclass').size().reset_index(name='count')
    class_counts = class_counts.sort_values('count', ascending=False)

    if len(class_counts) > 20:
        class_counts = class_counts.head(20) # Auf Top 20 begrenzen
        class_title = "Top 20 Meteoritenklassen nach Funden"
    else:
        class_title = "Meteoritenklassen nach Funden"

    fig = px.bar(
        class_counts,
        x="recclass",
        y="count",
        title=class_title,
        labels={ # Beschriftungen für Achsen
            "recclass": "Meteoritenklasse",
            "count": "Anzahl der Meteoriten"
        },
        color_discrete_sequence=["#9c27b0"] # Farbe der Balken
    )
    fig.update_layout(
        xaxis=dict(tickangle=-45), # Achsenbeschriftungen neigen
        height=400,
        margin={"r": 20, "t": 50, "l": 20, "b": 100} # Ränder anpassen
    )
    return fig