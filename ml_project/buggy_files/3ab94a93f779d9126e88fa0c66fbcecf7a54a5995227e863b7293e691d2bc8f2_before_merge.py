    def reindex(self, index=None, method=None, copy=True, limit=None):
        """
        Conform SparseSeries to new Index

        See Series.reindex docstring for general behavior

        Returns
        -------
        reindexed : SparseSeries
        """
        new_index = _ensure_index(index)

        if self.index.equals(new_index):
            if copy:
                return self.copy()
            else:
                return self
        return self._constructor(self._data.reindex(new_index, method=method,
                                                    limit=limit, copy=copy),
                                 index=new_index).__finalize__(self)