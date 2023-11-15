    def describe(self, **kwargs):
        """Generates descriptive statistics.

        Returns:
            DataFrame object containing the descriptive statistics of the DataFrame.
        """
        # Only describe numeric if there are numeric columns
        # Otherwise, describe all
        new_columns = self.numeric_columns(include_bool=False)
        if len(new_columns) != 0:
            numeric = True
            exclude = kwargs.get("exclude", None)
            if is_list_like(exclude):
                exclude.append([np.timedelta64, np.datetime64, np.object, np.bool])
            else:
                exclude = [exclude, np.timedelta64, np.datetime64, np.object, np.bool]
            kwargs["exclude"] = exclude
        else:
            numeric = False
            # If only timedelta and datetime objects, only do the timedelta
            # columns
            if all(
                (
                    dtype
                    for dtype in self.dtypes
                    if dtype == np.datetime64 or dtype == np.timedelta64
                )
            ):
                new_columns = [
                    self.columns[i]
                    for i in range(len(self.columns))
                    if self.dtypes[i] != np.dtype("datetime64[ns]")
                ]
            else:
                # Describe all columns
                new_columns = self.columns

        def describe_builder(df, **kwargs):
            return pandas.DataFrame.describe(df, **kwargs)

        # Apply describe and update indices, columns, and dtypes
        func = self._prepare_method(describe_builder, **kwargs)
        new_data = self.full_axis_reduce_along_select_indices(
            func, 0, new_columns, False
        )
        new_index = self.compute_index(0, new_data, False)
        if numeric:
            new_dtypes = pandas.Series(
                [np.float64 for _ in new_columns], index=new_columns
            )
        else:
            new_dtypes = pandas.Series(
                [np.object for _ in new_columns], index=new_columns
            )
        return self.__constructor__(new_data, new_index, new_columns, new_dtypes)