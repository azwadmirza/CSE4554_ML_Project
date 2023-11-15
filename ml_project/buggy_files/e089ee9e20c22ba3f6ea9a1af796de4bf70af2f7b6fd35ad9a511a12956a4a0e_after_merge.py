def __virtual__():
    '''
    Only load if hg is available
    '''
    return __salt__['cmd.has_exec'](HG_BINARY)