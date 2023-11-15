def to_str(s, encoding=None, errors='strict', normalize=False):
    '''
    Given str, bytes, bytearray, or unicode (py2), return str
    '''
    def _normalize(s):
        try:
            return unicodedata.normalize('NFC', s) if normalize else s
        except TypeError:
            return s

    # This shouldn't be six.string_types because if we're on PY2 and we already
    # have a string, we should just return it.
    if isinstance(s, str):
        return _normalize(s)
    if six.PY3:
        if isinstance(s, (bytes, bytearray)):
            if encoding:
                return _normalize(s.decode(encoding, errors))
            else:
                try:
                    # Try UTF-8 first
                    return _normalize(s.decode('utf-8', errors))
                except UnicodeDecodeError:
                    # Fall back to detected encoding
                    return _normalize(s.decode(__salt_system_encoding__, errors))
        raise TypeError('expected str, bytes, or bytearray not {}'.format(type(s)))
    else:
        if isinstance(s, bytearray):
            return str(s)  # future lint: disable=blacklisted-function
        if isinstance(s, unicode):  # pylint: disable=incompatible-py3-code,undefined-variable
            if encoding:
                return _normalize(s).encode(encoding, errors)
            else:
                try:
                    # Try UTF-8 first
                    return _normalize(s).encode('utf-8', errors)
                except UnicodeEncodeError:
                    # Fall back to detected encoding
                    return _normalize(s).encode(__salt_system_encoding__, errors)
        raise TypeError('expected str, bytearray, or unicode')