def __virtual__():
    if salt.utils.is_windows():
        return False, 'Windows platform is not supported by this module'

    return __virtualname__