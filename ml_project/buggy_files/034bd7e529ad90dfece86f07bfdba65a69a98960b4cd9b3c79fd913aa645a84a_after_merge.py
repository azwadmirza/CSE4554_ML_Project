    def get_loc(self, key, method=None, tolerance=None):
        """
        Get integer location for requested label

        Parameters
        ----------
        key : label
        method : {None, 'pad'/'ffill', 'backfill'/'bfill', 'nearest'}, optional
            * default: exact matches only.
            * pad / ffill: find the PREVIOUS index value if no exact match.
            * backfill / bfill: use NEXT index value if no exact match
            * nearest: use the NEAREST index value if no exact match. Tied
              distances are broken by preferring the larger index value.
        tolerance : optional
            Maximum distance from index value for inexact matches. The value of
            the index at the matching location most satisfy the equation
            ``abs(index[loc] - key) <= tolerance``.

            .. versionadded:: 0.17.0

        Returns
        -------
        loc : int if unique index, possibly slice or mask if not
        """
        if method is None:
            if tolerance is not None:
                raise ValueError('tolerance argument only valid if using pad, '
                                 'backfill or nearest lookups')
            key = _values_from_object(key)
            return self._engine.get_loc(key)

        indexer = self.get_indexer([key], method=method,
                                   tolerance=tolerance)
        if indexer.ndim > 1 or indexer.size > 1:
            raise TypeError('get_loc requires scalar valued input')
        loc = indexer.item()
        if loc == -1:
            raise KeyError(key)
        return loc