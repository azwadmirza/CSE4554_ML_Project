def __virtual__():
    if not has_raven:
        return False
    return __virtualname__