    async def _get_response(
        self,
        request: AsyncRequest,
        *,
        stream: bool = False,
        auth: AuthTypes = None,
        allow_redirects: bool = True,
        verify: VerifyTypes = None,
        cert: CertTypes = None,
        timeout: TimeoutTypes = None,
        trust_env: bool = None,
        proxies: ProxiesTypes = None,
    ) -> AsyncResponse:
        if request.url.scheme not in ("http", "https"):
            raise InvalidURL('URL scheme must be "http" or "https".')

        if proxies is not None:
            dispatch_proxies = _proxies_to_dispatchers(proxies)
        else:
            dispatch_proxies = self.proxies
        dispatch = self._dispatcher_for_request(request, dispatch_proxies)

        async def get_response(request: AsyncRequest) -> AsyncResponse:
            try:
                with ElapsedTimer() as timer:
                    response = await dispatch.send(
                        request, verify=verify, cert=cert, timeout=timeout
                    )
                response.elapsed = timer.elapsed
            except HTTPError as exc:
                # Add the original request to any HTTPError unless
                # there'a already a request attached in the case of
                # a ProxyError.
                if exc.request is None:
                    exc.request = request
                raise

            self.cookies.extract_cookies(response)
            if not stream:
                try:
                    await response.read()
                finally:
                    await response.close()

            return response

        def wrap(
            get_response: typing.Callable, middleware: BaseMiddleware
        ) -> typing.Callable:
            return functools.partial(middleware, get_response=get_response)

        get_response = wrap(
            get_response,
            RedirectMiddleware(allow_redirects=allow_redirects, cookies=self.cookies),
        )

        auth_middleware = self._get_auth_middleware(
            request=request,
            trust_env=self.trust_env if trust_env is None else trust_env,
            auth=self.auth if auth is None else auth,
        )

        if auth_middleware is not None:
            get_response = wrap(get_response, auth_middleware)

        return await get_response(request)