def __virtual__():
    '''
    Only load if boto is available.
    '''
    return 'boto_cfn.exists' in __salt__