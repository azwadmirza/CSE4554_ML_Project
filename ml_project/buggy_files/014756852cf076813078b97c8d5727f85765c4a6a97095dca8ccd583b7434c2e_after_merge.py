    def _proxy_from_url(url: URLTypes) -> AsyncDispatcher:
        nonlocal verify, cert, timeout, http_versions, pool_limits, backend, trust_env
        url = URL(url)
        if url.scheme in ("http", "https"):
            return HTTPProxy(
                url,
                verify=verify,
                cert=cert,
                timeout=timeout,
                pool_limits=pool_limits,
                backend=backend,
                trust_env=trust_env,
                http_versions=http_versions,
            )
        raise ValueError(f"Unknown proxy for {url!r}")