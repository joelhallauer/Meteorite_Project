from typing import Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from utils.caching import cache

# Initialisiere den Nominatim-Geolocator mit RateLimiter auf geocode
_geolocator = Nominatim(user_agent="meteorite_app")
_geocode = RateLimiter(_geolocator.geocode, min_delay_seconds=1)

@cache.memoize()
def geocode_location(address: str) -> Optional[Tuple[float, float]]:
    """
    Wandelt einen Ortsnamen in (latitude, longitude) um.
    Gibt None zurück, falls nichts gefunden wird oder ein Fehler auftritt.
    """
    try:
        location = _geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        return None
    return None