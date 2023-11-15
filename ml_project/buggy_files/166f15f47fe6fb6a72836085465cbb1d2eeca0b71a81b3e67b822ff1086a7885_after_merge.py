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
        data = {}
        if self.latest_update is not None:
            data["offset"] = self.latest_update

        await asyncio.sleep(self.update_interval)
        resp = await self.session.get(self.build_url("getUpdates"),
                                      params=data)

        if resp.status == 409:
            _LOGGER.info("Can't get updates because previous "
                         "webhook is still active. Will try to "
                         "delete webhook.")
            await self.delete_webhook()

        if resp.status != 200:
            _LOGGER.error("Telegram error %s, %s",
                          resp.status, resp.text)
            self.listening = False
        else:
            json = await resp.json()

            await self._parse_message(json)