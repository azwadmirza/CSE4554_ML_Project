    def add_prefix(self, prefix):
        """
        Prefix labels with string `prefix`.

        For Series, the row labels are prefixed.
        For DataFrame, the column labels are prefixed.

        Parameters
        ----------
        prefix : str
           The string to add before each label.

        Returns
        -------
        Series
           New Series with updated labels.

        See Also
        --------
        Series.add_suffix: Suffix column labels with string `suffix`.
        DataFrame.add_suffix: Suffix column labels with string `suffix`.
        DataFrame.add_prefix: Prefix column labels with string `prefix`.

        Examples
        --------
        >>> s = ks.Series([1, 2, 3, 4])
        >>> s
        0    1
        1    2
        2    3
        3    4
        Name: 0, dtype: int64

        >>> s.add_prefix('item_')
        item_0    1
        item_1    2
        item_2    3
        item_3    4
        Name: 0, dtype: int64
        """
        assert isinstance(prefix, str)
        kdf = self.to_dataframe()
        internal = kdf._internal
        sdf = internal.sdf
        sdf = sdf.select([F.concat(F.lit(prefix), sdf[index_column]).alias(index_column)
                          for index_column in internal.index_columns] + internal.data_columns)
        kdf._internal = internal.copy(sdf=sdf)
        return Series(kdf._internal.copy(scol=self._scol), anchor=kdf)