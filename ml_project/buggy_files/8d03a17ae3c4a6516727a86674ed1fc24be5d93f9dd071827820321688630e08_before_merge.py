    def filter(self, func, dropna=True, *args, **kwargs):
        """
        Return a copy of a DataFrame excluding elements from groups that
        do not satisfy the boolean criterion specified by func.

        Parameters
        ----------
        f : function
            Function to apply to each subframe. Should return True or False.
        dropna : Drop groups that do not pass the filter. True by default;
            if False, groups that evaluate False are filled with NaNs.

        Note
        ----
        Each subframe is endowed the attribute 'name' in case you need to know
        which group you are working on.

        Example
        --------
        >>> grouped = df.groupby(lambda x: mapping[x])
        >>> grouped.filter(lambda x: x['A'].sum() + x['B'].sum() > 0)
        """
        from pandas.tools.merge import concat

        indexers = []

        obj = self._obj_with_exclusions
        gen = self.grouper.get_iterator(obj, axis=self.axis)

        fast_path, slow_path = self._define_paths(func, *args, **kwargs)

        path = None
        for name, group in gen:
            object.__setattr__(group, 'name', name)

            if path is None:
                # Try slow path and fast path.
                try:
                    path, res = self._choose_path(fast_path, slow_path, group)
                except Exception:  # pragma: no cover
                    res  = fast_path(group)
                    path = fast_path
            else:
                res = path(group)

            def add_indexer():
                indexers.append(self.obj.index.get_indexer(group.index))

            # interpret the result of the filter
            if isinstance(res,(bool,np.bool_)):
                if res:
                    add_indexer()
            else:
                if getattr(res,'ndim',None) == 1:
                    if res.ravel()[0]:
                        add_indexer()
                else:

                    # in theory you could do .all() on the boolean result ?
                    raise TypeError("the filter must return a boolean result")

        if len(indexers) == 0:
            filtered = self.obj.take([]) # because np.concatenate would fail
        else:
            filtered = self.obj.take(np.concatenate(indexers))
        if dropna:
            return filtered
        else:
            return filtered.reindex(self.obj.index) # Fill with NaNs.