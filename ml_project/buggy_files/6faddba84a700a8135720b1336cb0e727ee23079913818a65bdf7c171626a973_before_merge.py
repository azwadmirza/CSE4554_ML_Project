def _get_handle(path, mode, encoding=None):
    if py3compat.PY3:  # pragma: no cover
        f = open(path, mode, encoding=encoding)
    else:
        f = open(path, mode)
    return f