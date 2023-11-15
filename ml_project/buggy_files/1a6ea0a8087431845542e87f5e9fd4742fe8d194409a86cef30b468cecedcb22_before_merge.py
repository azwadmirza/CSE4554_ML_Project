    async def async_added_to_hass(self):
        """Perform tasks after loading."""
        # Register event handler on bus
        self._listener = self.hass.bus.async_listen(
            f"{ALEXA_DOMAIN}_{hide_email(self._login.email)}"[0:32], self._handle_event
        )