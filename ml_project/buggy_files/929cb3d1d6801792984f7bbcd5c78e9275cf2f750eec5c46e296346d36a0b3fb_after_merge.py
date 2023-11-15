    async def is_online(self):
        if not self._token:
            raise InvalidYoutubeCredentials("YouTube API key is not set.")

        if not self.id:
            self.id = await self.fetch_id()
        elif not self.name:
            self.name = await self.fetch_name()

        url = YOUTUBE_SEARCH_ENDPOINT
        params = {
            "key": self._token,
            "part": "snippet",
            "channelId": self.id,
            "type": "video",
            "eventType": "live",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                data = await r.json()
        if "items" in data and len(data["items"]) == 0:
            raise OfflineStream()
        elif "items" in data:
            vid_id = data["items"][0]["id"]["videoId"]
            params = {"key": self._token, "id": vid_id, "part": "snippet"}
            async with aiohttp.ClientSession() as session:
                async with session.get(YOUTUBE_VIDEOS_ENDPOINT, params=params) as r:
                    data = await r.json()
            return self.make_embed(data)