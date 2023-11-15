    def reindex(self, major=None, items=None, minor=None, method=None,
                major_axis=None, minor_axis=None, copy=True):
        """
        Conform panel to new axis or axes

        Parameters
        ----------
        major : Index or sequence, default None
            Can also use 'major_axis' keyword
        items : Index or sequence, default None
        minor : Index or sequence, default None
            Can also use 'minor_axis' keyword
        method : {'backfill', 'bfill', 'pad', 'ffill', None}, default None
            Method to use for filling holes in reindexed Series

            pad / ffill: propagate last valid observation forward to next valid
            backfill / bfill: use NEXT valid observation to fill gap
        copy : boolean, default True
            Return a new object, even if the passed indexes are the same

        Returns
        -------
        Panel (new object)
        """
        result = self

        major = _mut_exclusive(major, major_axis)
        minor = _mut_exclusive(minor, minor_axis)

        if (method is None and not self._is_mixed_type and
            com._count_not_none(items, major, minor) == 3):
            return self._reindex_multi(items, major, minor)

        if major is not None:
            result = result._reindex_axis(major, method, 1, copy)

        if minor is not None:
            result = result._reindex_axis(minor, method, 2, copy)

        if items is not None:
            result = result._reindex_axis(items, method, 0, copy)

        if result is self and copy:
            raise ValueError('Must specify at least one axis')

        return result