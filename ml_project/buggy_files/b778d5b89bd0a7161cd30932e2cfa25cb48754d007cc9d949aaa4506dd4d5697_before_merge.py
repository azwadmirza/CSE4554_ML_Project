def start(name, timeout=90):
    '''
    Start the specified service.

    .. warning::
        You cannot start a disabled service in Windows. If the service is
        disabled, it will be changed to ``Manual`` start.

    Args:
        name (str): The name of the service to start

        timeout (int):
            The time in seconds to wait for the service to start before
            returning. Default is 90 seconds

            .. versionadded:: 2017.7.9, 2018.3.4

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt '*' service.start <service name>
    '''
    if status(name):
        return True

    # Set the service to manual if disabled
    if disabled(name):
        modify(name, start_type='Manual')

    try:
        win32serviceutil.StartService(name)
    except pywintypes.error as exc:
        raise CommandExecutionError(
            'Failed To Start {0}: {1}'.format(name, exc[2]))

    srv_status = _status_wait(service_name=name,
                              end_time=time.time() + int(timeout),
                              service_states=['Start Pending', 'Stopped'])

    return srv_status['Status'] == 'Running'