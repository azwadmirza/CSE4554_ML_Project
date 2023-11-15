def build_empty_df(dtypes, index=None):
    columns = dtypes.index
    df = pd.DataFrame(columns=columns, index=index)
    for c, d in zip(columns, dtypes):
        df[c] = pd.Series(dtype=d, index=index)
    return df