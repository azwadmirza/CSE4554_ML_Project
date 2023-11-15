    def transform(self, func, *args, **kwargs):
        """
        Call ``func`` producing the same type as `self` with transformed values
        and that has the same axis length as input.

        .. note:: unlike pandas, it is required for `func` to specify return type hint.

        Parameters
        ----------
        func : function or list
            A function or a list of functions to use for transforming the data.
        *args
            Positional arguments to pass to `func`.
        **kwargs
            Keyword arguments to pass to `func`.

        Returns
        -------
        An instance of the same type with `self` that must have the same length as input.

        See Also
        --------
        Series.apply : Invoke function on Series.

        Examples
        --------

        >>> s = ks.Series(range(3))
        >>> s
        0    0
        1    1
        2    2
        Name: 0, dtype: int64

        >>> def sqrt(x) -> float:
        ...    return np.sqrt(x)
        >>> s.transform(sqrt)
        0    0.000000
        1    1.000000
        2    1.414214
        Name: 0, dtype: float32

        Even though the resulting instance must have the same length as the
        input, it is possible to provide several input functions:

        >>> def exp(x) -> float:
        ...    return np.exp(x)
        >>> s.transform([sqrt, exp])
               sqrt       exp
        0  0.000000  1.000000
        1  1.000000  2.718282
        2  1.414214  7.389056

        """
        if isinstance(func, list):
            applied = []
            for f in func:
                applied.append(self.apply(f).rename(f.__name__))

            sdf = self._kdf._sdf.select(
                self._internal.index_scols + [c._scol for c in applied])

            internal = self.to_dataframe()._internal.copy(
                sdf=sdf, data_columns=[c.name for c in applied])

            return DataFrame(internal)
        else:
            return self.apply(func, args=args, **kwargs)