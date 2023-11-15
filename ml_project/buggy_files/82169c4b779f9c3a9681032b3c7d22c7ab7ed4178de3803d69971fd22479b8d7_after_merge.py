    async def async_select_source(self, source):
        """Select input source."""
        self.check_login_changes()
        if source == "Local Speaker":
            await self.alexa_api.disconnect_bluetooth()
            self._source = "Local Speaker"
        elif self._bluetooth_state["pairedDeviceList"] is not None:
            for devices in self._bluetooth_state["pairedDeviceList"]:
                if devices["friendlyName"] == source:
                    await self.alexa_api.set_bluetooth(devices["address"])
                    self._source = source
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()