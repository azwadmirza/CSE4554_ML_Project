def cat(fname, fallback=_DEFAULT, binary=True):
    """Return file content.
    fallback: the value returned in case the file does not exist or
              cannot be read
    binary: whether to open the file in binary or text mode.
    """
    try:
        with open_binary(fname) if binary else open_text(fname) as f:
            return f.read().strip()
    except IOError:
        if fallback is not _DEFAULT:
            return fallback
        else:
            raise