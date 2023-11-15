def dataframe_groupby(df, by, as_index=True):
    if isinstance(by, six.string_types):
        by = [by]
    op = DataFrameGroupByOperand(by=by, as_index=as_index)
    return op(df)