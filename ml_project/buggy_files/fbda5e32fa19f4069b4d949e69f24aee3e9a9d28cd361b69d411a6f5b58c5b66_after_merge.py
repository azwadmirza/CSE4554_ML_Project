def create_key_from_series(namespace, fn, **kw):
    """Create a key made of indexer name and show ID."""
    def generate_key(*args, **kw):
        show_key = namespace + '_' + text_type(args[1])
        if PY2:
            return show_key.encode('utf-8')
        return show_key
    return generate_key