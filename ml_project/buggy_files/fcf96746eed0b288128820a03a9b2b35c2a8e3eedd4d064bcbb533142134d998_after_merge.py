    async def async_media_pause(self):
        """Send pause command."""
        self.check_login_changes()
        if not (self.state in [STATE_PLAYING, STATE_PAUSED] and self.available):
            return
        if self._playing_parent:
            await self._playing_parent.async_media_pause()
        else:
            await self.alexa_api.pause()
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()