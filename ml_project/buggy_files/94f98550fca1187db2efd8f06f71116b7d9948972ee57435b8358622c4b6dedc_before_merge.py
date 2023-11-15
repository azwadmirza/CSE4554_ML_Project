def add_resizable_cache(cache_name: str, cache_resize_callback: Callable):
    """Register a cache that's size can dynamically change

    Args:
        cache_name: A reference to the cache
        cache_resize_callback: A callback function that will be ran whenever
            the cache needs to be resized
    """
    # Some caches have '*' in them which we strip out.
    cache_name = _canonicalise_cache_name(cache_name)

    _CACHES[cache_name] = cache_resize_callback

    # Ensure all loaded caches are sized appropriately
    #
    # This method should only run once the config has been read,
    # as it uses values read from it
    if properties.resize_all_caches_func:
        properties.resize_all_caches_func()