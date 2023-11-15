def seterr(*, divide=None, over=None, under=None, invalid=None, linalg=None):
    """
    TODO(hvy): Write docs.
    """
    if divide is not None:
        raise NotImplementedError()
    if over is not None:
        raise NotImplementedError()
    if under is not None:
        raise NotImplementedError()
    if invalid is not None:
        raise NotImplementedError()
    if linalg is not None:
        if linalg not in ('ignore', 'raise'):
            raise NotImplementedError()

    old_state = geterr()

    _config.divide = divide
    _config.under = under
    _config.over = over
    _config.invalid = invalid
    _config.linalg = linalg

    return old_state