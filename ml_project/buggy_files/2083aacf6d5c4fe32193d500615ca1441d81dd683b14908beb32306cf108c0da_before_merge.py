def df_apply(df, func, axis=0, raw=False, result_type=None, args=(), dtypes=None,
             output_type=None, index=None, elementwise=None, **kwds):
    if isinstance(func, (list, dict)):
        return df.aggregate(func)

    if isinstance(output_type, str):
        output_type = getattr(OutputType, output_type.lower())

    # calling member function
    if isinstance(func, str):
        func = getattr(df, func)
        sig = inspect.getfullargspec(func)
        if "axis" in sig.args:
            kwds["axis"] = axis
        return func(*args, **kwds)

    op = ApplyOperand(func=func, axis=axis, raw=raw, result_type=result_type, args=args, kwds=kwds,
                      output_type=output_type, elementwise=elementwise)
    return op(df, dtypes=dtypes, index=index)