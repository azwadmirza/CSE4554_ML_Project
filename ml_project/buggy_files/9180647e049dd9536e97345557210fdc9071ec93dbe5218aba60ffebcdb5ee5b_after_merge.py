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
            include = kwargs.get("include", None)
            # This is done to check against the default dtypes with 'in'.
            # We don't change `include` in kwargs, so we can just use this for the
            # check.
            if include is None:
                include = []
            default_excludes = [np.timedelta64, np.datetime64, np.object, np.bool]
            add_to_excludes = [e for e in default_excludes if e not in include]
            if is_list_like(exclude):
                exclude.append(add_to_excludes)
            else:
                exclude = add_to_excludes
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
            try:
                return pandas.DataFrame.describe(df, **kwargs)
            except ValueError:
                return pandas.DataFrame(index=df.index)

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