    def is_monotonic_decreasing(self):
        """
        Return boolean if values in the object are monotonically decreasing.

        .. note:: the current implementation of is_monotonic_decreasing uses Spark's
            Window without specifying partition specification. This leads to move all data into
            single partition in single machine and could cause serious
            performance degradation. Avoid this method against very large dataset.

        Returns
        -------
        is_monotonic : boolean

        Examples
        --------
        >>> ser = ks.Series(['4/1/2018', '3/1/2018', '1/1/2018'])
        >>> ser.is_monotonic_decreasing
        True

        >>> df = ks.DataFrame({'dates': [None, '3/1/2018', '2/1/2018', '1/1/2018']})
        >>> df.dates.is_monotonic_decreasing
        False

        >>> df.index.is_monotonic_decreasing
        False

        >>> ser = ks.Series([1])
        >>> ser.is_monotonic_decreasing
        True

        >>> ser = ks.Series([])
        >>> ser.is_monotonic_decreasing
        True
        """
        if len(self._kdf._internal.index_columns) == 0:
            raise ValueError("Index must be set.")

        col = self._scol
        index_columns = self._kdf._internal.index_columns
        window = Window.orderBy(index_columns).rowsBetween(-1, -1)
        sdf = self._kdf._sdf.withColumn(
            "__monotonic_col", (col <= F.lag(col, 1).over(window)) & col.isNotNull())
        kdf = ks.DataFrame(
            self._kdf._internal.copy(
                sdf=sdf, data_columns=self._kdf._internal.data_columns + ["__monotonic_col"]))
        return kdf["__monotonic_col"].all()