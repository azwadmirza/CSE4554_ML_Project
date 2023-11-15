def __virtual__():
    '''
    Only load if requests is installed
    '''
    if HAS_LIBS:
        return 'zenoss'