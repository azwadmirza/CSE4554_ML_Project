def dataframe_groupby(df, by, as_index=True, sort=True):
    if isinstance(by, six.string_types):
        by = [by]
    op = DataFrameGroupByOperand(by=by, as_index=as_index, sort=sort)
    return op(df)