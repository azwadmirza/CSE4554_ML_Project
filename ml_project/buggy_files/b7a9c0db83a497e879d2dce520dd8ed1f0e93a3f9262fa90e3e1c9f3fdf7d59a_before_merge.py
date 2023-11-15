def _make_col(c):
    from databricks.koalas.series import Series
    if isinstance(c, Series):
        return c._scol
    elif isinstance(c, str):
        return F.col(c)
    else:
        raise SparkPandasNotImplementedError(
            description="Can only convert a string to a column type.")