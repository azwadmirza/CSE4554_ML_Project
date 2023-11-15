def open(uri, mode, min_part_size=WEBHDFS_MIN_PART_SIZE):
    """
    Parameters
    ----------
    min_part_size: int, optional
        For writing only.

    """
    if mode == 'rb':
        return BufferedInputBase(uri)
    elif mode == 'wb':
        return BufferedOutputBase(uri, min_part_size=min_part_size)
    else:
        raise NotImplementedError('webhdfs support for mode %r not implemented' % mode)