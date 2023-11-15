def __virtual__():
    '''
    Only for MacOS with atrun enabled
    '''
    if not salt.utils.is_darwin():
        return (False, 'The mac_system module could not be loaded: '
                       'module only works on MacOS systems.')

    if not _atrun_enabled():
        if not _enable_atrun():
            return False, 'atrun could not be enabled on this system'

    return __virtualname__