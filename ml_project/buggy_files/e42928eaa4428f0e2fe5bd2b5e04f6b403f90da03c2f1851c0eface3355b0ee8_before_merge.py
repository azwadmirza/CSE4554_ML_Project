    def __getitem__(self, key):
        kwargs = self._kwargs.copy()
        if self._drop:
            if not isinstance(key, list):
                key = [key]
                kwargs["squeeze"] = True
        # When `as_index` is False, pandas will always convert to a `DataFrame`, we
        # convert to a list here so that the result will be a `DataFrame`.
        elif not self._as_index and not isinstance(key, list):
            key = [key]
        if isinstance(key, list):
            return DataFrameGroupBy(
                self._df[key],
                self._by,
                self._axis,
                idx_name=self._idx_name,
                drop=self._drop,
                **kwargs
            )
        return SeriesGroupBy(
            self._df[key],
            self._by,
            self._axis,
            idx_name=self._idx_name,
            drop=False,
            **kwargs
        )