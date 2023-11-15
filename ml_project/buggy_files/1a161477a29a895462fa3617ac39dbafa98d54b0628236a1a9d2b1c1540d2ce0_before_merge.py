    def filter(self, func, dropna=True, *args, **kwargs):
        """
        Return a copy of a Series excluding elements from groups that
        do not satisfy the boolean criterion specified by func.

        Parameters
        ----------
        func : function
            To apply to each group. Should return True or False.
        dropna : Drop groups that do not pass the filter. True by default;
            if False, groups that evaluate False are filled with NaNs.

        Example
        -------
        >>> grouped.filter(lambda x: x.mean() > 0)

        Returns
        -------
        filtered : Series
        """
        if isinstance(func, compat.string_types):
            wrapper = lambda x: getattr(x, func)(*args, **kwargs)
        else:
            wrapper = lambda x: func(x, *args, **kwargs)

        indexers = [self.obj.index.get_indexer(group.index) \
                    if wrapper(group) else [] for _ , group in self]

        if len(indexers) == 0:
            filtered = self.obj.take([]) # because np.concatenate would fail
        else:
            filtered = self.obj.take(np.concatenate(indexers))
        if dropna:
            return filtered
        else:
            return filtered.reindex(self.obj.index) # Fill with NaNs.