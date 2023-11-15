    def groupby(
        self,
        by=None,
        axis=0,
        level=None,
        as_index=True,
        sort=True,
        group_keys=True,
        squeeze=False,
        observed=False,
        **kwargs
    ):
        """Apply a groupby to this DataFrame. See _groupby() remote task.
        Args:
            by: The value to groupby.
            axis: The axis to groupby.
            level: The level of the groupby.
            as_index: Whether or not to store result as index.
            sort: Whether or not to sort the result by the index.
            group_keys: Whether or not to group the keys.
            squeeze: Whether or not to squeeze.
        Returns:
            A new DataFrame resulting from the groupby.
        """
        axis = self._get_axis_number(axis)
        idx_name = None
        if callable(by):
            by = by(self.index)
        elif isinstance(by, string_types):
            idx_name = by
            by = self.__getitem__(by)._query_compiler
        elif is_list_like(by):
            if isinstance(by, Series):
                idx_name = by.name
                by = by.values
            mismatch = (
                len(by) != len(self) if axis == 0 else len(by) != len(self.columns)
            )
            if mismatch and all(obj in self for obj in by):
                # In the future, we will need to add logic to handle this, but for now
                # we default to pandas in this case.
                pass
            elif mismatch:
                raise KeyError(next(x for x in by if x not in self))

        from .groupby import DataFrameGroupBy

        return DataFrameGroupBy(
            self,
            by,
            axis,
            level,
            as_index,
            sort,
            group_keys,
            squeeze,
            idx_name,
            observed=observed,
            **kwargs
        )