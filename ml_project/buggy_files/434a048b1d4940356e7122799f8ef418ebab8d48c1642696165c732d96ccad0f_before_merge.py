def __virtual__():
    if not HAS_PYCASSA:
        return False
    return __virtualname__