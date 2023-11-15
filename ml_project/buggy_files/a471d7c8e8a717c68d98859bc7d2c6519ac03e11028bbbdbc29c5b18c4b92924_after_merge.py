    async def post_call(
        self, url: str, payload: MutableMapping, headers: MutableMapping = None
    ) -> MutableMapping[str, Union[str, int]]:
        async with self.session.post(url, data=payload, headers=headers) as r:
            if r.status != 200:
                log.debug(
                    "Issue making POST request to {0}: [{1.status}] {2}".format(
                        url, r, await r.json()
                    )
                )
            return await r.json()