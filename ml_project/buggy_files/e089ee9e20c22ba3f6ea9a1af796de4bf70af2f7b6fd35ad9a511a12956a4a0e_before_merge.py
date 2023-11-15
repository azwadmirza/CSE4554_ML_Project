def __virtual__():
    '''
    Only load if hg is available
    '''
    return 'hg' if __salt__['cmd.has_exec'](hg_binary) else False