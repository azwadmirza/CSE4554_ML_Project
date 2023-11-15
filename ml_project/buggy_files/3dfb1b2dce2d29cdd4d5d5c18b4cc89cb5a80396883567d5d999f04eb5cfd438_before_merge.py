            def _reduce(df):
                # See note above about setting `as_index`
                groupby_args["as_index"] = True
                if other_len > 1:
                    by = list(df.columns[0:other_len])
                else:
                    by = df.columns[0]
                result = map_func(
                    df.groupby(by=by, axis=axis, **groupby_args), **map_args
                )
                if (
                    not isinstance(result.index, pandas.MultiIndex)
                    and result.index.name is not None
                    and "_modin_groupby_" in result.index.name
                ):
                    result.index.name = result.index.name[len("_modin_groupby_") :]
                return result