    def send(
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
    ) -> Response:
        concurrency_backend = self.concurrency_backend

        coroutine = self._get_response
        args = [request]
        kwargs = {
            "stream": True,
            "auth": auth,
            "allow_redirects": allow_redirects,
            "verify": verify,
            "cert": cert,
            "timeout": timeout,
            "trust_env": trust_env,
        }
        async_response = concurrency_backend.run(coroutine, *args, **kwargs)

        content = getattr(
            async_response, "_raw_content", getattr(async_response, "_raw_stream", None)
        )

        sync_content = self._sync_data(content)

        def sync_on_close() -> None:
            nonlocal concurrency_backend, async_response
            concurrency_backend.run(async_response.on_close)

        response = Response(
            status_code=async_response.status_code,
            http_version=async_response.http_version,
            headers=async_response.headers,
            content=sync_content,
            on_close=sync_on_close,
            request=async_response.request,
            history=async_response.history,
            elapsed=async_response.elapsed,
        )
        if not stream:
            try:
                response.read()
            finally:
                response.close()
        return response