    def melt(self, id_vars=None, value_vars=None, var_name='variable',
             value_name='value'):
        """
        Unpivot a DataFrame from wide format to long format, optionally
        leaving identifier variables set.

        This function is useful to massage a DataFrame into a format where one
        or more columns are identifier variables (`id_vars`), while all other
        columns, considered measured variables (`value_vars`), are "unpivoted" to
        the row axis, leaving just two non-identifier columns, 'variable' and
        'value'.

        Parameters
        ----------
        frame : DataFrame
        id_vars : tuple, list, or ndarray, optional
            Column(s) to use as identifier variables.
        value_vars : tuple, list, or ndarray, optional
            Column(s) to unpivot. If not specified, uses all columns that
            are not set as `id_vars`.
        var_name : scalar, default 'variable'
            Name to use for the 'variable' column.
        value_name : scalar, default 'value'
            Name to use for the 'value' column.

        Returns
        -------
        DataFrame
            Unpivoted DataFrame.

        Examples
        --------
        >>> df = ks.DataFrame({'A': {0: 'a', 1: 'b', 2: 'c'},
        ...                    'B': {0: 1, 1: 3, 2: 5},
        ...                    'C': {0: 2, 1: 4, 2: 6}})
        >>> df
           A  B  C
        0  a  1  2
        1  b  3  4
        2  c  5  6

        >>> ks.melt(df)
          variable value
        0        A     a
        1        B     1
        2        C     2
        3        A     b
        4        B     3
        5        C     4
        6        A     c
        7        B     5
        8        C     6

        >>> df.melt(id_vars='A')
           A variable  value
        0  a        B      1
        1  a        C      2
        2  b        B      3
        3  b        C      4
        4  c        B      5
        5  c        C      6

        >>> ks.melt(df, id_vars=['A', 'B'])
           A  B variable  value
        0  a  1        C      2
        1  b  3        C      4
        2  c  5        C      6

        >>> df.melt(id_vars=['A'], value_vars=['C'])
           A variable  value
        0  a        C      2
        1  b        C      4
        2  c        C      6

        The names of 'variable' and 'value' columns can be customized:

        >>> ks.melt(df, id_vars=['A'], value_vars=['B'],
        ...         var_name='myVarname', value_name='myValname')
           A myVarname  myValname
        0  a         B          1
        1  b         B          3
        2  c         B          5
        """
        if id_vars is None:
            id_vars = []
        if not isinstance(id_vars, (list, tuple, np.ndarray)):
            id_vars = list(id_vars)

        data_columns = self._internal.data_columns

        if value_vars is None:
            value_vars = []
        if not isinstance(value_vars, (list, tuple, np.ndarray)):
            value_vars = list(value_vars)
        if len(value_vars) == 0:
            value_vars = data_columns

        data_columns = [data_column for data_column in data_columns if data_column not in id_vars]
        sdf = self._sdf

        pairs = F.explode(F.array(*[
            F.struct(*(
                [F.lit(column).alias(var_name)] +
                [F.col(column).alias(value_name)])
            ) for column in data_columns if column in value_vars]))

        columns = (id_vars +
                   [F.col("pairs.%s" % var_name), F.col("pairs.%s" % value_name)])
        exploded_df = sdf.withColumn("pairs", pairs).select(columns)

        return DataFrame(exploded_df)