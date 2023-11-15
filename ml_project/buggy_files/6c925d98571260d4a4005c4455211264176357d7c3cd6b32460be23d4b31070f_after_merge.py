def _get_service_exec():
    '''
    Returns the path to the sysv service manager (either update-rc.d or
    chkconfig)
    '''
    contextkey = 'systemd._get_service_exec'
    if contextkey not in __context__:
        executables = ('update-rc.d', 'chkconfig')
        for executable in executables:
            service_exec = salt.utils.which(executable)
            if service_exec is not None:
                break
        else:
            raise CommandExecutionError(
                'Unable to find sysv service manager (tried {0})'.format(
                    ', '.join(executables)
                )
            )
        __context__[contextkey] = service_exec
    return __context__[contextkey]