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
        bool: ``True`` if successful, otherwise ``False``. Also returns ``True``
            if the service is already stopped

    CLI Example:

    .. code-block:: bash

        salt '*' service.stop <service name>
    '''
    try:
        win32serviceutil.StopService(name)
    except pywintypes.error as exc:
        if exc.winerror != 1062:
            raise CommandExecutionError(
                'Failed To Stop {0}: {1}'.format(name, exc.strerror))
        log.debug('Service "{0}" is not running'.format(name))

    srv_status = _status_wait(service_name=name,
                              end_time=time.time() + int(timeout),
                              service_states=['Running', 'Stop Pending'])

    return srv_status['Status'] == 'Stopped'