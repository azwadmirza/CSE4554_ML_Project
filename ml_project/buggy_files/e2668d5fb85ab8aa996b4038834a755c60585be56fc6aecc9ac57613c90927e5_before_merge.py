def build_empty_df(dtypes, index=None):
    columns = dtypes.index
    # duplicate column may exist,
    # so use RangeIndex first
    df = pd.DataFrame(columns=pd.RangeIndex(len(columns)), index=index)
    for i, d in enumerate(dtypes):
        df[i] = pd.Series(dtype=d, index=index)
    df.columns = columns
    return df