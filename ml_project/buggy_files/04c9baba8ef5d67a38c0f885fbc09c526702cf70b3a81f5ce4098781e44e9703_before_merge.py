    async def _request(self, *, http_verb, api_url, req_args):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """
        if self.session and not self.session.closed:
            async with self.session.request(http_verb, api_url, **req_args) as res:
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }
        async with aiohttp.ClientSession(
            loop=self._event_loop,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            auth=req_args.pop("auth"),
        ) as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }