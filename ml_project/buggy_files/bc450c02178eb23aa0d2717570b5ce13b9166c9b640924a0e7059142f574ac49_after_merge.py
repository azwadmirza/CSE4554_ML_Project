    def __setstate__(self, state):
        self._wkt = None
        self._data = None
        self._crs = _CRS.from_wkt(state)