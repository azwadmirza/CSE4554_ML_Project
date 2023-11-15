def length_fn_pandas(df):
    assert isinstance(df, pandas.DataFrame)
    return len(df) if len(df) > 0 else 0