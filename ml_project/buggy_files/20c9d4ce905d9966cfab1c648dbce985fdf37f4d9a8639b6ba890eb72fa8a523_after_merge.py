    async def async_mute_volume(self, mute):
        """Mute the volume.

        Since we can't actually mute, we'll:
        - On mute, store volume and set volume to 0
        - On unmute, set volume to previously stored volume
        """
        self.check_login_changes()
        if not self.available:
            return

        self._media_is_muted = mute
        if mute:
            self._previous_volume = self.volume_level
            await self.alexa_api.set_volume(0)
        else:
            if self._previous_volume is not None:
                await self.alexa_api.set_volume(self._previous_volume)
            else:
                await self.alexa_api.set_volume(50)
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()