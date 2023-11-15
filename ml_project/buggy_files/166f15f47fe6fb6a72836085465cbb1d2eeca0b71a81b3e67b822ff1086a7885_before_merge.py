    async def _get_messages(self):
        """Connect to the Telegram API.

        Uses an aiohttp ClientSession to connect to Telegram API
        and get the latest messages from the chat service.

        The data["offset"] is used to consume every new message, the API
        returns an  int - "update_id" value. In order to get the next
        message this value needs to be increased by 1 the next time
        the API is called. If no new messages exists the API will just
        return an empty {}.

        """
        async with aiohttp.ClientSession() as session:
            data = {}
            if self.latest_update is not None:
                data["offset"] = self.latest_update
            resp = await session.get(self.build_url("getUpdates"),
                                     params=data)
            if resp.status != 200:
                _LOGGER.error("Telegram error %s, %s",
                              resp.status, resp.text)
                self.listening = False

            else:
                json = await resp.json()

                await self._parse_message(json)