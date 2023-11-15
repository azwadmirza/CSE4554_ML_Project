    def join(
        self,
        right: "DataFrame",
        on: Optional[Union[str, List[str], Tuple[str, ...], List[Tuple[str, ...]]]] = None,
        how: str = "left",
        lsuffix: str = "",
        rsuffix: str = "",
    ) -> "DataFrame":
        """
        Join columns of another DataFrame.

        Join columns with `right` DataFrame either on index or on a key column. Efficiently join
        multiple DataFrame objects by index at once by passing a list.

        Parameters
        ----------
        right: DataFrame, Series
        on: str, list of str, or array-like, optional
            Column or index level name(s) in the caller to join on the index in `right`, otherwise
            joins index-on-index. If multiple values given, the `right` DataFrame must have a
            MultiIndex. Can pass an array as the join key if it is not already contained in the
            calling DataFrame. Like an Excel VLOOKUP operation.
        how: {'left', 'right', 'outer', 'inner'}, default 'left'
            How to handle the operation of the two objects.

            * left: use `left` frame’s index (or column if on is specified).
            * right: use `right`’s index.
            * outer: form union of `left` frame’s index (or column if on is specified) with
              right’s index, and sort it. lexicographically.
            * inner: form intersection of `left` frame’s index (or column if on is specified)
              with `right`’s index, preserving the order of the `left`’s one.
        lsuffix : str, default ''
            Suffix to use from left frame's overlapping columns.
        rsuffix : str, default ''
            Suffix to use from `right` frame's overlapping columns.

        Returns
        -------
        DataFrame
            A dataframe containing columns from both the `left` and `right`.

        See Also
        --------
        DataFrame.merge: For column(s)-on-columns(s) operations.
        DataFrame.update : Modify in place using non-NA values from another DataFrame.
        DataFrame.hint : Specifies some hint on the current DataFrame.
        broadcast : Marks a DataFrame as small enough for use in broadcast joins.

        Notes
        -----
        Parameters on, lsuffix, and rsuffix are not supported when passing a list of DataFrame
        objects.

        Examples
        --------
        >>> kdf1 = ks.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
        ...                      'A': ['A0', 'A1', 'A2', 'A3']},
        ...                     columns=['key', 'A'])
        >>> kdf2 = ks.DataFrame({'key': ['K0', 'K1', 'K2'],
        ...                      'B': ['B0', 'B1', 'B2']},
        ...                     columns=['key', 'B'])
        >>> kdf1
          key   A
        0  K0  A0
        1  K1  A1
        2  K2  A2
        3  K3  A3
        >>> kdf2
          key   B
        0  K0  B0
        1  K1  B1
        2  K2  B2

        Join DataFrames using their indexes.

        >>> join_kdf = kdf1.join(kdf2, lsuffix='_left', rsuffix='_right')
        >>> join_kdf.sort_values(by=join_kdf.columns)
          key_left   A key_right     B
        0       K0  A0        K0    B0
        1       K1  A1        K1    B1
        2       K2  A2        K2    B2
        3       K3  A3      None  None

        If we want to join using the key columns, we need to set key to be the index in both df and
        right. The joined DataFrame will have key as its index.

        >>> join_kdf = kdf1.set_index('key').join(kdf2.set_index('key'))
        >>> join_kdf.sort_values(by=join_kdf.columns) # doctest: +NORMALIZE_WHITESPACE
              A     B
        key
        K0   A0    B0
        K1   A1    B1
        K2   A2    B2
        K3   A3  None

        Another option to join using the key columns is to use the on parameter. DataFrame.join
        always uses right’s index but we can use any column in df. This method not preserve the
        original DataFrame’s index in the result unlike pandas.

        >>> join_kdf = kdf1.join(kdf2.set_index('key'), on='key')
        >>> join_kdf.index
        Int64Index([0, 1, 2, 3], dtype='int64')
        """
        if isinstance(right, ks.Series):
            common = list(self.columns.intersection([right.name]))
        else:
            common = list(self.columns.intersection(right.columns))
        if len(common) > 0 and not lsuffix and not rsuffix:
            raise ValueError(
                "columns overlap but no suffix specified: " "{rename}".format(rename=common)
            )
        if on:
            self = self.set_index(on)
            join_kdf = self.merge(
                right, left_index=True, right_index=True, how=how, suffixes=(lsuffix, rsuffix)
            ).reset_index()
        else:
            join_kdf = self.merge(
                right, left_index=True, right_index=True, how=how, suffixes=(lsuffix, rsuffix)
            )
        return join_kdf