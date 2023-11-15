    def add_suffix(self, suffix):
        """
        Suffix labels with string suffix.

        For Series, the row labels are suffixed.
        For DataFrame, the column labels are suffixed.

        Parameters
        ----------
        suffix : str
           The string to add after each label.

        Returns
        -------
        Series
           New Series with updated labels.

        See Also
        --------
        Series.add_prefix: Prefix row labels with string `prefix`.
        DataFrame.add_prefix: Prefix column labels with string `prefix`.
        DataFrame.add_suffix: Suffix column labels with string `suffix`.

        Examples
        --------
        >>> s = ks.Series([1, 2, 3, 4])
        >>> s
        0    1
        1    2
        2    3
        3    4
        Name: 0, dtype: int64

        >>> s.add_suffix('_item')
        0_item    1
        1_item    2
        2_item    3
        3_item    4
        Name: 0, dtype: int64
        """
        assert isinstance(suffix, str)
        kdf = self.to_dataframe()
        internal = kdf._internal
        sdf = internal.sdf
        sdf = sdf.select([F.concat(scol_for(sdf, index_column),
                                   F.lit(suffix)).alias(index_column)
                          for index_column in internal.index_columns] + internal.data_columns)
        kdf._internal = internal.copy(sdf=sdf)
        return Series(kdf._internal.copy(scol=self._scol), anchor=kdf)