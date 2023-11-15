    async def async_turn_on(self):
        """Turn the client on.

        While Alexa's do not have on/off capability, we can use this as another
        trigger to do updates.
        """
        self.check_login_changes()
        self._should_poll = True
        await self.async_media_pause()