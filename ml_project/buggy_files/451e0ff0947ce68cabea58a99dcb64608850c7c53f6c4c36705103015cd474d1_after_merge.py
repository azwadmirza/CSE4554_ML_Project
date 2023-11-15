def preload_resources() -> None:
    """Load resource files into the cache."""
    resource_path = _resource_path('')
    for subdir, ext in [
            ('html', '.html'),
            ('javascript', '.js'),
            ('javascript/quirks', '.js'),
    ]:
        for name in _glob_resources(resource_path, subdir, ext):
            _resource_cache[name] = read_file(name)