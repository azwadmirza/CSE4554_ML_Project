    def pivot_table(self, values=None, index=None, columns=None,
                    aggfunc='mean', fill_value=None):
        """
        Create a spreadsheet-style pivot table as a DataFrame. The levels in
        the pivot table will be stored in MultiIndex objects (hierarchical
        indexes) on the index and columns of the result DataFrame.

        Parameters
        ----------
        values : column to aggregate.
            They should be either a list of one column or a string. A list of columns
            is not supported yet.
        index : column (string) or list of columns
            If an array is passed, it must be the same length as the data.
            The list should contain string.
        columns : column
            Columns used in the pivot operation. Only one column is supported and
            it should be a string.
        aggfunc : function (string), dict, default mean
            If dict is passed, the resulting pivot table will have
            columns concatenated by "_" where the first part is the value
            of columns and the second part is the column name in values
            If dict is passed, the key is column to aggregate and value
            is function or list of functions.
        fill_value : scalar, default None
            Value to replace missing values with.

        Returns
        -------
        table : DataFrame

        Examples
        --------
        >>> df = ks.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
        ...                          "bar", "bar", "bar", "bar"],
        ...                    "B": ["one", "one", "one", "two", "two",
        ...                          "one", "one", "two", "two"],
        ...                    "C": ["small", "large", "large", "small",
        ...                          "small", "large", "small", "small",
        ...                          "large"],
        ...                    "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
        ...                    "E": [2, 4, 5, 5, 6, 6, 8, 9, 9]},
        ...                   columns=['A', 'B', 'C', 'D', 'E'])
        >>> df
             A    B      C  D  E
        0  foo  one  small  1  2
        1  foo  one  large  2  4
        2  foo  one  large  2  5
        3  foo  two  small  3  5
        4  foo  two  small  3  6
        5  bar  one  large  4  6
        6  bar  one  small  5  8
        7  bar  two  small  6  9
        8  bar  two  large  7  9

        This first example aggregates values by taking the sum.

        >>> table = df.pivot_table(values='D', index=['A', 'B'],
        ...                        columns='C', aggfunc='sum')
        >>> table  # doctest: +NORMALIZE_WHITESPACE
                 large  small
        A   B
        foo one    4.0      1
            two    NaN      6
        bar two    7.0      6
            one    4.0      5

        We can also fill missing values using the `fill_value` parameter.

        >>> table = df.pivot_table(values='D', index=['A', 'B'],
        ...                        columns='C', aggfunc='sum', fill_value=0)
        >>> table  # doctest: +NORMALIZE_WHITESPACE
                 large  small
        A   B
        foo one      4      1
            two      0      6
        bar two      7      6
            one      4      5

        We can also calculate multiple types of aggregations for any given
        value column.

        >>> table = df.pivot_table(values = ['D'], index =['C'],
        ...                        columns="A", aggfunc={'D':'mean'})
        >>> table  # doctest: +NORMALIZE_WHITESPACE
               bar       foo
        C
        small  5.5  2.333333
        large  5.5  2.000000
        """
        if not isinstance(columns, str):
            raise ValueError("columns should be string.")

        if not isinstance(values, str) and not isinstance(values, list):
            raise ValueError('values should be string or list of one column.')

        if not isinstance(aggfunc, str) and (not isinstance(aggfunc, dict) or not all(
                isinstance(key, str) and isinstance(value, str) for key, value in aggfunc.items())):
            raise ValueError("aggfunc must be a dict mapping from column name (string) "
                             "to aggregate functions (string).")

        if isinstance(aggfunc, dict) and index is None:
            raise NotImplementedError("pivot_table doesn't support aggfunc"
                                      " as dict and without index.")

        if isinstance(values, list) and len(values) > 1:
            raise NotImplementedError('Values as list of columns is not implemented yet.')

        if isinstance(aggfunc, str):
            agg_cols = [F.expr('{1}(`{0}`) as `{0}`'.format(values, aggfunc))]

        elif isinstance(aggfunc, dict):
            agg_cols = [F.expr('{1}(`{0}`) as `{0}`'.format(key, value))
                        for key, value in aggfunc.items()]
            agg_columns = [key for key, value in aggfunc.items()]

            if set(agg_columns) != set(values):
                raise ValueError("Columns in aggfunc must be the same as values.")

        if index is None:
            sdf = self._sdf.groupBy().pivot(pivot_col=columns).agg(*agg_cols)

        elif isinstance(index, list):
            sdf = self._sdf.groupBy(index).pivot(pivot_col=columns).agg(*agg_cols)
        else:
            raise ValueError("index should be a None or a list of columns.")

        if fill_value is not None and isinstance(fill_value, (int, float)):
            sdf = sdf.fillna(fill_value)

        if index is not None:
            return DataFrame(sdf).set_index(index)
        else:
            if isinstance(values, list):
                index_values = values[-1]
            else:
                index_values = values

            return DataFrame(sdf.withColumn(columns, F.lit(index_values))).set_index(columns)