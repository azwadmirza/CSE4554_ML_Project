def __virtual__():
    '''
    Set the user module if the kernel is Linux, OpenBSD, NetBSD or AIX
    '''

    if HAS_PWD and __grains__['kernel'] in ('Linux', 'OpenBSD', 'NetBSD', 'AIX'):
        return __virtualname__
    return (False, 'useradd execution module not loaded: either pwd python library not available or system not one of Linux, OpenBSD, NetBSD or AIX')