    def has_value(self):
        if isinstance(self._index_value, self.RangeIndex):
            return True
        elif getattr(self, '_data', None) is not None:
            return True
        return False