def to_str(s, encoding=None):
    '''
    Given str, bytes, bytearray, or unicode (py2), return str
    '''
    if isinstance(s, str):
        return s
    if six.PY3:
        if isinstance(s, (bytes, bytearray)):
            # https://docs.python.org/3/howto/unicode.html#the-unicode-type
            # replace error with U+FFFD, REPLACEMENT CHARACTER
            return s.decode(encoding or __salt_system_encoding__, "replace")
        raise TypeError('expected str, bytes, or bytearray')
    else:
        if isinstance(s, bytearray):
            return str(s)
        if isinstance(s, unicode):  # pylint: disable=incompatible-py3-code
            return s.encode(encoding or __salt_system_encoding__)
        raise TypeError('expected str, bytearray, or unicode')