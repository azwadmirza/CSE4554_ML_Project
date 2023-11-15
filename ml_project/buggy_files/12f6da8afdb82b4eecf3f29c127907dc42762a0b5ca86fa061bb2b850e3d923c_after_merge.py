def _safe_extended_peer_info(ext_peer_info):
    """
    Given a string describing peer info, return a json.twisted_dumps() safe representation.

    :param ext_peer_info: the string to convert to a dumpable format
    :return: the safe string
    """
    # First see if we can use this as-is
    if not ext_peer_info:
        ext_peer_info = u''
    try:
        return ensure_unicode(ext_peer_info, "utf8")
    except UnicodeDecodeError:
        # We might have some special unicode characters in here
        return u''.join([unichr(ord(c)) for c in ext_peer_info])