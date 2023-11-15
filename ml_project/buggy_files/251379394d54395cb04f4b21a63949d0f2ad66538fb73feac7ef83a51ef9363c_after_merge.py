    def _scalar_operations(self, axis, scalar, func):
        """Handler for mapping scalar operations across a Manager.

        Args:
            axis: The axis index object to execute the function on.
            scalar: The scalar value to map.
            func: The function to use on the Manager with the scalar.

        Returns:
            A new QueryCompiler with updated data and new index.
        """
        if isinstance(scalar, (list, np.ndarray, pandas.Series)):
            new_index = self.index if axis == 0 else self.columns

            def list_like_op(df):
                if axis == 0:
                    df.index = new_index
                else:
                    df.columns = new_index
                return func(df)

            new_data = self._map_across_full_axis(
                axis, self._prepare_method(list_like_op)
            )
            if axis == 1 and isinstance(scalar, pandas.Series):
                new_columns = self.columns.union(
                    [label for label in scalar.index if label not in self.columns]
                )
            else:
                new_columns = self.columns
            return self.__constructor__(new_data, self.index, new_columns)
        else:
            return self._map_partitions(self._prepare_method(func))