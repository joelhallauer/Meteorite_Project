def register_callbacks(app, cache, df):
    from . import filters, map, reset   # noqa
    filters.register(app, df)
    map.register(app, cache, df)
    reset.register(app)
