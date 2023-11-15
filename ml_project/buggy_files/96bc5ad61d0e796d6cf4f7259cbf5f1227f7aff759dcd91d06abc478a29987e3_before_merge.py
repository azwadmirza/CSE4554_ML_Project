        def map_func(df, n=n, keep=keep, columns=columns):
            if columns is None:
                return pandas.DataFrame(
                    pandas.Series.nsmallest(df.squeeze(axis=1), n=n, keep=keep)
                )
            return pandas.DataFrame.nsmallest(df, n=n, columns=columns, keep=keep)