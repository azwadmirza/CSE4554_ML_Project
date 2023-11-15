def open(http_uri, mode, min_part_size=WEBHDFS_MIN_PART_SIZE):
    """
    Parameters
    ----------
    http_uri: str
        webhdfs url converted to http REST url
    min_part_size: int, optional
        For writing only.

    """
    if mode == 'rb':
        return BufferedInputBase(http_uri)
    elif mode == 'wb':
        return BufferedOutputBase(http_uri, min_part_size=min_part_size)
    else:
        raise NotImplementedError("webhdfs support for mode %r not implemented" % mode)