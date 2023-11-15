def to_str(s, encoding=None, errors='strict'):
    '''
    Given str, bytes, bytearray, or unicode (py2), return str
    '''
    # This shouldn't be six.string_types because if we're on PY2 and we already
    # have a string, we should just return it.
    if isinstance(s, str):
        return s
    if six.PY3:
        if isinstance(s, (bytes, bytearray)):
            if encoding:
                return s.decode(encoding, errors)
            else:
                try:
                    # Try UTF-8 first
                    return s.decode('utf-8', errors)
                except UnicodeDecodeError:
                    # Fall back to detected encoding
                    return s.decode(__salt_system_encoding__, errors)
        raise TypeError('expected str, bytes, or bytearray not {}'.format(type(s)))
    else:
        if isinstance(s, bytearray):
            return str(s)  # future lint: disable=blacklisted-function
        if isinstance(s, unicode):  # pylint: disable=incompatible-py3-code,undefined-variable
            if encoding:
                return s.encode(encoding, errors)
            else:
                try:
                    # Try UTF-8 first
                    return s.encode('utf-8', errors)
                except UnicodeEncodeError:
                    # Fall back to detected encoding
                    return s.encode(__salt_system_encoding__, errors)
        raise TypeError('expected str, bytearray, or unicode')