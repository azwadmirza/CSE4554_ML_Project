    def open_cover(self, **kwargs):
        """Open the cover."""
        self._write_to_hub(self._sid, **{self._data_key['status']: 'open'})