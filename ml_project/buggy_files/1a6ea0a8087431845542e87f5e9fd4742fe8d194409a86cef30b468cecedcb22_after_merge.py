    async def async_added_to_hass(self):
        """Perform tasks after loading."""
        # Register event handler on bus
        self._listener = async_dispatcher_connect(
            self.hass,
            f"{ALEXA_DOMAIN}_{hide_email(self._login.email)}"[0:32],
            self._handle_event,
        )