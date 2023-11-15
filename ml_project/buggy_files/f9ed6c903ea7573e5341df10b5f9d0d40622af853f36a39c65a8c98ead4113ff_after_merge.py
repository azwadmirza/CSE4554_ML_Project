def set_index(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
    op = DataFrameSetIndex(keys=keys, drop=drop, append=append,
                           verify_integrity=verify_integrity, output_types=[OutputType.dataframe])
    result = op(df)
    if not inplace:
        return result
    else:
        df.data = result.data