    def _get_setitem_indexer(self, key):
        if self.axis is not None:
            return self._convert_tuple(key, is_setter=True)

        axis = self.obj._get_axis(0)
        if isinstance(axis, MultiIndex):
            try:
                return axis.get_loc(key)
            except Exception:
                pass

        if isinstance(key, tuple) and not self.ndim < len(key):
            return self._convert_tuple(key, is_setter=True)
        if isinstance(key, range):
            return self._convert_range(key, is_setter=True)

        try:
            return self._convert_to_indexer(key, is_setter=True)
        except TypeError:
            raise IndexingError(key)