def __virtual__():
    '''
    Only load if requests is installed
    '''
    if HAS_LIBS:
        return __virtualname__
    else:
        return False, 'The \'{0}\' module could not be loaded: ' \
                      '\'requests\' is not installed.'.format(__virtualname__)