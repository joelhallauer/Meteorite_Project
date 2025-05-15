# meteorite_project/__init__.py
"""
Meteorite-Project Package – bewusst ohne harte Importe,
damit keine Kreisimporte entstehen.
"""

def create_app(*args, **kwargs):
    """Lazy-Import, um Circular-Imports zu vermeiden."""
    from .app import create_app as _factory
    return _factory(*args, **kwargs)
