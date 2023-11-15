def __virtual__():
    '''
    Only load this module if the ca config options are set
    '''
    if HAS_SSL:
        return True
    return False, ['PyOpenSSL must be installed before this module can be used.']