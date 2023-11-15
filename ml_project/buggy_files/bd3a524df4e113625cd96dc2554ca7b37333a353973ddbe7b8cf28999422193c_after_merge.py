    def transform(self, func):
        """
        Call ``func`` on self producing a Series with transformed values
        and that has the same length as its input.

        .. note:: unlike pandas, it is required for ``func`` to specify return type hint.

        .. note:: the series within ``func`` is actually a pandas series, and
            the length of each series is not guaranteed.

        Parameters
        ----------
        func : function
            Function to use for transforming the data. It must work when pandas Series
            is passed.

        Returns
        -------
        DataFrame
            A DataFrame that must have the same length as self.

        Raises
        ------
        Exception : If the returned DataFrame has a different length than self.

        Examples
        --------
        >>> df = ks.DataFrame({'A': range(3), 'B': range(1, 4)}, columns=['A', 'B'])
        >>> df
           A  B
        0  0  1
        1  1  2
        2  2  3

        >>> def square(x) -> ks.Series[np.int32]:
        ...     return x ** 2
        >>> df.transform(square)
           A  B
        0  0  1
        1  1  4
        2  4  9
        """
        assert callable(func), "the first argument should be a callable function."
        spec = inspect.getfullargspec(func)
        return_sig = spec.annotations.get("return", None)
        if return_sig is None:
            raise ValueError("Given function must have return type hint; however, not found.")

        wrapped = ks.pandas_wraps(func)
        applied = []
        for column in self._internal.data_columns:
            applied.append(wrapped(self[column]).rename(column))

        sdf = self._sdf.select(
            self._internal.index_scols + [c._scol for c in applied])
        internal = self._internal.copy(sdf=sdf)

        return DataFrame(internal)