        def to_pandas(self):
            data = getattr(self, '_data', None)
            if data is None:
                sortorder = getattr(self, '_sortorder', None)
                return pd.MultiIndex.from_arrays([[] for _ in range(len(self._names))],
                                                 sortorder=sortorder, names=self._names)
            return pd.MultiIndex.from_tuples([tuple(d) for d in data], sortorder=self._sortorder,
                                             names=self._names)