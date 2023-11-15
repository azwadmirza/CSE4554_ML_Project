    def append(self, other: 'DataFrame', ignore_index: bool = False,
               verify_integrity: bool = False, sort: bool = False) -> 'DataFrame':
        """
        Append rows of other to the end of caller, returning a new object.

        Columns in other that are not in the caller are added as new columns.

        Parameters
        ----------
        other : DataFrame or Series/dict-like object, or list of these
            The data to append.

        ignore_index : boolean, default False
            If True, do not use the index labels.

        verify_integrity : boolean, default False
            If True, raise ValueError on creating index with duplicates.

        sort : boolean, default False
            Currently not supported.

        Returns
        -------
        appended : DataFrame

        Examples
        --------
        >>> df = ks.DataFrame([[1, 2], [3, 4]], columns=list('AB'))

        >>> df.append(df)
           A  B
        0  1  2
        1  3  4
        0  1  2
        1  3  4

        >>> df.append(df, ignore_index=True)
           A  B
        0  1  2
        1  3  4
        2  1  2
        3  3  4
        """
        if isinstance(other, ks.Series):
            raise ValueError("DataFrames.append() does not support appending Series to DataFrames")
        if sort:
            raise ValueError("The 'sort' parameter is currently not supported")

        if not ignore_index:
            index_scols = self._internal.index_scols
            if len(index_scols) != len(other._internal.index_scols):
                raise ValueError("Both DataFrames have to have the same number of index levels")

            if verify_integrity and len(index_scols) > 0:
                if (self._sdf.select(index_scols)
                        .intersect(other._sdf.select(other._internal.index_scols))
                        .count()) > 0:
                    raise ValueError("Indices have overlapping values")

        # Lazy import to avoid circular dependency issues
        from databricks.koalas.namespace import concat
        return concat([self, other], ignore_index=ignore_index)