    def __del__(self):
        """Cleanup GEOS related processes"""
        if self._lgeos is not None:
            self._lgeos.finishGEOS()
            self._lgeos = None
            self.geos_handle = None