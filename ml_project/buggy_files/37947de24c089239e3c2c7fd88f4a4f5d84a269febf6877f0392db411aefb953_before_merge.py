        def to_pandas(self):
            data = getattr(self, '_data', None)
            if data is None:
                sortorder = getattr(self, '_sortorder', None)
                return pd.MultiIndex.from_arrays([np.array([], dtype=dtype) for dtype in self._dtypes],
                                                 sortorder=sortorder, names=self._names)
            return pd.MultiIndex.from_tuples([tuple(d) for d in data], sortorder=self._sortorder,
                                             names=self._names)