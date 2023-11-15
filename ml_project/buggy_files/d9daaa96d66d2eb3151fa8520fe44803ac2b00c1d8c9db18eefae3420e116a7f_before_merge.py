def __virtual__():
    if not HAS_POSTGRES:
        return False
    return __virtualname__