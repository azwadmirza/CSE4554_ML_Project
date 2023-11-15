        def _reduce(df):
            def compute_reduce(df):
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
                if isinstance(by_part, str) and by_part in result.columns:
                    if "_modin_groupby_" in by_part and drop:
                        col_name = by_part[len("_modin_groupby_") :]
                        new_result = result.drop(columns=col_name)
                        new_result.columns = [
                            col_name if "_modin_groupby_" in c else c
                            for c in new_result.columns
                        ]
                        return new_result
                    else:
                        return result.drop(columns=by_part)
                return result

            try:
                return compute_reduce(df)
            # This will happen with Arrow buffer read-only errors. We don't want to copy
            # all the time, so this will try to fast-path the code first.
            except (ValueError):
                return compute_reduce(df.copy())