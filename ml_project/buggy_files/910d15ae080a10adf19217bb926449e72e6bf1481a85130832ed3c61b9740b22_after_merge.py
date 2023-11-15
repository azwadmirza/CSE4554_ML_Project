    def _sort_levels_monotonic(self):
        """
        .. versionadded:: 0.20.0

        This is an *internal* function.

        create a new MultiIndex from the current to monotonically sorted
        items IN the levels. This does not actually make the entire MultiIndex
        monotonic, JUST the levels.

        The resulting MultiIndex will have the same outward
        appearance, meaning the same .values and ordering. It will also
        be .equals() to the original.

        Returns
        -------
        MultiIndex

        Examples
        --------

        >>> i = pd.MultiIndex(levels=[['a', 'b'], ['bb', 'aa']],
                              labels=[[0, 0, 1, 1], [0, 1, 0, 1]])
        >>> i
        MultiIndex(levels=[['a', 'b'], ['bb', 'aa']],
                   labels=[[0, 0, 1, 1], [0, 1, 0, 1]])

        >>> i.sort_monotonic()
        MultiIndex(levels=[['a', 'b'], ['aa', 'bb']],
                   labels=[[0, 0, 1, 1], [1, 0, 1, 0]])

        """

        if self.is_lexsorted() and self.is_monotonic:
            return self

        new_levels = []
        new_labels = []

        for lev, lab in zip(self.levels, self.labels):

            if not lev.is_monotonic:
                try:
                    # indexer to reorder the levels
                    indexer = lev.argsort()
                except TypeError:
                    pass
                else:
                    lev = lev.take(indexer)

                    # indexer to reorder the labels
                    indexer = _ensure_int64(indexer)
                    ri = lib.get_reverse_indexer(indexer, len(indexer))
                    lab = algos.take_1d(ri, lab)

            new_levels.append(lev)
            new_labels.append(lab)

        return MultiIndex(new_levels, new_labels,
                          names=self.names, sortorder=self.sortorder,
                          verify_integrity=False)