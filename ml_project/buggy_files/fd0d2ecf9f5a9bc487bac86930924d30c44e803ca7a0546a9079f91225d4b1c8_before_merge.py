    def transform(self, func, *args, **kwargs):
        """
        Call function producing a like-indexed DataFrame on each group and
        return a DataFrame having the same indexes as the original object
        filled with the transformed values

        Parameters
        ----------
        f : function
            Function to apply to each subframe

        Notes
        -----
        Each subframe is endowed the attribute 'name' in case you need to know
        which group you are working on.

        Examples
        --------
        >>> grouped = df.groupby(lambda x: mapping[x])
        >>> grouped.transform(lambda x: (x - x.mean()) / x.std())
        """

        # optimized transforms
        func = self._is_cython_func(func) or func
        if isinstance(func, compat.string_types):
            if func in _cython_transforms:
                # cythonized transform
                return getattr(self, func)(*args, **kwargs)
            else:
                # cythonized aggregation and merge
                result = getattr(self, func)(*args, **kwargs)
        else:
            return self._transform_general(func, *args, **kwargs)

        # a reduction transform
        if not isinstance(result, DataFrame):
            return self._transform_general(func, *args, **kwargs)

        obj = self._obj_with_exclusions
        # nuiscance columns
        if not result.columns.equals(obj.columns):
            return self._transform_general(func, *args, **kwargs)

        results = np.empty_like(obj.values, result.values.dtype)
        for (name, group), (i, row) in zip(self, result.iterrows()):
            indexer = self._get_index(name)
            if len(indexer) > 0:
                results[indexer] = np.tile(row.values, len(
                    indexer)).reshape(len(indexer), -1)

        counts = self.size().fillna(0).values
        if any(counts == 0):
            results = self._try_cast(results, obj[result.columns])

        return (DataFrame(results, columns=result.columns, index=obj.index)
                ._convert(datetime=True))