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
            FilterStringList, Values
        )
        if isinstance(filter, Values):
            return self._values_filter_to_indicator(filter)

        col = self.get_column_view(filter.column)[0]

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