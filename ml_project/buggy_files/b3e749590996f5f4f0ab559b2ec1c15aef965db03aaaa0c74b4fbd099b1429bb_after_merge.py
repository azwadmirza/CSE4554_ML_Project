def interfaces():
    '''
    Return a dictionary of information about all the interfaces on the minion
    '''
    if salt.utils.platform.is_windows():
        return win_interfaces()
    elif salt.utils.platform.is_netbsd():
        return netbsd_interfaces()
    else:
        return linux_interfaces()