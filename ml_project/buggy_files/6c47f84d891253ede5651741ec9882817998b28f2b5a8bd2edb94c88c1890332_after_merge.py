    def sort_values(  # type: ignore[override]
        self,
        by,
        axis: Axis = 0,
        ascending=True,
        inplace: bool = False,
        kind: str = "quicksort",
        na_position: str = "last",
        ignore_index: bool = False,
        key: ValueKeyFunc = None,
    ):
        inplace = validate_bool_kwarg(inplace, "inplace")
        axis = self._get_axis_number(axis)

        if not isinstance(by, list):
            by = [by]
        if is_sequence(ascending) and len(by) != len(ascending):
            raise ValueError(
                f"Length of ascending ({len(ascending)}) != length of by ({len(by)})"
            )
        if len(by) > 1:

            keys = [self._get_label_or_level_values(x, axis=axis) for x in by]

            # need to rewrap columns in Series to apply key function
            if key is not None:
                keys = [Series(k, name=name) for (k, name) in zip(keys, by)]

            indexer = lexsort_indexer(
                keys, orders=ascending, na_position=na_position, key=key
            )
            indexer = ensure_platform_int(indexer)
        else:

            by = by[0]
            k = self._get_label_or_level_values(by, axis=axis)

            # need to rewrap column in Series to apply key function
            if key is not None:
                k = Series(k, name=by)

            if isinstance(ascending, (tuple, list)):
                ascending = ascending[0]

            indexer = nargsort(
                k, kind=kind, ascending=ascending, na_position=na_position, key=key
            )

        new_data = self._mgr.take(
            indexer, axis=self._get_block_manager_axis(axis), verify=False
        )

        if ignore_index:
            new_data.set_axis(
                self._get_block_manager_axis(axis), ibase.default_index(len(indexer))
            )

        result = self._constructor(new_data)
        if inplace:
            return self._update_inplace(result)
        else:
            return result.__finalize__(self, method="sort_values")