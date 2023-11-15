    def _handle_event(self, event):
        """Handle websocket events.

        Used instead of polling.
        """
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        if "push_activity" in event.data:
            async_call_later(
                self.hass,
                2,
                lambda _: self.hass.async_create_task(
                    self.async_update(no_throttle=True)
                ),
            )