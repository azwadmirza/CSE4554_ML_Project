        def reduce_fn(df, **kwargs):
            df.dropna(axis=1, inplace=True, how="any")
            return build_applyier(reduce_apply_fn, axis=axis)(df)