def build_df(df_obj, fill_value=1, size=1):
    empty_df = build_empty_df(df_obj.dtypes, index=df_obj.index_value.to_pandas()[:0])
    dtypes = empty_df.dtypes
    record = [_generate_value(dtype, fill_value) for dtype in empty_df.dtypes]
    if isinstance(empty_df.index, pd.MultiIndex):
        index = tuple(_generate_value(level.dtype, fill_value) for level in empty_df.index.levels)
        empty_df.loc[index, ] = record
    else:
        index = _generate_value(empty_df.index.dtype, fill_value)
        empty_df.loc[index] = record

    empty_df = pd.concat([empty_df] * size)
    # make sure dtypes correct for MultiIndex
    empty_df = empty_df.astype(dtypes, copy=False)
    return empty_df