def set_index(df, keys, drop=True, append=False, verify_integrity=False, **kw):
    op = DataFrameSetIndex(keys=keys, drop=drop, append=append,
                           verify_integrity=verify_integrity, output_types=[OutputType.dataframe], **kw)
    return op(df)