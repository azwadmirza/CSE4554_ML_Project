def _proxies_to_dispatchers(
    proxies: typing.Optional[ProxiesTypes],
    verify: VerifyTypes,
    cert: typing.Optional[CertTypes],
    timeout: TimeoutTypes,
    http_versions: typing.Optional[HTTPVersionTypes],
    pool_limits: PoolLimits,
    backend: ConcurrencyBackend,
    trust_env: bool,
) -> typing.Dict[str, AsyncDispatcher]:
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

    if proxies is None:
        return {}
    elif isinstance(proxies, (str, URL)):
        return {"all": _proxy_from_url(proxies)}
    elif isinstance(proxies, AsyncDispatcher):
        return {"all": proxies}
    else:
        new_proxies = {}
        for key, dispatcher_or_url in proxies.items():
            if isinstance(dispatcher_or_url, (str, URL)):
                new_proxies[str(key)] = _proxy_from_url(dispatcher_or_url)
            else:
                new_proxies[str(key)] = dispatcher_or_url
        return new_proxies