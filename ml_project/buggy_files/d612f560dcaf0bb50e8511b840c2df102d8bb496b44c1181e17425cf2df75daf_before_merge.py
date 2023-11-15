def restart(name):
    '''
    Restart the named service

    CLI Example:

    .. code-block:: bash

        salt '*' service.restart <service name>
    '''
    stopcmd = 'sc stop "{0}"'.format(name)
    __salt__['cmd.run'](stopcmd)
    servicestate = status(name)
    while True:
        servicestate = status(name)
        if servicestate == '':
            break
        else:
            time.sleep(2)
    startcmd = 'sc start "{0}"'.format(name)
    return not __salt__['cmd.retcode'](startcmd)