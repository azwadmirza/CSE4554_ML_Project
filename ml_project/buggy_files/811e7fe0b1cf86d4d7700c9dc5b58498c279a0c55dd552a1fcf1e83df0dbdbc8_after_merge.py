    def sort_index(
        self,
        axis=0,
        level=None,
        ascending=True,
        inplace=False,
        kind="quicksort",
        na_position="last",
        sort_remaining=True,
        by=None,
    ):
        """Sort a DataFrame by one of the indices (columns or index).

        Args:
            axis: The axis to sort over.
            level: The MultiIndex level to sort over.
            ascending: Ascending or descending
            inplace: Whether or not to update this DataFrame inplace.
            kind: How to perform the sort.
            na_position: Where to position NA on the sort.
            sort_remaining: On Multilevel Index sort based on all levels.
            by: (Deprecated) argument to pass to sort_values.

        Returns:
            A sorted DataFrame
        """
        axis = self._get_axis_number(axis)
        if level is not None or (
            (axis == 0 and isinstance(self.index, pandas.MultiIndex))
            or (axis == 1 and isinstance(self.columns, pandas.MultiIndex))
        ):
            new_query_compiler = self._default_to_pandas(
                "sort_index",
                axis=axis,
                level=level,
                ascending=ascending,
                inplace=False,
                kind=kind,
                na_position=na_position,
                sort_remaining=sort_remaining,
            )._query_compiler
            return self._create_or_update_from_compiler(new_query_compiler, inplace)
        if by is not None:
            warnings.warn(
                "by argument to sort_index is deprecated, "
                "please use .sort_values(by=...)",
                FutureWarning,
                stacklevel=2,
            )
            if level is not None:
                raise ValueError("unable to simultaneously sort by and level")
            return self.sort_values(by, axis=axis, ascending=ascending, inplace=inplace)
        new_query_compiler = self._query_compiler.sort_index(
            axis=axis, ascending=ascending, kind=kind, na_position=na_position
        )
        if inplace:
            self._update_inplace(new_query_compiler=new_query_compiler)
        else:
            return self.__constructor__(query_compiler=new_query_compiler)