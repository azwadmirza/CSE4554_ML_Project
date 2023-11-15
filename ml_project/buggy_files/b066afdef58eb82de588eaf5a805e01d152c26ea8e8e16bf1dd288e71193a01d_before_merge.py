def __virtual__():
    if not HAS_MEMCACHE:
        return False
    return __virtualname__