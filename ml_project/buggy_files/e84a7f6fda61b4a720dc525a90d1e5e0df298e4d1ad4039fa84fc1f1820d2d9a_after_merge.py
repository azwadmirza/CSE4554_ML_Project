def _encode(value, fallback=None):
    """Encode the value using the specified encoding.

    It fallbacks to the specified encoding or SYS_ENCODING if not defined

    :param value: the value to be encoded
    :type value: str
    :param encoding: the encoding to be used
    :type encoding: str
    :param fallback: the fallback encoding to be used
    :type fallback: str
    :return: the encoded value
    :rtype: str
    """
    if isinstance(value, binary_type):
        return value

    encoding = 'utf-8' if os.name != 'nt' else app.SYS_ENCODING

    try:
        return value.encode(encoding)
    except UnicodeEncodeError:
        logger.debug(u'Failed to encode to %s, falling back to %s: %r',
                     encoding, fallback or app.SYS_ENCODING, value)
        return value.encode(fallback or app.SYS_ENCODING)