    def _allocated(self):
        if not self._typed:
            return 0
        else:
            return _allocated(self)