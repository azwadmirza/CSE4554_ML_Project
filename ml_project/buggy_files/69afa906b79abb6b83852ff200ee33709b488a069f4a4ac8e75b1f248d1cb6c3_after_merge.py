def __virtual__():
    '''
    Return virtualname
    '''
    return 'nagios.list_plugins' in __salt__