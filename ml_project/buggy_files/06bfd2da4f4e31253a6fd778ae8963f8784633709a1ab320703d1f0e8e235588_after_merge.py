    async def get_file(
        self,
        url: str,
        output_stream: BinaryIO,
        max_size: Optional[int] = None,
        headers: Optional[RawHeaders] = None,
    ) -> Tuple[int, Dict[bytes, List[bytes]], str, int]:
        """GETs a file from a given URL
        Args:
            url: The URL to GET
            output_stream: File to write the response body to.
            headers: A map from header name to a list of values for that header
        Returns:
            A tuple of the file length, dict of the response
            headers, absolute URI of the response and HTTP response code.

        Raises:
            RequestTimedOutError: if there is a timeout before the response headers
               are received. Note there is currently no timeout on reading the response
               body.

            SynapseError: if the response is not a 2xx, the remote file is too large, or
               another exception happens during the download.
        """

        actual_headers = {b"User-Agent": [self.user_agent]}
        if headers:
            actual_headers.update(headers)  # type: ignore

        response = await self.request("GET", url, headers=Headers(actual_headers))

        resp_headers = dict(response.headers.getAllRawHeaders())

        if (
            b"Content-Length" in resp_headers
            and max_size
            and int(resp_headers[b"Content-Length"][0]) > max_size
        ):
            logger.warning("Requested URL is too large > %r bytes" % (max_size,))
            raise SynapseError(
                502,
                "Requested file is too large > %r bytes" % (max_size,),
                Codes.TOO_LARGE,
            )

        if response.code > 299:
            logger.warning("Got %d when downloading %s" % (response.code, url))
            raise SynapseError(502, "Got error %d" % (response.code,), Codes.UNKNOWN)

        # TODO: if our Content-Type is HTML or something, just read the first
        # N bytes into RAM rather than saving it all to disk only to read it
        # straight back in again

        try:
            length = await make_deferred_yieldable(
                read_body_with_max_size(response, output_stream, max_size)
            )
        except BodyExceededMaxSize:
            raise SynapseError(
                502,
                "Requested file is too large > %r bytes" % (max_size,),
                Codes.TOO_LARGE,
            )
        except Exception as e:
            raise SynapseError(502, ("Failed to download remote body: %s" % e)) from e

        return (
            length,
            resp_headers,
            response.request.absoluteURI.decode("ascii"),
            response.code,
        )