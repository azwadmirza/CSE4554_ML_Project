        def describe_builder(df, internal_indices=[], **kwargs):
            return df.iloc[:, internal_indices].describe(**kwargs)