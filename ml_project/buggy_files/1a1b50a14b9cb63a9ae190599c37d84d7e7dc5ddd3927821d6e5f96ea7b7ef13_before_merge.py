def __virtual__():
    '''
    Only work on proxy
    '''
    if salt.utils.is_proxy():
        return __virtualname__
    return (False, 'THe ssh_service execution module failed to load: only works on a proxy minion.')