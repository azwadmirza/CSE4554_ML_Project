def get_dependencies():
    '''
    Warn if dependencies aren't met.
    '''
    if LIBCLOUD_IMPORT_ERROR:
        log.error("Failure when importing LibCloud: ", exc_info=LIBCLOUD_IMPORT_ERROR)
        log.error("Note: The libcloud dependency is called 'apache-libcloud' on PyPi/pip.")
    return config.check_driver_dependencies(
        __virtualname__,
        {'libcloud': HAS_LIBCLOUD}
    )