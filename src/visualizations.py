import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .utils import format_mass, calculate_zoom_level, get_circle_coords

def create_empty_map_figure(center_lat=20, center_lon=0, zoom=1):
    """Erstellt eine leere Karte mit einem bestimmten Fokus."""
    empty_fig = px.scatter_mapbox(
        pd.DataFrame(columns=["reclat", "reclong"]),
        lat="reclat",
        lon="reclong",
        zoom=zoom,
        center=dict(lat=center_lat, lon=center_lon),
        mapbox_style="carto-positron"
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
    """Erstellt eine Cluster-Karte der Meteoritenfunde."""
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
    for trace in fig.data:
        if isinstance(trace, go.Scattermapbox):
            trace.update(cluster=dict(
                enabled=True, maxzoom=8, step=60, size=20,
                color='rgb(0, 123, 255)', opacity=0.6
            ))
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
    
    # Add search radius and center marker
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
    """Erstellt eine Punktekarte der Meteoritenfunde."""
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

    # Add search radius and center marker
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
    """Erstellt eine Heatmap der Meteoritenfunde."""
    fig = px.density_mapbox(
        filtered_df,
        lat="reclat",
        lon="reclong",
        radius=15,
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

    # Add search radius and center marker
    _add_search_radius_to_map(fig, center_lat, center_lon, radius)
    _add_search_center_marker(fig, center_lat, center_lon)
    return fig

def _add_search_radius_to_map(fig: go.Figure, center_lat, center_lon, radius):
    """Fügt den Suchradius zur Karte hinzu, falls relevant."""
    if center_lat is not None and center_lon is not None and radius != 'unlimited':
        radius_km = float(radius)
        circle_lats, circle_lons = get_circle_coords(center_lat, center_lon, radius_km)
        fig.add_trace(go.Scattermapbox(
            lat=circle_lats, lon=circle_lons, mode='lines', fill='toself',
            fillcolor='rgba(255,0,0,0.15)', line=dict(color='red', width=2), 
            name=f'Suchradius ({radius_km} km)',
            showlegend=True
        ))

def _add_search_center_marker(fig: go.Figure, center_lat, center_lon):
    """Fügt einen Marker für das Suchzentrum hinzu."""
    if center_lat is not None and center_lon is not None:
        fig.add_trace(go.Scattermapbox(
            lat=[center_lat], lon=[center_lon], mode='markers',
            marker=dict(size=12, color='red', symbol='circle'),
            name='Suchzentrum',
            showlegend=True,
            hovertemplate="<b>Suchzentrum</b><br>" +
                         f"Breitengrad: {center_lat:.4f}<br>" +
                         f"Längengrad: {center_lon:.4f}<br>" +
                         "<extra></extra>"
        ))


def create_country_bar_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Erstellt ein Balkendiagramm der Meteoritenfunde pro Land."""
    country_counts = filtered_df.groupby('country').size().reset_index(name='count')
    country_counts = country_counts.sort_values('count', ascending=False)
    
    if len(country_counts) > 20:
        country_counts = country_counts.head(20)
        country_title = "Top 20 Länder nach Meteoritenfunden"
    else:
        country_title = "Länder nach Meteoritenfunden"

    fig = px.bar(
        country_counts,
        x="country",
        y="count",
        title=country_title,
        labels={
            "country": "Land",
            "count": "Anzahl der Meteoriten"
        },
        color_discrete_sequence=["#9c27b0"]
    )
    fig.update_layout(
        xaxis=dict(tickangle=-45),
        height=400,
        margin={"r": 20, "t": 50, "l": 20, "b": 100}
    )
    return fig

def create_class_bar_chart(filtered_df: pd.DataFrame) -> go.Figure:
    """Erstellt ein Balkendiagramm der Meteoritenfunde pro Meteoritenklasse."""
    class_counts = filtered_df.groupby('recclass').size().reset_index(name='count')
    class_counts = class_counts.sort_values('count', ascending=False)
    
    if len(class_counts) > 20:
        class_counts = class_counts.head(20)
        class_title = "Top 20 Meteoritenklassen nach Funden"
    else:
        class_title = "Meteoritenklassen nach Funden"

    fig = px.bar(
        class_counts,
        x="recclass",
        y="count",
        title=class_title,
        labels={
            "recclass": "Meteoritenklasse",
            "count": "Anzahl der Meteoriten"
        },
        color_discrete_sequence=["#9c27b0"]
    )
    fig.update_layout(
        xaxis=dict(tickangle=-45),
        height=400,
        margin={"r": 20, "t": 50, "l": 20, "b": 100}
    )
    return fig