        def map_func(df, n=n, keep=keep, columns=columns):
            if columns is None:
                return pandas.DataFrame(
                    getattr(pandas.Series, sort_type)(
                        df.squeeze(axis=1), n=n, keep=keep
                    )
                )
            return getattr(pandas.DataFrame, sort_type)(
                df, n=n, columns=columns, keep=keep
            )