    def caller(df, *args, **kwargs):
        df = df.copy()
        func(df, *args, **kwargs)
        return df