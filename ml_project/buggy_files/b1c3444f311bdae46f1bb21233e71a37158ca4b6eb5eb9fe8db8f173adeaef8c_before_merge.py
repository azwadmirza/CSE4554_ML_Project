def encode_nc3_variable(var):
    var = conventions.maybe_encode_as_char_array(var)
    data = coerce_nc3_dtype(var.data)
    attrs = encode_nc3_attrs(var.attrs)
    return Variable(var.dims, data, attrs, var.encoding)