    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if not self.available:
            return
        self.alexa_api.set_volume(volume)
        self._media_vol_level = volume
        self.update()