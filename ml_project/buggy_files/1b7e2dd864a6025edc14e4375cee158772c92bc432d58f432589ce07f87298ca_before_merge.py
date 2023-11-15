def __virtual__():
    if not HAS_KAFKA:
        return False
    return __virtualname__