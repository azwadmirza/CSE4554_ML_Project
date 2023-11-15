def __virtual__():
    '''
    Only work on systems that are a proxy minion
    '''
    try:
        if salt.utils.is_proxy() and __opts__['proxy']['proxytype'] == 'ssh_sample':
            return __virtualname__
    except KeyError:
        return (False, 'The ssh_service execution module failed to load.  Check the proxy key in pillar.')

    return (False, 'The ssh_service execution module failed to load: only works on an ssh_sample proxy minion.')