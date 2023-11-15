    async def _request(self, *, http_verb, api_url, req_args):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """
        session = None
        if self.session and not self.session.closed:
            session = self.session
        else:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                auth=req_args.pop("auth", None),
            )

        response = None
        async with session.request(http_verb, api_url, **req_args) as res:
            data = {}
            try:
                data = await res.json()
            except aiohttp.ContentTypeError:
                self._logger.debug(
                    f"No response data returned from the following API call: {api_url}."
                )
            response = {"data": data, "headers": res.headers, "status_code": res.status}

        await session.close()
        return response