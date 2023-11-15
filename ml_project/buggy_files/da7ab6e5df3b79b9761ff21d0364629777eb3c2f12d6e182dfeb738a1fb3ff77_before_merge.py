def _conv_value(val):
    # Convert numpy types to Python types for the Excel writers.
    if com.is_integer(val):
        val = int(val)
    elif com.is_float(val):
        val = float(val)
    elif com.is_bool(val):
        val = bool(val)
    elif isinstance(val, Period):
        val = "%s" % val

    return val