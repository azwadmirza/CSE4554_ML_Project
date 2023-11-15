    def _filter_to_indicator(self, filter):
        """Return selection of rows that match the condition.

        Parameters
        ----------
        filter: ValueFilter describing the condition

        Returns
        -------
        A 1d bool array. len(result) == len(self)
        """
        from Orange.data.filter import (
            FilterContinuous, FilterDiscrete, FilterRegex, FilterString,
            FilterStringList, IsDefined, Values
        )
        if isinstance(filter, Values):
            return self._values_filter_to_indicator(filter)

        def get_col_indices():
            cols = chain(self.domain.variables, self.domain.metas)
            if isinstance(filter, IsDefined):
                return list(cols)

            if filter.column is not None:
                return [filter.column]

            if isinstance(filter, FilterDiscrete):
                raise ValueError("Discrete filter can't be applied across rows")
            if isinstance(filter, FilterContinuous):
                return [col for col in cols if col.is_continuous]
            if isinstance(filter,
                          (FilterString, FilterStringList, FilterRegex)):
                return [col for col in cols if col.is_string]
            raise TypeError("Invalid filter")

        def col_filter(col_idx):
            col = self.get_column_view(col_idx)[0]
            if isinstance(filter, IsDefined):
                if self.domain[col_idx].is_primitive():
                    return ~np.isnan(col.astype(float))
                else:
                    return col.astype(np.bool)
            if isinstance(filter, FilterDiscrete):
                return self._discrete_filter_to_indicator(filter, col)
            if isinstance(filter, FilterContinuous):
                return self._continuous_filter_to_indicator(filter, col)
            if isinstance(filter, FilterString):
                return self._string_filter_to_indicator(filter, col)
            if isinstance(filter, FilterStringList):
                if not filter.case_sensitive:
                    col = np.char.lower(np.array(col, dtype=str))
                    vals = [val.lower() for val in filter.values]
                else:
                    vals = filter.values
                return reduce(operator.add, (col == val for val in vals))
            if isinstance(filter, FilterRegex):
                return np.vectorize(filter)(col)
            raise TypeError("Invalid filter")

        col_indices = get_col_indices()
        if len(col_indices) == 1:
            return col_filter(col_indices[0])

        sel = np.ones(len(self), dtype=bool)
        for col_idx in col_indices:
            sel *= col_filter(col_idx)
        return sel