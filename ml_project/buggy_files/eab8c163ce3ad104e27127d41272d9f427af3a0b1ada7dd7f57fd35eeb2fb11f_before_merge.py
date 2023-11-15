def rtruediv(df, other, axis='columns', level=None, fill_value=None):
    other = wrap_sequence(other)
    op = DataFrameTrueDiv(axis=axis, level=level, fill_value=fill_value, lhs=other, rhs=df)
    return op.rcall(df, other)