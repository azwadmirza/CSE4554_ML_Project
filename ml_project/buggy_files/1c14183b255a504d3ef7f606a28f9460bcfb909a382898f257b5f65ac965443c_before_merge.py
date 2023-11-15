def __virtual__():
    '''
    Only work on proxy
    '''
    if salt.utils.is_proxy():
        return __virtualname__
    return (False, 'The rest_package execution module failed to load: only available on proxy minions.')