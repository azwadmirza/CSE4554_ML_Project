def delete(name, timeout=90):
    '''
    Delete the named service

    Args:

        name (str): The name of the service to delete

        timeout (int):
            The time in seconds to wait for the service to be deleted before
            returning. This is necessary because a service must be stopped
            before it can be deleted. Default is 90 seconds

            .. versionadded:: 2017.7.9, 2018.3.4

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt '*' service.delete <service name>
    '''
    handle_scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_CONNECT)

    try:
        handle_svc = win32service.OpenService(
            handle_scm, name, win32service.SERVICE_ALL_ACCESS)
    except pywintypes.error as exc:
        raise CommandExecutionError(
            'Failed to open {0}. {1}'.format(name, exc.strerror))

    try:
        win32service.DeleteService(handle_svc)
    except pywintypes.error as exc:
        raise CommandExecutionError(
            'Failed to delete {0}. {1}'.format(name, exc.strerror))
    finally:
        log.debug('Cleaning up')
        win32service.CloseServiceHandle(handle_scm)
        win32service.CloseServiceHandle(handle_svc)

    end_time = time.time() + int(timeout)
    while name in get_all() and time.time() < end_time:
        time.sleep(1)

    return name not in get_all()