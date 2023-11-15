    def aggregate(self, func_or_funcs, *args, **kwargs):
        """Aggregate using one or more operations over the specified axis.

        Parameters
        ----------
        func : dict
             a dict mapping from column name (string) to aggregate functions (string).

        Returns
        -------
        Series or DataFrame

            The return can be:

            * Series : when DataFrame.agg is called with a single function
            * DataFrame : when DataFrame.agg is called with several functions

            Return Series or DataFrame.

        Notes
        -----
        `agg` is an alias for `aggregate`. Use the alias.

        See Also
        --------
        databricks.koalas.Series.groupby
        databricks.koalas.DataFrame.groupby

        Examples
        --------
        >>> df = ks.DataFrame({'A': [1, 1, 2, 2],
        ...                    'B': [1, 2, 3, 4],
        ...                    'C': [0.362, 0.227, 1.267, -0.562]},
        ...                   columns=['A', 'B', 'C'])

        >>> df
           A  B      C
        0  1  1  0.362
        1  1  2  0.227
        2  2  3  1.267
        3  2  4 -0.562

        Different aggregations per column

        >>> aggregated = df.groupby('A').agg({'B': 'min', 'C': 'sum'})
        >>> aggregated[['B', 'C']]  # doctest: +NORMALIZE_WHITESPACE
           B      C
        A
        1  1  0.589
        2  3  0.705

        """
        if not isinstance(func_or_funcs, dict) or \
                not all(isinstance(key, str) and isinstance(value, str)
                        for key, value in func_or_funcs.items()):
            raise ValueError("aggs must be a dict mapping from column name (string) to aggregate "
                             "functions (string).")

        sdf = self._kdf._sdf
        groupkeys = self._groupkeys
        groupkey_cols = [s._scol.alias('__index_level_{}__'.format(i))
                         for i, s in enumerate(groupkeys)]
        reordered = []
        for key, value in func_or_funcs.items():
            if value == "nunique":
                reordered.append(F.expr('count(DISTINCT `{0}`) as `{0}`'.format(key)))
            else:
                reordered.append(F.expr('{1}(`{0}`) as `{0}`'.format(key, value)))
        sdf = sdf.groupby(*groupkey_cols).agg(*reordered)
        internal = _InternalFrame(sdf=sdf,
                                  data_columns=[key for key, _ in func_or_funcs.items()],
                                  index_map=[('__index_level_{}__'.format(i), s.name)
                                             for i, s in enumerate(groupkeys)])
        return DataFrame(internal)