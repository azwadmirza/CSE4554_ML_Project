def convert_PN(byte_string,
               encodings=None):
    """Read and return string(s) as PersonName instance(s)"""

    def get_valtype(x):
        if not in_py2:
            return PersonName(x, encodings).decode()
        return PersonName(x, encodings)

    # XXX - We have to replicate MultiString functionality
    # here because we can't decode easily here since that
    # is performed in PersonNameUnicode
    if byte_string.endswith((b' ', b'\x00')):
        byte_string = byte_string[:-1]

    splitup = byte_string.split(b"\\")

    if len(splitup) == 1:
        return get_valtype(splitup[0])
    else:
        return MultiValue(get_valtype, splitup)