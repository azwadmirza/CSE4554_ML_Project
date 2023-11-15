def df_apply(df, func, axis=0, raw=False, result_type=None, args=(), dtypes=None,
             output_type=None, index=None, elementwise=None, **kwds):
    if isinstance(func, (list, dict)):
        return df.aggregate(func)

    output_types = kwds.pop('output_types', None)
    object_type = kwds.pop('object_type', None)
    output_types = validate_output_types(
        output_type=output_type, output_types=output_types, object_type=object_type)
    output_type = output_types[0] if output_types else None

    # calling member function
    if isinstance(func, str):
        func = getattr(df, func)
        sig = inspect.getfullargspec(func)
        if "axis" in sig.args:
            kwds["axis"] = axis
        return func(*args, **kwds)

    op = ApplyOperand(func=func, axis=axis, raw=raw, result_type=result_type, args=args, kwds=kwds,
                      output_types=output_type, elementwise=elementwise)
    return op(df, dtypes=dtypes, index=index)