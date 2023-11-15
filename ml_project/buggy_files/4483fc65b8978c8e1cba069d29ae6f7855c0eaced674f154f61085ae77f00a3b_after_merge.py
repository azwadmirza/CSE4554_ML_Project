def __virtual__():
    '''
    Only return if python-etcd is installed
    '''
    if HAS_LIBS:
        return __virtualname__

    return False, 'Could not import etcd returner; python-etcd is not installed.'