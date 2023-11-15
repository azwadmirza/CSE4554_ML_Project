def should_bypass_proxies_patched(should_bypass_proxies_func, url, no_proxy):
    # Monkey patch requests, per https://github.com/requests/requests/pull/4723
    if url.startswith("file://"):
        return True
    try:
        return should_bypass_proxies_func(url, no_proxy)
    except TypeError:
        # For versions of requests we shouldn't have to deal with.
        # https://github.com/conda/conda/issues/7503
        # https://github.com/conda/conda/issues/7506
        return should_bypass_proxies_func(url)