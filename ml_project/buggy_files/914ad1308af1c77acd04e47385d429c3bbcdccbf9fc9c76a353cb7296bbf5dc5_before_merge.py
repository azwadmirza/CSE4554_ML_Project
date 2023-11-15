def should_bypass_proxies_patched(should_bypass_proxies_func, url, no_proxy):
    # Monkey patch requests, per https://github.com/requests/requests/pull/4723
    if url.startswith("file://"):
        return True
    return should_bypass_proxies_func(url, no_proxy)