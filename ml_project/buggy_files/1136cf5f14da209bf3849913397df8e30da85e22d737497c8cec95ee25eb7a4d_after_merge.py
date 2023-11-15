        def describe_builder(df, **kwargs):
            try:
                return pandas.DataFrame.describe(df, **kwargs)
            except ValueError:
                return pandas.DataFrame(index=df.index)