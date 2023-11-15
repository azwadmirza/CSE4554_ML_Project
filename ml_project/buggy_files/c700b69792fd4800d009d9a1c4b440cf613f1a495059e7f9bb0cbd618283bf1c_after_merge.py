    async def async_media_previous_track(self):
        """Send previous track command."""
        self.check_login_changes()
        if not (self.state in [STATE_PLAYING, STATE_PAUSED] and self.available):
            return
        if self._playing_parent:
            await self._playing_parent.async_media_previous_track()
        else:
            await self.alexa_api.previous()
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()