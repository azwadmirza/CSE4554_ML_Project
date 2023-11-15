def enable(name, **kwargs):  # pylint: disable=unused-argument
    '''
    Enable the named service to start when the system boots

    CLI Example:

    .. code-block:: bash

        salt '*' service.enable <service name>
    '''
    _check_for_unit_changes(name)
    unmask(name)
    if name in _get_sysv_services():
        cmd = [_get_service_exec(), '-f', name, 'defaults', '99']
        return __salt__['cmd.retcode'](cmd,
                                       python_shell=False,
                                       ignore_retcode=True) == 0
    return __salt__['cmd.retcode'](_systemctl_cmd('enable', name),
                                   python_shell=False,
                                   ignore_retcode=True) == 0