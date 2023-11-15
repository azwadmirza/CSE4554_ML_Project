def encode_nc3_variable(var):
    for coder in [coding.strings.EncodedStringCoder(allows_unicode=False),
                  coding.strings.CharacterArrayCoder()]:
        var = coder.encode(var)
    data = coerce_nc3_dtype(var.data)
    attrs = encode_nc3_attrs(var.attrs)
    return Variable(var.dims, data, attrs, var.encoding)