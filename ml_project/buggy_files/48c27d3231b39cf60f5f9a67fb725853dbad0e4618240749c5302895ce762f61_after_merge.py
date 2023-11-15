    def _allocated(self):
        if not self._typed:
            return DEFAULT_ALLOCATED
        else:
            return _allocated(self)