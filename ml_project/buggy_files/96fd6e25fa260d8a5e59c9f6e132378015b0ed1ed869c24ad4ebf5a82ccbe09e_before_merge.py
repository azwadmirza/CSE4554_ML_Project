    def nunique(self, dropna=True):
        """
        Return DataFrame with number of distinct observations per group for
        each column.

        .. versionadded:: 0.20.0

        Parameters
        ----------
        dropna : boolean, default True
            Don't include NaN in the counts.

        Returns
        -------
        nunique: DataFrame

        Examples
        --------
        >>> df = pd.DataFrame({'id': ['spam', 'egg', 'egg', 'spam',
        ...                           'ham', 'ham'],
        ...                    'value1': [1, 5, 5, 2, 5, 5],
        ...                    'value2': list('abbaxy')})
        >>> df
             id  value1 value2
        0  spam       1      a
        1   egg       5      b
        2   egg       5      b
        3  spam       2      a
        4   ham       5      x
        5   ham       5      y

        >>> df.groupby('id').nunique()
            id  value1  value2
        id
        egg    1       1       1
        ham    1       1       2
        spam   1       2       1

        # check for rows with the same id but conflicting values
        >>> df.groupby('id').filter(lambda g: (g.nunique() > 1).any())
             id  value1 value2
        0  spam       1      a
        3  spam       2      a
        4   ham       5      x
        5   ham       5      y
        """

        obj = self._selected_obj

        def groupby_series(obj, col=None):
            return SeriesGroupBy(obj,
                                 selection=col,
                                 grouper=self.grouper).nunique(dropna=dropna)

        if isinstance(obj, Series):
            results = groupby_series(obj)
        else:
            from pandas.core.reshape.concat import concat
            results = [groupby_series(obj[col], col) for col in obj.columns]
            results = concat(results, axis=1)

        if not self.as_index:
            results.index = ibase.default_index(len(results))
        return results