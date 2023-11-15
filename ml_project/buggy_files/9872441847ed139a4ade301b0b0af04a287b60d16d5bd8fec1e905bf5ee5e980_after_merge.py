    async def _send_single_request(
        self, request: Request, timeout: Timeout
    ) -> Response:
        """
        Sends a single request, without handling any redirections.
        """
        transport = self._transport_for_url(request.url)
        timer = Timer()
        await timer.async_start()

        with map_exceptions(HTTPCORE_EXC_MAP, request=request):
            (status_code, headers, stream, ext) = await transport.arequest(
                request.method.encode(),
                request.url.raw,
                headers=request.headers.raw,
                stream=request.stream,  # type: ignore
                ext={"timeout": timeout.as_dict()},
            )

        async def on_close(response: Response) -> None:
            response.elapsed = datetime.timedelta(seconds=await timer.async_elapsed())
            if hasattr(stream, "aclose"):
                with map_exceptions(HTTPCORE_EXC_MAP, request=request):
                    await stream.aclose()

        response = Response(
            status_code,
            headers=headers,
            stream=stream,  # type: ignore
            ext=ext,
            request=request,
            on_close=on_close,
        )

        self.cookies.extract_cookies(response)

        status = f"{response.status_code} {response.reason_phrase}"
        response_line = f"{response.http_version} {status}"
        logger.debug(f'HTTP Request: {request.method} {request.url} "{response_line}"')

        return response