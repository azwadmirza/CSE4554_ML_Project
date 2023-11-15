def __virtual__():
    '''
    This function determines whether or not
    to make this cloud module available upon execution.
    Most often, it uses get_configured_provider() to determine
     if the necessary configuration has been set up.
    It may also check for necessary imports decide whether to load the module.
    In most cases, it will return a True or False value.
    If the name of the driver used does not match the filename,
     then that name should be returned instead of True.

    @return True|False|str
    '''
    if not HAS_VBOX:
        return False, 'The virtualbox driver cannot be loaded: \'vboxapi\' is not installed.'

    if get_configured_provider() is False:
        return False, 'The virtualbox driver cannot be loaded: \'virtualbox\' provider is not configured.'

    # If the name of the driver used does not match the filename,
    #  then that name should be returned instead of True.
    return __virtualname__