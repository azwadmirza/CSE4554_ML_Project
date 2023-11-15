def __virtual__():
    '''
    Only work on systems that are a proxy minion
    '''
    if __grains__['os'] == 'proxy':
        return __virtualname__
    return (False, 'The rest_service execution module failed to load: only available on proxy minions.')