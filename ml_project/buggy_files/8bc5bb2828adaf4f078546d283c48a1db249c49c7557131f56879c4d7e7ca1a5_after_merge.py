    def close_cover(self, **kwargs):
        """Close the cover."""
        self._write_to_hub(self._sid, **{self._data_key: 'close'})