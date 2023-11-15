def __virtual__():
    '''
    Only work on systems that are a proxy minion
    '''
    if __grains__['os'] == 'proxy':
        return __virtualname__
    return (False, 'ssh_service module cannot be loaded: only available on proxy minions.')