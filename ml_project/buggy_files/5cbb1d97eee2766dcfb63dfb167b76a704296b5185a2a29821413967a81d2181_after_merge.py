    def media_next_track(self):
        """Send next track command."""
        if not (self.state in [STATE_PLAYING, STATE_PAUSED]
                and self.available):
            return
        self.alexa_api.next()
        if not (self.hass.data[DATA_ALEXAMEDIA]
                ['accounts'][self._login.email]['websocket']):
            self.update()