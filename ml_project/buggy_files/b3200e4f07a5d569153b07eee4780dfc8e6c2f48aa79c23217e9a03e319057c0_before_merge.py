    def describe(self, **kwargs):
        """Generates descriptive statistics.

        Returns:
            DataFrame object containing the descriptive statistics of the DataFrame.
        """
        # Only describe numeric if there are numeric columns
        # Otherwise, describe all
        new_columns = self.numeric_columns(include_bool=False)
        include = kwargs.get("include", None)
        if len(new_columns) != 0 and include is not None:
            if not isinstance(include, np.dtype) and include == "all":
                new_columns = self.columns
            else:
                new_columns = self.dtypes[
                    [
                        any(
                            (isinstance(inc, np.dtype) and inc == d)
                            or (
                                not isinstance(inc, np.dtype)
                                and inc.__subclasscheck__(getattr(np, d.__str__()))
                            )
                            for inc in include
                        )
                        for d in self.dtypes.values
                    ]
                ].index
        elif len(new_columns) == 0:
            new_columns = [
                self.columns[i]
                for i in range(len(self.columns))
                if self.dtypes[i] != np.dtype("datetime64[ns]")
            ]
        else:
            exclude = kwargs.get("exclude", None)
            # This is done to check against the default dtypes with 'in'.
            # We don't change `include` in kwargs, so we can just use this for the
            # check.
            include = []
            default_excludes = [np.timedelta64, np.datetime64, np.object, np.bool]
            add_to_excludes = [e for e in default_excludes if e not in include]
            if isinstance(exclude, list):
                exclude.extend(add_to_excludes)
            else:
                exclude = add_to_excludes
            kwargs["exclude"] = exclude
            # Update `new_columns` to reflect the included types
            new_columns = self.dtypes[~self.dtypes.isin(exclude)].index

        def describe_builder(df, internal_indices=[], **kwargs):
            return df.iloc[:, internal_indices].describe(**kwargs)

        # Apply describe and update indices, columns, and dtypes
        func = self._prepare_method(describe_builder, **kwargs)
        new_data = self._full_axis_reduce_along_select_indices(
            func, 0, new_columns, False
        )
        new_index = self.compute_index(0, new_data, False)
        return self.__constructor__(new_data, new_index, new_columns)