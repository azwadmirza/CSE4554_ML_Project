def __virtual__():
    if not HAS_REDIS:
        return False
    return __virtualname__