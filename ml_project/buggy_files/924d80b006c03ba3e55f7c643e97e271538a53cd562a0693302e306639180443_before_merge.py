def build_empty_df(dtypes, index=None):
    columns = dtypes.index
    df = pd.DataFrame(columns=columns)
    for c, d in zip(columns, dtypes):
        df[c] = pd.Series(dtype=d, index=index)
    return df