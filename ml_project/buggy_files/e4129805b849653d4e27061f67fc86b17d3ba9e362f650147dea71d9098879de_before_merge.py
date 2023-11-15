    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._write_to_hub(self._sid, **{self._data_key['status']: 'stop'})