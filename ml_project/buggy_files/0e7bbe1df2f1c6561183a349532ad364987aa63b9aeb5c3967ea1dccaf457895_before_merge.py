    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if not self.available:
            return
        await self.alexa_api.set_volume(volume)
        self._media_vol_level = volume
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()