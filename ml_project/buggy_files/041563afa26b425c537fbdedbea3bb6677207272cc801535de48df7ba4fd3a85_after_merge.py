    def media_play(self):
        """Send play command."""
        if not (self.state in [STATE_PLAYING, STATE_PAUSED]
                and self.available):
            return
        self.alexa_api.play()
        if not (self.hass.data[DATA_ALEXAMEDIA]
                ['accounts'][self._login.email]['websocket']):
            self.update()