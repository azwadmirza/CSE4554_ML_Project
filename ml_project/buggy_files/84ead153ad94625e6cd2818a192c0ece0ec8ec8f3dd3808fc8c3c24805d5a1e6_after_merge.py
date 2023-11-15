def __virtual__():
    '''
    Only work when npm is installed.
    '''
    try:
        if salt.utils.which('npm') is not None:
            _check_valid_version(__salt__)
            return True
        else:
            return (False, 'npm execution module could not be loaded '
                           'because the npm binary could not be located')
    except CommandExecutionError as exc:
        return (False, str(exc))