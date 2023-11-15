def _encode_nc4_variable(var):
    for coder in [coding.strings.EncodedStringCoder(allows_unicode=True),
                  coding.strings.CharacterArrayCoder()]:
        var = coder.encode(var)
    return var