    def count(self, axis=0, level=None, numeric_only=False):
        """Get the count of non-null objects in the DataFrame.

        Arguments:
            axis: 0 or 'index' for row-wise, 1 or 'columns' for column-wise.
            level: If the axis is a MultiIndex (hierarchical), count along a
                particular level, collapsing into a DataFrame.
            numeric_only: Include only float, int, boolean data

        Returns:
            The count, in a Series (or DataFrame if level is specified).
        """

        axis = self._get_axis_number(axis) if axis is not None else 0

        if level is not None:

            if not isinstance(self.axes[axis], pandas.MultiIndex):
                # error thrown by pandas
                raise TypeError("Can only count levels on hierarchical columns.")

            if isinstance(level, str):
                level = self.axes[axis].names.index(level)
            return self.groupby(level=level, axis=axis).count()

        return self._reduce_dimension(
            self._query_compiler.count(
                axis=axis, level=level, numeric_only=numeric_only
            )
        )