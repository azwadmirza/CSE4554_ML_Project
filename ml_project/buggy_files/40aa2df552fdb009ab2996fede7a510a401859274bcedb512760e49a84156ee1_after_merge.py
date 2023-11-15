def truediv(df, other, axis='columns', level=None, fill_value=None):
    op = DataFrameTrueDiv(axis=axis, level=level, fill_value=fill_value, lhs=df, rhs=other)
    return op(df, other)