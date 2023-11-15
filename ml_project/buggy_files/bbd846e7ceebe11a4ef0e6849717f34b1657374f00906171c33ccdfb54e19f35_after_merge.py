            def helper(df, internal_indices=[]):
                if len(internal_indices) > 0:
                    return pandas_func(df, internal_indices=internal_indices, **kwargs)
                return pandas_func(df, **kwargs)