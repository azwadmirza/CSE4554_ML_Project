def disable(name, **kwargs):  # pylint: disable=unused-argument
    '''
    Disable the named service to not start when the system boots

    CLI Example:

    .. code-block:: bash

        salt '*' service.disable <service name>
    '''
    _check_for_unit_changes(name)
    if name in _get_sysv_services():
        cmd = [_get_service_exec(), '-f', name, 'remove']
        return __salt__['cmd.retcode'](cmd,
                                       python_shell=False,
                                       ignore_retcode=True) == 0
    return __salt__['cmd.retcode'](_systemctl_cmd('disable', name),
                                   python_shell=False,
                                   ignore_retcode=True) == 0