def __virtual__():
    '''
    Only works on Windows systems with the _winreg python module
    '''
    if not salt.utils.is_windows():
        return (False, 'reg execution module failed to load: '
                       'The module will only run on Windows systems')

    if not HAS_WINDOWS_MODULES:
        return (False, 'reg execution module failed to load: '
                       'One of the following libraries did not load: '
                       + '_winreg, win32gui, win32con, win32api')

    return __virtualname__