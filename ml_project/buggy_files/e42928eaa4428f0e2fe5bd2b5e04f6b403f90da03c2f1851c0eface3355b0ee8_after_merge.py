    def __getitem__(self, key):
        kwargs = self._kwargs.copy()
        # Most of time indexing DataFrameGroupBy results in another DataFrameGroupBy object unless circumstances are
        # special in which case SeriesGroupBy has to be returned. Such circumstances are when key equals to a single
        # column name and is not a list of column names or list of one column name.
        make_dataframe = True
        if self._drop:
            if not isinstance(key, list):
                key = [key]
                kwargs["squeeze"] = True
                make_dataframe = False
        # When `as_index` is False, pandas will always convert to a `DataFrame`, we
        # convert to a list here so that the result will be a `DataFrame`.
        elif not self._as_index and not isinstance(key, list):
            key = [key]
        if isinstance(key, list) and (make_dataframe or not self._as_index):
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