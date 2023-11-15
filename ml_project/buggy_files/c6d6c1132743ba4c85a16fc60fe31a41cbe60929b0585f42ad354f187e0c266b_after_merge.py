    async def connect(self):
        """Connect to Telegram.

        This method is not an authorization call. It basically
        checks if the API token was provided and makes an API
        call to Telegram and evaluates the status of the call.

        """
        _LOGGER.debug("Connecting to telegram")
        self.session = aiohttp.ClientSession()
        resp = await self.session.get(self.build_url("getMe"))

        if resp.status != 200:
            _LOGGER.error("Unable to connect")
            _LOGGER.error("Telegram error %s, %s",
                          resp.status, resp.text)
        else:
            json = await resp.json()
            _LOGGER.debug(json)
            _LOGGER.debug("Connected to telegram as %s",
                          json["result"]["username"])