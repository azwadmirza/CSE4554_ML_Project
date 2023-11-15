    async def async_media_play(self):
        """Send play command."""
        if not (self.state in [STATE_PLAYING, STATE_PAUSED] and self.available):
            return
        if self._playing_parent:
            await self._playing_parent.async_media_play()
        else:
            await self.alexa_api.play()
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()