def build_empty_df(dtypes, index=None):
    columns = dtypes.index
    # duplicate column may exist,
    # so use RangeIndex first
    df = pd.DataFrame(columns=pd.RangeIndex(len(columns)), index=index)
    length = len(index) if index is not None else 0
    for i, d in enumerate(dtypes):
        df[i] = pd.Series([_generate_value(d, 1) for _ in range(length)],
                          dtype=d, index=index)
    df.columns = columns
    return df