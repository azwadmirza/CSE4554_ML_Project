    def shift(self, periods=1, fill_value=None):
        """
        Shift Series/Index by desired number of periods.

        .. note:: the current implementation of shift uses Spark's Window without
            specifying partition specification. This leads to move all data into
            single partition in single machine and could cause serious
            performance degradation. Avoid this method against very large dataset.

        Parameters
        ----------
        periods : int
            Number of periods to shift. Can be positive or negative.
        fill_value : object, optional
            The scalar value to use for newly introduced missing values.
            The default depends on the dtype of self. For numeric data, np.nan is used.

        Returns
        -------
        Copy of input Series/Index, shifted.

        Examples
        --------
        >>> df = ks.DataFrame({'Col1': [10, 20, 15, 30, 45],
        ...                    'Col2': [13, 23, 18, 33, 48],
        ...                    'Col3': [17, 27, 22, 37, 52]},
        ...                   columns=['Col1', 'Col2', 'Col3'])

        >>> df.Col1.shift(periods=3)
        0     NaN
        1     NaN
        2     NaN
        3    10.0
        4    20.0
        Name: Col1, dtype: float64

        >>> df.Col2.shift(periods=3, fill_value=0)
        0     0
        1     0
        2     0
        3    13
        4    23
        Name: Col2, dtype: int64

        """
        if len(self._internal.index_columns) == 0:
            raise ValueError("Index must be set.")

        if not isinstance(periods, int):
            raise ValueError('periods should be an int; however, got [%s]' % type(periods))

        col = self._scol
        index_columns = self._kdf._internal.index_columns
        window = Window.orderBy(index_columns).rowsBetween(-periods, -periods)
        shifted_col = F.lag(col, periods).over(window)
        col = F.when(
            shifted_col.isNull() | F.isnan(shifted_col), fill_value
        ).otherwise(shifted_col)

        return self._with_new_scol(col).alias(self.name)