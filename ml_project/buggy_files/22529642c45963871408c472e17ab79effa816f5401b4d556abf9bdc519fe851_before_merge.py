    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            key = tuple(com.apply_if_callable(x, self.obj) for x in key)
        else:
            # scalar callable may return tuple
            key = com.apply_if_callable(key, self.obj)

        if not isinstance(key, tuple):
            key = _tuplify(self.ndim, key)
        if len(key) != self.ndim:
            raise ValueError("Not enough indexers for scalar access (setting)!")
        key = list(self._convert_key(key, is_setter=True))
        self.obj._set_value(*key, value=value, takeable=self._takeable)