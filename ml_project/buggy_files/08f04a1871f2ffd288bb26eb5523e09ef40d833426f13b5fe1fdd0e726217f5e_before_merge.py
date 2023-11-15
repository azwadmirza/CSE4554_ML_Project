    def applymap(self, func):
        """
        Apply a function to a Dataframe elementwise.

        This method applies a function that accepts and returns a scalar
        to every element of a DataFrame.

        .. note:: unlike pandas, it is required for `func` to specify return type hint.
            See https://docs.python.org/3/library/typing.html. For instance, as below:

            >>> def function() -> int:
            ...     return 1

        Parameters
        ----------
        func : callable
            Python function, returns a single value from a single value.

        Returns
        -------
        DataFrame
            Transformed DataFrame.

        Examples
        --------
        >>> df = ks.DataFrame([[1, 2.12], [3.356, 4.567]])
        >>> df
               0      1
        0  1.000  2.120
        1  3.356  4.567

        >>> def str_len(x) -> int:
        ...     return len(str(x))
        >>> df.applymap(str_len)
           0  1
        0  3  4
        1  5  5

        >>> def power(x) -> float:
        ...     return x ** 2
        >>> df.applymap(power)
                   0          1
        0   1.000000   4.494400
        1  11.262736  20.857489
        """

        applied = []
        for column in self._internal.data_columns:
            applied.append(self[column].apply(func))

        sdf = self._sdf.select(
            self._internal.index_columns + [c._scol for c in applied])

        internal = self._internal.copy(sdf=sdf, data_columns=[c.name for c in applied])
        return DataFrame(internal)