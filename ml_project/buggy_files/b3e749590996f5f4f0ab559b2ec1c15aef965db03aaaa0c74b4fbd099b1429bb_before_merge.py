def interfaces():
    '''
    Return a dictionary of information about all the interfaces on the minion
    '''
    if salt.utils.platform.is_windows():
        return win_interfaces()
    else:
        return linux_interfaces()