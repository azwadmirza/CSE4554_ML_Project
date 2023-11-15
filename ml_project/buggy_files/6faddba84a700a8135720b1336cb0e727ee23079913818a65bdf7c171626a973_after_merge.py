def _get_handle(path, mode, encoding=None):
    if py3compat.PY3:  # pragma: no cover
        if encoding:
            f = open(path, mode, encoding=encoding)
        else:
            f = open(path, mode, errors='replace')
    else:
        f = open(path, mode)
    return f