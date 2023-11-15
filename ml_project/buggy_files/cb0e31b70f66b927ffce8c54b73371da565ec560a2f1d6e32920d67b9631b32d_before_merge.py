    def __init__(
        self,
        df,
        by,
        axis,
        level,
        as_index,
        sort,
        group_keys,
        squeeze,
        idx_name,
        drop,
        **kwargs
    ):
        self._axis = axis
        self._idx_name = idx_name
        self._df = df
        self._query_compiler = self._df._query_compiler
        self._index = self._query_compiler.index
        self._columns = self._query_compiler.columns
        self._by = by
        self._drop = drop

        if (
            level is None
            and not isinstance(by, type(self._query_compiler))
            and is_list_like(by)
        ):
            # This tells us whether or not there are multiple columns/rows in the groupby
            self._is_multi_by = all(obj in self._df for obj in self._by) and axis == 0
        else:
            self._is_multi_by = False
        self._level = level
        self._kwargs = {
            "level": level,
            "sort": sort,
            "as_index": as_index,
            "group_keys": group_keys,
            "squeeze": squeeze,
        }
        self._kwargs.update(kwargs)