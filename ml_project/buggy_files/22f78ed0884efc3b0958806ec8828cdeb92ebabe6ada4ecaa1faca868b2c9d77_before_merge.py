    def __init__(
        self,
        proxy_url: URLTypes,
        *,
        proxy_headers: HeaderTypes = None,
        proxy_mode: HTTPProxyMode = HTTPProxyMode.DEFAULT,
        verify: VerifyTypes = True,
        cert: CertTypes = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        pool_limits: PoolLimits = DEFAULT_POOL_LIMITS,
        backend: ConcurrencyBackend = None,
    ):

        super(HTTPProxy, self).__init__(
            verify=verify,
            cert=cert,
            timeout=timeout,
            pool_limits=pool_limits,
            backend=backend,
        )

        self.proxy_url = URL(proxy_url)
        self.proxy_mode = proxy_mode
        self.proxy_headers = Headers(proxy_headers)

        url = self.proxy_url
        if url.username or url.password:
            self.proxy_headers.setdefault(
                "Proxy-Authorization",
                build_basic_auth_header(url.username, url.password),
            )
            # Remove userinfo from the URL authority, e.g.:
            # 'username:password@proxy_host:proxy_port' -> 'proxy_host:proxy_port'
            credentials, _, authority = url.authority.rpartition("@")
            self.proxy_url = url.copy_with(authority=authority)