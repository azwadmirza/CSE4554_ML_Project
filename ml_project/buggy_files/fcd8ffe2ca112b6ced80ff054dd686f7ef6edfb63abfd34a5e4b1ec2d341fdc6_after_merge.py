def disable(name, **kwargs):  # pylint: disable=unused-argument
    '''
    Disable the named service to not start when the system boots

    CLI Example:

    .. code-block:: bash

        salt '*' service.disable <service name>
    '''
    _check_for_unit_changes(name)
    if name in _get_sysv_services():
        service_exec = _get_service_exec()
        if service_exec.endswith('/update-rc.d'):
            cmd = [service_exec, '-f', name, 'remove']
        elif service_exec.endswith('/chkconfig'):
            cmd = [service_exec, name, 'off']
        return __salt__['cmd.retcode'](cmd,
                                       python_shell=False,
                                       ignore_retcode=True) == 0
    return __salt__['cmd.retcode'](_systemctl_cmd('disable', name),
                                   python_shell=False,
                                   ignore_retcode=True) == 0