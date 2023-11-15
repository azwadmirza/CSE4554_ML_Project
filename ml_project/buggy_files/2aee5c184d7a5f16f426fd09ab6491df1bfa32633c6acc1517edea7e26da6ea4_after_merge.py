    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        self._write_to_hub(self._sid, **{ATTR_CURTAIN_LEVEL: str(position)})