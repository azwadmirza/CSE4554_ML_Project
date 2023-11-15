def _get_data_algo(values, func_map):
    if com.is_float_dtype(values):
        f = func_map['float64']
        values = com._ensure_float64(values)
    elif com.is_datetime64_dtype(values):
        f = func_map['int64']
        values = values.view('i8')
    elif com.is_integer_dtype(values):
        f = func_map['int64']
        values = com._ensure_int64(values)
    else:
        f = func_map['generic']
        values = com._ensure_object(values)
    return f, values