    def filter(self, items=None, like=None, regex=None, axis=None):
        """
        Subset rows or columns of dataframe according to labels in
        the specified index.

        Note that this routine does not filter a dataframe on its
        contents. The filter is applied to the labels of the index.

        Parameters
        ----------
        items : list-like
            List of info axis to restrict to (must not all be present)
        like : string
            Keep info axis where "arg in col == True"
        regex : string (regular expression)
            Keep info axis with re.search(regex, col) == True
        axis : int or string axis name
            The axis to filter on.  By default this is the info axis,
            'index' for Series, 'columns' for DataFrame

        Returns
        -------
        same type as input object

        Examples
        --------
        >>> df
        one  two  three
        mouse     1    2      3
        rabbit    4    5      6

        >>> # select columns by name
        >>> df.filter(items=['one', 'three'])
        one  three
        mouse     1      3
        rabbit    4      6

        >>> # select columns by regular expression
        >>> df.filter(regex='e$', axis=1)
        one  three
        mouse     1      3
        rabbit    4      6

        >>> # select rows containing 'bbi'
        >>> df.filter(like='bbi', axis=0)
        one  two  three
        rabbit    4    5      6

        See Also
        --------
        pandas.DataFrame.loc

        Notes
        -----
        The ``items``, ``like``, and ``regex`` parameters are
        enforced to be mutually exclusive.

        ``axis`` defaults to the info axis that is used when indexing
        with ``[]``.
        """
        import re

        nkw = _count_not_none(items, like, regex)
        if nkw > 1:
            raise TypeError('Keyword arguments `items`, `like`, or `regex` '
                            'are mutually exclusive')

        if axis is None:
            axis = self._info_axis_name
        labels = self._get_axis(axis)

        if items is not None:
            name = self._get_axis_name(axis)
            return self.reindex(
                **{name: [r for r in items if r in labels]})
        elif like:
            def f(x):
                if not isinstance(x, string_types):
                    x = str(x)
                return like in x
            values = labels.map(f)
            return self.loc(axis=axis)[values]
        elif regex:
            matcher = re.compile(regex)
            values = labels.map(lambda x: matcher.search(str(x)) is not None)
            return self.loc(axis=axis)[values]
        else:
            raise TypeError('Must pass either `items`, `like`, or `regex`')