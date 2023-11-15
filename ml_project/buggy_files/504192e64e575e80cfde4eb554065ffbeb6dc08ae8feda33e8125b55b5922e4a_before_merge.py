        def map_func(df, *args, **kwargs):
            return df.squeeze(axis=1).value_counts(**kwargs)