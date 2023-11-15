    def from_product(cls, iterables, sortorder=None, names=None):
        """
        Make a MultiIndex from the cartesian product of multiple iterables

        Parameters
        ----------
        iterables : list / sequence of iterables
            Each iterable has unique labels for each level of the index.
        sortorder : int or None
            Level of sortedness (must be lexicographically sorted by that
            level).
        names : list / sequence of strings or None
            Names for the levels in the index.

        Returns
        -------
        index : MultiIndex

        Examples
        --------
        >>> numbers = [0, 1, 2]
        >>> colors = [u'green', u'purple']
        >>> MultiIndex.from_product([numbers, colors],
                                     names=['number', 'color'])
        MultiIndex(levels=[[0, 1, 2], [u'green', u'purple']],
                   labels=[[0, 0, 1, 1, 2, 2], [0, 1, 0, 1, 0, 1]],
                   names=[u'number', u'color'])

        See Also
        --------
        MultiIndex.from_arrays : Convert list of arrays to MultiIndex
        MultiIndex.from_tuples : Convert list of tuples to MultiIndex
        """
        from pandas.core.categorical import _factorize_from_iterables
        from pandas.tools.util import cartesian_product

        labels, levels = _factorize_from_iterables(iterables)
        labels = cartesian_product(labels)

        return MultiIndex(levels=levels, labels=labels, sortorder=sortorder,
                          names=names)