    async def async_media_stop(self):
        """Send stop command."""
        self.check_login_changes()
        if not self.available:
            return
        if self._playing_parent:
            await self._playing_parent.async_media_stop()
        else:
            await self.alexa_api.stop(
                customer_id=self._customer_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ][CONF_QUEUE_DELAY],
            )
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()