from flask_caching import Cache

# Initialisiere den Cache ohne App
cache = Cache(config={
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 3600
})

def init_cache(app):
    # Hänge den Cache an den Flask-Server
    cache.init_app(app.server)
    return cache
