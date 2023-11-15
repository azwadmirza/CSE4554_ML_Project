    def take(self, indices, axis=0):
        """
        Analogous to ndarray.take, return SparseDataFrame corresponding to
        requested indices along an axis

        Parameters
        ----------
        indices : list / array of ints
        axis : {0, 1}

        Returns
        -------
        taken : SparseDataFrame
        """
        indices = com._ensure_platform_int(indices)
        new_values = self.values.take(indices, axis=axis)
        if axis == 0:
            new_columns = self.columns
            new_index = self.index.take(indices)
        else:
            new_columns = self.columns.take(indices)
            new_index = self.index
        return self._constructor(new_values, index=new_index,
                                 columns=new_columns)