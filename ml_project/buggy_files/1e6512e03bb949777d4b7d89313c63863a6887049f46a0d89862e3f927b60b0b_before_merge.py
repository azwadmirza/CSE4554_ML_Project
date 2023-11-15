    def merge(self, right: 'DataFrame', how: str = 'inner',
              on: Optional[Union[str, List[str]]] = None,
              left_on: Optional[Union[str, List[str]]] = None,
              right_on: Optional[Union[str, List[str]]] = None,
              left_index: bool = False, right_index: bool = False,
              suffixes: Tuple[str, str] = ('_x', '_y')) -> 'DataFrame':
        """
        Merge DataFrame objects with a database-style join.

        The index of the resulting DataFrame will be one of the following:
            - 0...n if no index is used for merging
            - Index of the left DataFrame if merged only on the index of the right DataFrame
            - Index of the right DataFrame if merged only on the index of the left DataFrame
            - All involved indices if merged using the indices of both DataFrames
                e.g. if `left` with indices (a, x) and `right` with indices (b, x), the result will
                be an index (x, a, b)

        Parameters
        ----------
        right: Object to merge with.
        how: Type of merge to be performed.
            {'left', 'right', 'outer', 'inner'}, default 'inner'

            left: use only keys from left frame, similar to a SQL left outer join; preserve key
                order.
            right: use only keys from right frame, similar to a SQL right outer join; preserve key
                order.
            outer: use union of keys from both frames, similar to a SQL full outer join; sort keys
                lexicographically.
            inner: use intersection of keys from both frames, similar to a SQL inner join;
                preserve the order of the left keys.
        on: Column or index level names to join on. These must be found in both DataFrames. If on
            is None and not merging on indexes then this defaults to the intersection of the
            columns in both DataFrames.
        left_on: Column or index level names to join on in the left DataFrame. Can also
            be an array or list of arrays of the length of the left DataFrame.
            These arrays are treated as if they are columns.
        right_on: Column or index level names to join on in the right DataFrame. Can also
            be an array or list of arrays of the length of the right DataFrame.
            These arrays are treated as if they are columns.
        left_index: Use the index from the left DataFrame as the join key(s). If it is a
            MultiIndex, the number of keys in the other DataFrame (either the index or a number of
            columns) must match the number of levels.
        right_index: Use the index from the right DataFrame as the join key. Same caveats as
            left_index.
        suffixes: Suffix to apply to overlapping column names in the left and right side,
            respectively.

        Returns
        -------
        DataFrame
            A DataFrame of the two merged objects.

        Examples
        --------
        >>> df1 = ks.DataFrame({'lkey': ['foo', 'bar', 'baz', 'foo'],
        ...                     'value': [1, 2, 3, 5]},
        ...                    columns=['lkey', 'value'])
        >>> df2 = ks.DataFrame({'rkey': ['foo', 'bar', 'baz', 'foo'],
        ...                     'value': [5, 6, 7, 8]},
        ...                    columns=['rkey', 'value'])
        >>> df1
          lkey  value
        0  foo      1
        1  bar      2
        2  baz      3
        3  foo      5
        >>> df2
          rkey  value
        0  foo      5
        1  bar      6
        2  baz      7
        3  foo      8

        Merge df1 and df2 on the lkey and rkey columns. The value columns have
        the default suffixes, _x and _y, appended.

        >>> merged = df1.merge(df2, left_on='lkey', right_on='rkey')
        >>> merged.sort_values(by=['lkey', 'value_x', 'rkey', 'value_y'])
          lkey  value_x rkey  value_y
        0  bar        2  bar        6
        1  baz        3  baz        7
        2  foo        1  foo        5
        3  foo        1  foo        8
        4  foo        5  foo        5
        5  foo        5  foo        8

        >>> left_kdf = ks.DataFrame({'A': [1, 2]})
        >>> right_kdf = ks.DataFrame({'B': ['x', 'y']}, index=[1, 2])

        >>> left_kdf.merge(right_kdf, left_index=True, right_index=True)
           A  B
        1  2  x

        >>> left_kdf.merge(right_kdf, left_index=True, right_index=True, how='left')
           A     B
        0  1  None
        1  2     x

        >>> left_kdf.merge(right_kdf, left_index=True, right_index=True, how='right')
             A  B
        1  2.0  x
        2  NaN  y

        >>> left_kdf.merge(right_kdf, left_index=True, right_index=True, how='outer')
             A     B
        0  1.0  None
        1  2.0     x
        2  NaN     y

        Notes
        -----
        As described in #263, joining string columns currently returns None for missing values
            instead of NaN.
        """
        _to_list = lambda o: o if o is None or is_list_like(o) else [o]

        if on:
            if left_on or right_on:
                raise ValueError('Can only pass argument "on" OR "left_on" and "right_on", '
                                 'not a combination of both.')
            left_keys = _to_list(on)
            right_keys = _to_list(on)
        else:
            # TODO: need special handling for multi-index.
            if left_index:
                left_keys = self._internal.index_columns
            else:
                left_keys = _to_list(left_on)
            if right_index:
                right_keys = right._internal.index_columns
            else:
                right_keys = _to_list(right_on)

            if left_keys and not right_keys:
                raise ValueError('Must pass right_on or right_index=True')
            if right_keys and not left_keys:
                raise ValueError('Must pass left_on or left_index=True')
            if not left_keys and not right_keys:
                common = list(self.columns.intersection(right.columns))
                if len(common) == 0:
                    raise ValueError(
                        'No common columns to perform merge on. Merge options: '
                        'left_on=None, right_on=None, left_index=False, right_index=False')
                left_keys = common
                right_keys = common
            if len(left_keys) != len(right_keys):  # type: ignore
                raise ValueError('len(left_keys) must equal len(right_keys)')

        if how == 'full':
            warnings.warn("Warning: While Koalas will accept 'full', you should use 'outer' " +
                          "instead to be compatible with the pandas merge API", UserWarning)
        if how == 'outer':
            # 'outer' in pandas equals 'full' in Spark
            how = 'full'
        if how not in ('inner', 'left', 'right', 'full'):
            raise ValueError("The 'how' parameter has to be amongst the following values: ",
                             "['inner', 'left', 'right', 'outer']")

        left_table = self._sdf.alias('left_table')
        right_table = right._sdf.alias('right_table')

        left_key_columns = [left_table[col] for col in left_keys]  # type: ignore
        right_key_columns = [right_table[col] for col in right_keys]  # type: ignore

        join_condition = reduce(lambda x, y: x & y,
                                [lkey == rkey for lkey, rkey
                                 in zip(left_key_columns, right_key_columns)])

        joined_table = left_table.join(right_table, join_condition, how=how)

        # Unpack suffixes tuple for convenience
        left_suffix = suffixes[0]
        right_suffix = suffixes[1]

        # Append suffixes to columns with the same name to avoid conflicts later
        duplicate_columns = (set(self._internal.data_columns)
                             & set(right._internal.data_columns))

        left_index_columns = set(self._internal.index_columns)
        right_index_columns = set(right._internal.index_columns)

        exprs = []
        for col in left_table.columns:
            if col in left_index_columns:
                continue
            scol = left_table[col]
            if col in duplicate_columns:
                if col in left_keys and col in right_keys:
                    pass
                else:
                    col = col + left_suffix
                    scol = scol.alias(col)
            exprs.append(scol)
        for col in right_table.columns:
            if col in right_index_columns:
                continue
            scol = right_table[col]
            if col in duplicate_columns:
                if col in left_keys and col in right_keys:
                    continue
                else:
                    col = col + right_suffix
                    scol = scol.alias(col)
            exprs.append(scol)

        # Retain indices if they are used for joining
        if left_index:
            if right_index:
                exprs.extend(['left_table.%s' % col for col in left_index_columns])
                exprs.extend(['right_table.%s' % col for col in right_index_columns])
                index_map = self._internal.index_map + [idx for idx in right._internal.index_map
                                                        if idx not in self._internal.index_map]
            else:
                exprs.extend(['right_table.%s' % col for col in right_index_columns])
                index_map = right._internal.index_map
        elif right_index:
            exprs.extend(['left_table.%s' % col for col in left_index_columns])
            index_map = self._internal.index_map
        else:
            index_map = []

        selected_columns = joined_table.select(*exprs)

        # Merge left and right indices after the join by replacing missing values in the left index
        # with values from the right index and dropping
        if (how == 'right' or how == 'full') and right_index:
            for left_index_col, right_index_col in zip(self._internal.index_columns,
                                                       right._internal.index_columns):
                selected_columns = selected_columns.withColumn(
                    'left_table.' + left_index_col,
                    F.when(F.col('left_table.%s' % left_index_col).isNotNull(),
                           F.col('left_table.%s' % left_index_col))
                    .otherwise(F.col('right_table.%s' % right_index_col))
                ).withColumnRenamed(
                    'left_table.%s' % left_index_col, left_index_col
                ).drop(F.col('left_table.%s' % left_index_col))
        if not (left_index and not right_index):
            selected_columns = selected_columns.drop(*[F.col('right_table.%s' % right_index_col)
                                                       for right_index_col in right_index_columns
                                                       if right_index_col in left_index_columns])

        if index_map:
            data_columns = [c for c in selected_columns.columns
                            if c not in [idx[0] for idx in index_map]]
            internal = _InternalFrame(
                sdf=selected_columns, data_columns=data_columns, index_map=index_map)
            return DataFrame(internal)
        else:
            return DataFrame(selected_columns)