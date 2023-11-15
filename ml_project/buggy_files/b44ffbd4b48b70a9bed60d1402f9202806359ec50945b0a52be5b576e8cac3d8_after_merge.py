def __virtual__():
    '''
    Only load if elementtree xml library and boto are available.
    '''
    if not HAS_ELEMENT_TREE:
        return (False, 'Cannot load {0} state: ElementTree library unavailable'.format(__virtualname__))

    if 'boto_cfn.exists' in __salt__:
        return True
    else:
        return (False, 'Cannot load {0} state: boto_cfn module unavailable'.format(__virtualname__))