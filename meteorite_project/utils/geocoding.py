from geopy.geocoders import Nominatim
from flask_caching import Cache

_geo = Nominatim(user_agent="impact-atlas")
_cache: Cache | None = None

def init_cache(cache: Cache) -> None:
    global _cache
    _cache = cache

def geocode_location(place: str):
    if _cache is None:                             # Fallback ohne Cache
        loc = _geo.geocode(place)
        return (loc.latitude, loc.longitude) if loc else None

    @_cache.memoize()
    def _gc(p):
        loc = _geo.geocode(p)
        return (loc.latitude, loc.longitude) if loc else None
    return _gc(place)
