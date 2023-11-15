        def _map(df, other):
            # Set `as_index` to True to track the metadata of the grouping object
            # It is used to make sure that between phases we are constructing the
            # right index and placing columns in the correct order.
            groupby_args["as_index"] = True
            other = other.squeeze(axis=axis ^ 1)
            if isinstance(other, pandas.DataFrame):
                df = pandas.concat(
                    [df] + [other[[o for o in other if o not in df]]], axis=1
                )
                other = list(other.columns)
            result = map_func(
                df.groupby(by=other, axis=axis, **groupby_args), **map_args
            )
            if (
                not isinstance(result.index, pandas.MultiIndex)
                and result.index.name is not None
                and result.index.name in result.columns
            ):
                result.index.name = "{}{}".format("_modin_groupby_", result.index.name)
            return result.reset_index(drop=False)