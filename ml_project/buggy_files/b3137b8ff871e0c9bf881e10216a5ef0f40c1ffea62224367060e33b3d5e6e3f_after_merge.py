def _decode(value, fallback=None):
    """Decode the value using the specified encoding.

    It fallbacks to the specified encoding or SYS_ENCODING if not defined

    :param value: the value to be encoded
    :type value: str
    :param encoding: the encoding to be used
    :type encoding: str
    :param fallback: the fallback encoding to be used
    :type fallback: str
    :return: the decoded value
    :rtype: unicode
    """
    if isinstance(value, text_type):
        return value

    encoding = 'utf-8' if os.name != 'nt' else app.SYS_ENCODING

    try:
        return text_type(value, encoding)
    except UnicodeDecodeError:
        logger.debug(u'Failed to decode to %s, falling back to %s: %r',
                     encoding, fallback or app.SYS_ENCODING, value)
        return text_type(value, fallback or app.SYS_ENCODING)