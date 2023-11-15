def __virtual__():
    if not HAS_SYSLOG:
        return False, 'Could not import syslog returner; syslog is not installed.'
    return __virtualname__