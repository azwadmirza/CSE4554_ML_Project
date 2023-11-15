    async def request(
        self,
        method: Text = "post",
        subpath: Optional[Text] = None,
        content_type: Optional[Text] = "application/json",
        return_method: Text = "json",
        **kwargs: Any,
    ):
        """Send a HTTP request to the endpoint.

        All additional arguments will get passed through
        to aiohttp's `session.request`."""

        # create the appropriate headers
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type

        if "headers" in kwargs:
            headers.update(kwargs["headers"])
            del kwargs["headers"]

        url = concat_url(self.url, subpath)
        async with self.session() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                params=self.combine_parameters(kwargs),
                **kwargs,
            ) as resp:
                if resp.status >= 400:
                    raise ClientResponseError(
                        resp.status, resp.reason, await resp.content.read()
                    )
                return await getattr(resp, return_method)()