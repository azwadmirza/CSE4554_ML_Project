    async def get_file(
        self,
        destination: str,
        path: str,
        output_stream,
        args: Optional[QueryArgs] = None,
        retry_on_dns_fail: bool = True,
        max_size: Optional[int] = None,
        ignore_backoff: bool = False,
    ) -> Tuple[int, Dict[bytes, List[bytes]]]:
        """GETs a file from a given homeserver
        Args:
            destination: The remote server to send the HTTP request to.
            path: The HTTP path to GET.
            output_stream: File to write the response body to.
            args: Optional dictionary used to create the query string.
            ignore_backoff: true to ignore the historical backoff data
                and try the request anyway.

        Returns:
            Resolves with an (int,dict) tuple of
            the file length and a dict of the response headers.

        Raises:
            HttpResponseException: If we get an HTTP response code >= 300
                (except 429).
            NotRetryingDestination: If we are not yet ready to retry this
                server.
            FederationDeniedError: If this destination  is not on our
                federation whitelist
            RequestSendFailed: If there were problems connecting to the
                remote, due to e.g. DNS failures, connection timeouts etc.
        """
        request = MatrixFederationRequest(
            method="GET", destination=destination, path=path, query=args
        )

        response = await self._send_request(
            request, retry_on_dns_fail=retry_on_dns_fail, ignore_backoff=ignore_backoff
        )

        headers = dict(response.headers.getAllRawHeaders())

        try:
            d = read_body_with_max_size(response, output_stream, max_size)
            d.addTimeout(self.default_timeout, self.reactor)
            length = await make_deferred_yieldable(d)
        except BodyExceededMaxSize:
            msg = "Requested file is too large > %r bytes" % (max_size,)
            logger.warning(
                "{%s} [%s] %s", request.txn_id, request.destination, msg,
            )
            SynapseError(502, msg, Codes.TOO_LARGE)
        except Exception as e:
            logger.warning(
                "{%s} [%s] Error reading response: %s",
                request.txn_id,
                request.destination,
                e,
            )
            raise
        logger.info(
            "{%s} [%s] Completed: %d %s [%d bytes] %s %s",
            request.txn_id,
            request.destination,
            response.code,
            response.phrase.decode("ascii", errors="replace"),
            length,
            request.method,
            request.uri.decode("ascii"),
        )
        return (length, headers)