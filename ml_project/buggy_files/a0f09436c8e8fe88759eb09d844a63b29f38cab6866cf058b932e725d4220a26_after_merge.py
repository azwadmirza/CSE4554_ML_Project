    async def api_request(self, path, method='GET', body=None, client=None):
        """Make an authenticated API request of the proxy."""
        client = client or AsyncHTTPClient()
        url = url_path_join(self.api_url, 'api/routes', path)

        if isinstance(body, dict):
            body = json.dumps(body)
        self.log.debug("Proxy: Fetching %s %s", method, url)
        req = HTTPRequest(
            url,
            method=method,
            headers={'Authorization': 'token {}'.format(self.auth_token)},
            body=body,
            connect_timeout=3,  # default: 20s
            request_timeout=10,  # default: 20s
        )

        async def _wait_for_api_request():
            try:
                async with self.semaphore:
                    return await client.fetch(req)
            except HTTPError as e:
                # Retry on potentially transient errors in CHP, typically
                # numbered 500 and up. Note that CHP isn't able to emit 429
                # errors.
                if e.code >= 500:
                    self.log.warning(
                        "api_request to the proxy failed with status code {}, retrying...".format(
                            e.code
                        )
                    )
                    return False  # a falsy return value make exponential_backoff retry
                else:
                    self.log.error("api_request to proxy failed: {0}".format(e))
                    # An unhandled error here will help the hub invoke cleanup logic
                    raise

        result = await exponential_backoff(
            _wait_for_api_request,
            'Repeated api_request to proxy path "{}" failed.'.format(path),
            timeout=30,
        )
        return result