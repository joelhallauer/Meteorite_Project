CACHE_CONFIG = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 3600,
}

MAPBOX_STYLE = "carto-positron"

# Cluster-Style (kann man hier zentral anpassen)
CLUSTER_CONF = dict(
    enabled=True,
    maxzoom=8,
    step=60,
    size=20,
    color="rgb(0, 123, 255)",
    opacity=0.6,
)
