def __virtual__():
    '''
    Only work on systems which default to SMF
    '''
    # Don't let this work on Solaris 9 since SMF doesn't exist on it.
    enable = set((
        'Solaris',
    ))
    if __grains__['os'] in enable:
        if __grains__['os'] == 'Solaris' and __grains__['kernelrelease'] == "5.9":
            return False
        return 'service'
    return False