    async def get_call(
        self, url: str, params: MutableMapping
    ) -> MutableMapping[str, Union[str, int]]:
        token = await self._get_spotify_token()
        return await self._make_get(
            url, params=params, headers={"Authorization": "Bearer {0}".format(token)}
        )