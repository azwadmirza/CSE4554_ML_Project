    def describe(self, **kwargs):
        """Generates descriptive statistics.

        Returns:
            DataFrame object containing the descriptive statistics of the DataFrame.
        """
        # Use pandas to calculate the correct columns
        empty_df = (
            pandas.DataFrame(columns=self.columns)
            .astype(self.dtypes)
            .describe(**kwargs)
        )
        new_index = empty_df.index

        # Note: `describe` convert timestamp type to object type
        # which results in the loss of two values in index: `first` and `last`
        # for empty DataFrame.
        datetime_is_numeric = kwargs.get("datetime_is_numeric") or False
        if not any(map(is_numeric_dtype, empty_df.dtypes)) and not datetime_is_numeric:
            for col_name in empty_df.dtypes.index:
                # if previosly type of `col_name` was datetime or timedelta
                if is_datetime_or_timedelta_dtype(self.dtypes[col_name]):
                    new_index = pandas.Index(
                        empty_df.index.to_list() + ["first"] + ["last"]
                    )
                    break

        def describe_builder(df, internal_indices=[]):
            return df.iloc[:, internal_indices].describe(**kwargs)

        return self.__constructor__(
            self._modin_frame._apply_full_axis_select_indices(
                0,
                describe_builder,
                empty_df.columns,
                new_index=new_index,
                new_columns=empty_df.columns,
            )
        )