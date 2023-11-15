    def __getitem__(self, key):
        if self._selection is not None:
            raise IndexError('Column(s) {selection} already selected'
                             .format(selection=self._selection))

        if isinstance(key, (list, tuple, ABCSeries, ABCIndexClass,
                            np.ndarray)):
            if len(self.obj.columns.intersection(key)) != len(key):
                bad_keys = list(set(key).difference(self.obj.columns))
                raise KeyError("Columns not found: {missing}"
                               .format(missing=str(bad_keys)[1:-1]))
            return self._gotitem(list(key), ndim=2)

        elif not getattr(self, 'as_index', False):
            if key not in self.obj.columns:
                raise KeyError("Column not found: {key}".format(key=key))
            return self._gotitem(key, ndim=2)

        else:
            if key not in self.obj:
                raise KeyError("Column not found: {key}".format(key=key))
            return self._gotitem(key, ndim=1)