def modify(name,
           bin_path=None,
           exe_args=None,
           display_name=None,
           description=None,
           service_type=None,
           start_type=None,
           start_delayed=None,
           error_control=None,
           load_order_group=None,
           dependencies=None,
           account_name=None,
           account_password=None,
           run_interactive=None):
    r'''
    Modify a service's parameters. Changes will not be made for parameters that
    are not passed.

    .. versionadded:: 2016.11.0

    Args:
        name (str):
            The name of the service. Can be found using the
            ``service.get_service_name`` function

        bin_path (str):
            The path to the service executable. Backslashes must be escaped, eg:
            ``C:\\path\\to\\binary.exe``

        exe_args (str):
            Any arguments required by the service executable

        display_name (str):
            The name to display in the service manager

        description (str):
            The description to display for the service

        service_type (str):
            Specifies the service type. Default is ``own``. Valid options are as
            follows:

            - kernel: Driver service
            - filesystem: File system driver service
            - adapter: Adapter driver service (reserved)
            - recognizer: Recognizer driver service (reserved)
            - own (default): Service runs in its own process
            - share: Service shares a process with one or more other services

        start_type (str):
            Specifies the service start type. Valid options are as follows:

            - boot: Device driver that is loaded by the boot loader
            - system: Device driver that is started during kernel initialization
            - auto: Service that automatically starts
            - manual: Service must be started manually
            - disabled: Service cannot be started

        start_delayed (bool):
            Set the service to Auto(Delayed Start). Only valid if the start_type
            is set to ``Auto``. If service_type is not passed, but the service
            is already set to ``Auto``, then the flag will be set.

        error_control (str):
            The severity of the error, and action taken, if this service fails
            to start. Valid options are as follows:

            - normal: Error is logged and a message box is displayed
            - severe: Error is logged and computer attempts a restart with the
              last known good configuration
            - critical: Error is logged, computer attempts to restart with the
              last known good configuration, system halts on failure
            - ignore: Error is logged and startup continues, no notification is
              given to the user

        load_order_group (str):
            The name of the load order group to which this service belongs

        dependencies (list):
            A list of services or load ordering groups that must start before
            this service

        account_name (str):
            The name of the account under which the service should run. For
            ``own`` type services this should be in the ``domain\username``
            format. The following are examples of valid built-in service
            accounts:

            - NT Authority\\LocalService
            - NT Authority\\NetworkService
            - NT Authority\\LocalSystem
            - .\LocalSystem

        account_password (str):
            The password for the account name specified in ``account_name``. For
            the above built-in accounts, this can be None. Otherwise a password
            must be specified.

        run_interactive (bool):
            If this setting is True, the service will be allowed to interact
            with the user. Not recommended for services that run with elevated
            privileges.

    Returns:
        dict: a dictionary of changes made

    CLI Example:

    .. code-block:: bash

        salt '*' service.modify spooler start_type=disabled
    '''
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms681987(v=vs.85).aspx
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms681988(v-vs.85).aspx
    handle_scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_CONNECT)

    try:
        handle_svc = win32service.OpenService(
            handle_scm,
            name,
            win32service.SERVICE_CHANGE_CONFIG |
            win32service.SERVICE_QUERY_CONFIG)
    except pywintypes.error as exc:
        raise CommandExecutionError(
            'Failed To Open {0}: {1}'.format(name, exc))

    config_info = win32service.QueryServiceConfig(handle_svc)

    changes = dict()

    # Input Validation
    if bin_path is not None:
        bin_path = bin_path.strip('"')
        if exe_args is not None:
            bin_path = '{0} {1}'.format(bin_path, exe_args)
        changes['BinaryPath'] = bin_path

    if service_type is not None:
        if service_type.lower() in SERVICE_TYPE:
            service_type = SERVICE_TYPE[service_type.lower()]
            if run_interactive:
                service_type = service_type | \
                               win32service.SERVICE_INTERACTIVE_PROCESS
        else:
            raise CommandExecutionError(
                'Invalid Service Type: {0}'.format(service_type))
    else:
        if run_interactive is True:
            service_type = config_info[0] | \
                           win32service.SERVICE_INTERACTIVE_PROCESS
        elif run_interactive is False:
            service_type = config_info[0] ^ \
                           win32service.SERVICE_INTERACTIVE_PROCESS
        else:
            service_type = win32service.SERVICE_NO_CHANGE

    if service_type is not win32service.SERVICE_NO_CHANGE:
        flags = list()
        for bit in SERVICE_TYPE:
            if service_type & bit:
                flags.append(SERVICE_TYPE[bit])

        changes['ServiceType'] = flags if flags else service_type

    if start_type is not None:
        if start_type.lower() in SERVICE_START_TYPE:
            start_type = SERVICE_START_TYPE[start_type.lower()]
        else:
            raise CommandExecutionError(
                'Invalid Start Type: {0}'.format(start_type))
        changes['StartType'] = SERVICE_START_TYPE[start_type]
    else:
        start_type = win32service.SERVICE_NO_CHANGE

    if error_control is not None:
        if error_control.lower() in SERVICE_ERROR_CONTROL:
            error_control = SERVICE_ERROR_CONTROL[error_control.lower()]
        else:
            raise CommandExecutionError(
                'Invalid Error Control: {0}'.format(error_control))
        changes['ErrorControl'] = SERVICE_ERROR_CONTROL[error_control]
    else:
        error_control = win32service.SERVICE_NO_CHANGE

    if account_name is not None:
        changes['ServiceAccount'] = account_name
    if account_name in ['LocalSystem', 'LocalService', 'NetworkService']:
        account_password = ''

    if account_password is not None:
        changes['ServiceAccountPassword'] = 'XXX-REDACTED-XXX'

    if load_order_group is not None:
        changes['LoadOrderGroup'] = load_order_group

    if dependencies is not None:
        changes['Dependencies'] = dependencies

    if display_name is not None:
        changes['DisplayName'] = display_name

    win32service.ChangeServiceConfig(handle_svc,
                                     service_type,
                                     start_type,
                                     error_control,
                                     bin_path,
                                     load_order_group,
                                     0,
                                     dependencies,
                                     account_name,
                                     account_password,
                                     display_name)

    if description is not None:
        win32service.ChangeServiceConfig2(
            handle_svc, win32service.SERVICE_CONFIG_DESCRIPTION, description)
        changes['Description'] = description

    if start_delayed is not None:
        # You can only set delayed start for services that are set to auto start
        # Start type 2 is Auto
        # Start type -1 is no change
        if (start_type == -1 and config_info[1] == 2) or start_type == 2:
            win32service.ChangeServiceConfig2(
                handle_svc, win32service.SERVICE_CONFIG_DELAYED_AUTO_START_INFO,
                start_delayed)
            changes['StartTypeDelayed'] = start_delayed
        else:
            changes['Warning'] = 'start_delayed: Requires start_type "auto"'

    win32service.CloseServiceHandle(handle_scm)
    win32service.CloseServiceHandle(handle_svc)

    return changes