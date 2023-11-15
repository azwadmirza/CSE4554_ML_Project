def __virtual__():
    '''
    Only works on Windows systems
    '''
    if salt.utils.is_windows():
        if not HAS_DEPENDENCIES:
            log.warning('Could not load dependencies for {0}'.format(__virtualname__))
        return __virtualname__
    return False, "Module win_task: module only works on Windows systems"