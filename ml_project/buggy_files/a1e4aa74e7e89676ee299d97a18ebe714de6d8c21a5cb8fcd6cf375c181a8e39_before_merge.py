    def bar(self, subset=None, axis=0, color='#d65f5f', width=100):
        """
        Color the background ``color`` proptional to the values in each column.
        Excludes non-numeric data by default.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        subset: IndexSlice, default None
            a valid slice for ``data`` to limit the style application to
        axis: int
        color: str
        width: float
            A number between 0 or 100. The largest value will cover ``width``
            percent of the cell's width

        Returns
        -------
        self
        """
        subset = _maybe_numeric_slice(self.data, subset)
        subset = _non_reducing_slice(subset)
        self.apply(self._bar, subset=subset, axis=axis, color=color,
                   width=width)
        return self