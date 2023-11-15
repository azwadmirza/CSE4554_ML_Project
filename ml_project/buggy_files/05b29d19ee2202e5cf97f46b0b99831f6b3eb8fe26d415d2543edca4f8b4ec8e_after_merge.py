def _generate_value(dtype, fill_value):
    # special handle for datetime64 and timedelta64
    dispatch = {
        np.datetime64: pd.Timestamp,
        np.timedelta64: pd.Timedelta,
        pd.CategoricalDtype.type: lambda x: pd.CategoricalDtype([x]),
        # for object, we do not know the actual dtype,
        # just convert to str for common usage
        np.object_: lambda x: str(fill_value),
    }
    # otherwise, just use dtype.type itself to convert
    convert = dispatch.get(dtype.type, dtype.type)
    return convert(fill_value)