def _proxy_from_url(url: URLTypes) -> AsyncDispatcher:
    url = URL(url)
    if url.scheme in ("http", "https"):
        return HTTPProxy(url)
    raise ValueError(f"Unknown proxy for {url!r}")