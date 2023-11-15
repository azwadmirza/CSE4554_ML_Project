def between_time(arg, lower, upper, timezone=None):
    """Check if the input expr falls between the lower/upper bounds passed.
    Bounds are inclusive. All arguments must be comparable.

    Parameters
    ----------
    lower : str, datetime.time
    upper : str, datetime.time
    timezone : str, timezone, default None

    Returns
    -------
    BooleanValue
    """

    if isinstance(arg.op(), ops.Time):
        # Here we pull out the first argument to the underlying Time operation
        # which is by definition (in _timestamp_value_methods) a
        # TimestampValue. We do this so that we can potentially specialize the
        # "between time" operation for timestamp_value_expr.time().between().
        # A similar mechanism is triggered when creating expressions like
        # t.column.distinct().count(), which is turned into t.column.nunique().
        arg = arg.op().args[0]
        if timezone is not None:
            arg = arg.cast(dt.Timestamp(timezone=timezone))
        op = ops.BetweenTime(arg, lower, upper)
    else:
        op = ops.Between(arg, lower, upper)

    return op.to_expr()