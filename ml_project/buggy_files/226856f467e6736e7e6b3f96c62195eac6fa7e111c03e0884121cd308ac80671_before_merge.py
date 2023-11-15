def convert_PN(byte_string,
               encodings=None):
    """Read and return string(s) as PersonName instance(s)"""

    def get_valtype(x):
        if not in_py2:
            if encodings:
                return PersonName(x, encodings).decode()
            return PersonName(x).decode()
        return PersonName(x)

    # XXX - We have to replicate MultiString functionality
    # here because we can't decode easily here since that
    # is performed in PersonNameUnicode
    ends_with1 = byte_string.endswith(b' ')
    ends_with2 = byte_string.endswith(b'\x00')
    if byte_string and (ends_with1 or ends_with2):
        byte_string = byte_string[:-1]

    splitup = byte_string.split(b"\\")

    if len(splitup) == 1:
        return get_valtype(splitup[0])
    else:
        return MultiValue(get_valtype, splitup)