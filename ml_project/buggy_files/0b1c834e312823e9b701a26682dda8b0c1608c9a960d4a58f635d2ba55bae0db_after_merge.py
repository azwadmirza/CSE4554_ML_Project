def enable(name, **kwargs):
    '''
    Enable the named service to start at boot

    CLI Example:

    .. code-block:: bash

        salt '*' service.enable <service name>
    '''
    osmajor = _osrel()[0]
    if osmajor < '6':
        cmd = 'update-rc.d -f {0} defaults 99'.format(_cmd_quote(name))
    else:
        cmd = 'update-rc.d {0} enable'.format(_cmd_quote(name))
    try:
        if int(osmajor) >= 6:
            cmd = 'insserv {0} && '.format(_cmd_quote(name)) + cmd
    except ValueError:
        osrel = _osrel()
        if osrel == 'testing/unstable' or osrel == 'unstable' or osrel.endswith("/sid"):
            cmd = 'insserv {0} && '.format(_cmd_quote(name)) + cmd
    return not __salt__['cmd.retcode'](cmd, python_shell=True)