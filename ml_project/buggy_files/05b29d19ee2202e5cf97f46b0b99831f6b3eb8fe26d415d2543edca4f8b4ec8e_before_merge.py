def _generate_value(dtype, fill_value):
    # special handle for datetime64 and timedelta64
    dispatch = {
        np.datetime64: pd.Timestamp,
        np.timedelta64: pd.Timedelta,
    }
    # otherwise, just use dtype.type itself to convert
    convert = dispatch.get(dtype.type, dtype.type)
    return convert(fill_value)