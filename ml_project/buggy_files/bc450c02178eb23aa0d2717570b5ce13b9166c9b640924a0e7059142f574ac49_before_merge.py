    def __setstate__(self, state):
        self._crs = _CRS.from_wkt(state)