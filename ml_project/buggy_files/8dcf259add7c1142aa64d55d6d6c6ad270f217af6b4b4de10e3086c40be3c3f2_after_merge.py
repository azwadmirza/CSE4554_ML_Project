    def _init_data_struct(self):
        """Generate a data dictionary (self._data) from metadata."""
        self._state = "LEVEL"
        self._data.update({self._state: None})
        if "LEVEL_2" in self._hmdevice.WRITENODE:
            self._data.update({"LEVEL_2": None})