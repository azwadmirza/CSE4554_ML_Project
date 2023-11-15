def stop(name, timeout=90):
    '''
    Stop the specified service

    Args:
        name (str): The name of the service to stop

        timeout (int):
            The time in seconds to wait for the service to stop before
            returning. Default is 90 seconds

            .. versionadded:: 2017.7.9, 2018.3.4

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt '*' service.stop <service name>
    '''
    try:
        win32serviceutil.StopService(name)
    except pywintypes.error as exc:
        if exc[0] != 1062:
            raise CommandExecutionError(
                'Failed To Stop {0}: {1}'.format(name, exc[2]))

    srv_status = _status_wait(service_name=name,
                              end_time=time.time() + int(timeout),
                              service_states=['Running', 'Stop Pending'])

    return srv_status['Status'] == 'Stopped'