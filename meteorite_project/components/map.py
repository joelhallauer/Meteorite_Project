import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from geopy.distance import geodesic
from ..config import MAPBOX_STYLE, CLUSTER_CONF

# ---------- Haupt-Figure ------------------------------------------------
def build_map(df, map_type: str, center: dict, zoom: float):
    if map_type == "Heatmap":
        fig = px.density_mapbox(
            df, lat="reclat", lon="reclong", z="mass",
            radius=10, opacity=0.8, mapbox_style=MAPBOX_STYLE,
            center=center, zoom=zoom
        )
    else:
        fig = px.scatter_mapbox(
            df, lat="reclat", lon="reclong",
            color="year", size="size_for_plot", size_max=15,
            hover_name="name",
            mapbox_style=MAPBOX_STYLE,
            color_continuous_scale="Viridis",
            opacity=0.7, center=center, zoom=zoom
        )
        # Clustering
        for tr in fig.data:
            if tr.mode == "markers":
                tr.update(cluster=CLUSTER_CONF)

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=600)
    return fig

# ---------- Kreis-Overlay ----------------------------------------------
def add_radius_circle(fig, lat: float, lon: float, radius_km: float):
    lats, lons = [], []
    for bearing in np.arange(0, 360, 1):
        p = geodesic(kilometers=radius_km).destination((lat, lon), bearing)
        lats.append(p.latitude)
        lons.append(p.longitude)
    fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines", fill="toself",
        fillcolor="rgba(255,0,0,0.15)",
        line=dict(color="red", width=2),
        name="Suchradius"
    ))

# ---------- Leere Figure ------------------------------------------------
def empty_figure():
    return px.scatter_mapbox(
        {}, lat=[], lon=[], mapbox_style=MAPBOX_STYLE, zoom=1,
        title="Keine Ergebnisse"
    )
