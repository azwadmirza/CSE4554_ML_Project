    def mean(self, axis, **kwargs):
        if kwargs.get("level") is not None:
            return self.default_to_pandas(pandas.DataFrame.mean, axis=axis, **kwargs)

        skipna = kwargs.get("skipna", True)

        # TODO-FIX: this function may work incorrectly with user-defined "numeric" values.
        # Since `count(numeric_only=True)` discards all unknown "numeric" types, we can get incorrect
        # divisor inside the reduce function.
        def map_fn(df, **kwargs):
            result = pandas.DataFrame(
                {
                    "sum": df.sum(axis=axis, skipna=skipna),
                    "count": df.count(axis=axis, numeric_only=True),
                }
            )
            return result if axis else result.T

        def reduce_fn(df, **kwargs):
            sum_cols = df["sum"] if axis else df.loc["sum"]
            count_cols = df["count"] if axis else df.loc["count"]

            if not isinstance(sum_cols, pandas.Series):
                # If we got `NaN` as the result of the sum in any axis partition,
                # then we must consider the whole sum as `NaN`, so setting `skipna=False`
                sum_cols = sum_cols.sum(axis=axis, skipna=False)
                count_cols = count_cols.sum(axis=axis, skipna=False)
            return sum_cols / count_cols

        return MapReduceFunction.register(
            map_fn,
            reduce_fn,
            preserve_index=(kwargs.get("numeric_only") is not None),
        )(self, axis=axis, **kwargs)