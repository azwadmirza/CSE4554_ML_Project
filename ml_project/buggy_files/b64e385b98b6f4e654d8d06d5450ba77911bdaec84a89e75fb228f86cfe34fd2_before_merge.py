    def __getitem__(self, key):
        kwargs = self._kwargs.copy()
        # Most of time indexing DataFrameGroupBy results in another DataFrameGroupBy object unless circumstances are
        # special in which case SeriesGroupBy has to be returned. Such circumstances are when key equals to a single
        # column name and is not a list of column names or list of one column name.
        make_dataframe = True
        if self._drop and self._as_index:
            if not isinstance(key, list):
                key = [key]
                kwargs["squeeze"] = True
                make_dataframe = False
        # When `as_index` is False, pandas will always convert to a `DataFrame`, we
        # convert to a list here so that the result will be a `DataFrame`.
        elif not self._as_index and not isinstance(key, list):
            # Sometimes `__getitem__` doesn't only get the item, it also gets the `by`
            # column. This logic is here to ensure that we also get the `by` data so
            # that it is there for `as_index=False`.
            if (
                isinstance(self._by, type(self._query_compiler))
                and all(c in self._columns for c in self._by.columns)
                and self._drop
            ):
                key = [key] + list(self._by.columns)
            else:
                key = [key]
        if isinstance(key, list) and (make_dataframe or not self._as_index):
            return DataFrameGroupBy(
                self._df[key],
                self._by,
                self._axis,
                idx_name=self._idx_name,
                drop=self._drop,
                **kwargs,
            )
        return SeriesGroupBy(
            self._df[key],
            self._by,
            self._axis,
            idx_name=self._idx_name,
            drop=False,
            **kwargs,
        )