    def reindex(self, index=None, method=None, copy=True):
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

        if len(self.index) == 0:
            # FIXME: inelegant / slow
            values = np.empty(len(new_index), dtype=np.float64)
            values.fill(nan)
            return SparseSeries(values, index=new_index,
                                fill_value=self.fill_value)

        new_index, fill_vec = self.index.reindex(index, method=method)
        new_values = common.take_1d(self.values, fill_vec)
        return SparseSeries(new_values, index=new_index,
                            fill_value=self.fill_value, name=self.name)