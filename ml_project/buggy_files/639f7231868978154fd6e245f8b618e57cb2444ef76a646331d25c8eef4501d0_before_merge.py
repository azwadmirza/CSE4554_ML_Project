def __virtual__():
    if not HAS_SYSLOG:
        return False
    return __virtualname__