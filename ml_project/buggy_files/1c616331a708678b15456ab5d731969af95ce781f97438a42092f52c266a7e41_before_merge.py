    def __init__(
        self,
        *,
        auth: AuthTypes = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        verify: VerifyTypes = True,
        cert: CertTypes = None,
        http_versions: HTTPVersionTypes = None,
        proxies: ProxiesTypes = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        pool_limits: PoolLimits = DEFAULT_POOL_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        base_url: URLTypes = None,
        dispatch: typing.Union[AsyncDispatcher, Dispatcher] = None,
        app: typing.Callable = None,
        backend: ConcurrencyBackend = None,
        trust_env: bool = True,
    ):
        if backend is None:
            backend = AsyncioBackend()

        self.check_concurrency_backend(backend)

        if app is not None:
            param_count = len(inspect.signature(app).parameters)
            assert param_count in (2, 3)
            if param_count == 2:
                dispatch = WSGIDispatch(app=app)
            else:
                dispatch = ASGIDispatch(app=app, backend=backend)

        self.trust_env = True if trust_env is None else trust_env

        if dispatch is None:
            async_dispatch: AsyncDispatcher = ConnectionPool(
                verify=verify,
                cert=cert,
                timeout=timeout,
                http_versions=http_versions,
                pool_limits=pool_limits,
                backend=backend,
                trust_env=self.trust_env,
            )
        elif isinstance(dispatch, Dispatcher):
            async_dispatch = ThreadedDispatcher(dispatch, backend)
        else:
            async_dispatch = dispatch

        if base_url is None:
            self.base_url = URL("", allow_relative=True)
        else:
            self.base_url = URL(base_url)

        if proxies is None and trust_env:
            proxies = typing.cast(ProxiesTypes, get_environment_proxies())

        self.proxies: typing.Dict[str, AsyncDispatcher] = _proxies_to_dispatchers(
            proxies
        )

        if params is None:
            params = {}

        self.auth = auth
        self._params = QueryParams(params)
        self._headers = Headers(headers)
        self._cookies = Cookies(cookies)
        self.max_redirects = max_redirects
        self.dispatch = async_dispatch
        self.concurrency_backend = backend