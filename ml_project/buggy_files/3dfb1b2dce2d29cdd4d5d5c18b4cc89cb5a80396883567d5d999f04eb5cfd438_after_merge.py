        def _reduce(df):
            other_len = len(df.index.names)
            df = df.reset_index(drop=False)
            # See note above about setting `as_index`
            groupby_args["as_index"] = as_index
            if other_len > 1:
                by_part = list(df.columns[0:other_len])
            else:
                by_part = df.columns[0]
            result = reduce_func(
                df.groupby(by=by_part, axis=axis, **groupby_args), **reduce_args
            )
            if (
                not isinstance(result.index, pandas.MultiIndex)
                and result.index.name is not None
                and "_modin_groupby_" in result.index.name
            ):
                result.index.name = result.index.name[len("_modin_groupby_") :]
            # Avoid inserting data after the first partition or if the data did not come
            # from this query compiler.
            if not as_index and (first_column not in df.columns or drop_by):
                return result.drop(columns=by_part)
            return result