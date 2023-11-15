def __virtual__():
    if salt.utils.is_windows():
        return (False, 'Cannot load status module on windows')
    return __virtualname__