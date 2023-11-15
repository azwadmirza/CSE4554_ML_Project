def _encode_nc4_variable(var):
    if var.dtype.kind == 'S':
        var = conventions.maybe_encode_as_char_array(var)
    return var