def create(name,
           bin_path,
           exe_args=None,
           display_name=None,
           description=None,
           service_type='own',
           start_type='manual',
           start_delayed=False,
           error_control='normal',
           load_order_group=None,
           dependencies=None,
           account_name='.\\LocalSystem',
           account_password=None,
           run_interactive=False,
           **kwargs):
    r'''
    Create the named service.

    .. versionadded:: 2015.8.0

    Args:

        name (str):
            Specifies the service name. This is not the display_name

        bin_path (str):
            Specifies the path to the service binary file. Backslashes must be
            escaped, eg: ``C:\\path\\to\\binary.exe``

        exe_args (str):
            Any additional arguments required by the service binary.

        display_name (str):
            The name to be displayed in the service manager. If not passed, the
            ``name`` will be used

        description (str):
            A description of the service

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
            - manual (default): Service must be started manually
            - disabled: Service cannot be started

        start_delayed (bool):
            Set the service to Auto(Delayed Start). Only valid if the start_type
            is set to ``Auto``. If service_type is not passed, but the service
            is already set to ``Auto``, then the flag will be set. Default is
            ``False``

        error_control (str):
            The severity of the error, and action taken, if this service fails
            to start. Valid options are as follows:

            - normal (normal): Error is logged and a message box is displayed
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
            - .\\LocalSystem

        account_password (str):
            The password for the account name specified in ``account_name``. For
            the above built-in accounts, this can be None. Otherwise a password
            must be specified.

        run_interactive (bool):
            If this setting is True, the service will be allowed to interact
            with the user. Not recommended for services that run with elevated
            privileges.

    Returns:
        dict: A dictionary containing information about the new service

    CLI Example:

    .. code-block:: bash

        salt '*' service.create <service name> <path to exe> display_name='<display name>'
    '''
    # Deprecations
    if 'binpath' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'binpath\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'bin_path\' '
            'instead.'
        )
        if bin_path is None:
            bin_path = kwargs.pop('binpath')

    if 'DisplayName' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'DisplayName\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'display_name\' '
            'instead.'
        )
        if display_name is None:
            display_name = kwargs.pop('DisplayName')

    if display_name is None:
        display_name = name

    if 'type' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'type\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'service_type\' '
            'instead.'
        )
        if service_type is None:
            service_type = kwargs.pop('type')

    if 'start' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'start\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'start_type\' '
            'instead.'
        )
        if start_type is None:
            start_type = kwargs.pop('start')

    if 'error' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'error\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'error_control\' '
            'instead.'
        )
        if error_control is None:
            error_control = kwargs.pop('error')

    if 'group' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'group\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use '
            '\'load_order_group\' instead.'
        )
        if load_order_group is None:
            load_order_group = kwargs.pop('group')

    if 'depend' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'depend\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'dependencies\' '
            'instead.'
        )
        if dependencies is None:
            dependencies = kwargs.pop('depend')

    if 'obj' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'obj\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use \'account_name\' '
            'instead.'
        )
        if account_name is None:
            account_name = kwargs.pop('obj')

    if 'password' in kwargs:
        salt.utils.warn_until(
            'Oxygen',
            'The \'password\' argument to service.create is deprecated, and '
            'will be removed in Salt {version}. Please use '
            '\'account_password\' instead.'
        )
        if account_password is None:
            account_password = kwargs.pop('password')

    # Test if the service already exists
    if name in get_all():
        raise CommandExecutionError('Service Already Exists: {0}'.format(name))

    # shlex.quote the path to the binary
    bin_path = _cmd_quote(bin_path)
    if exe_args is not None:
        bin_path = '{0} {1}'.format(bin_path, exe_args)

    if service_type.lower() in SERVICE_TYPE:
        service_type = SERVICE_TYPE[service_type.lower()]
        if run_interactive:
            service_type = service_type | \
                           win32service.SERVICE_INTERACTIVE_PROCESS
    else:
        raise CommandExecutionError(
            'Invalid Service Type: {0}'.format(service_type))

    if start_type.lower() in SERVICE_START_TYPE:
        start_type = SERVICE_START_TYPE[start_type.lower()]
    else:
        raise CommandExecutionError(
            'Invalid Start Type: {0}'.format(start_type))

    if error_control.lower() in SERVICE_ERROR_CONTROL:
        error_control = SERVICE_ERROR_CONTROL[error_control.lower()]
    else:
        raise CommandExecutionError(
            'Invalid Error Control: {0}'.format(error_control))

    if start_delayed:
        if start_type != 2:
            raise CommandExecutionError(
                'Invalid Parameter: start_delayed requires start_type "auto"')

    if account_name in ['LocalSystem', '.\\LocalSystem',
                        'LocalService', '.\\LocalService',
                        'NetworkService', '.\\NetworkService']:
        account_password = ''

    # Connect to Service Control Manager
    handle_scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_ALL_ACCESS)

    # Create the service
    handle_svc = win32service.CreateService(handle_scm,
                                            name,
                                            display_name,
                                            win32service.SERVICE_ALL_ACCESS,
                                            service_type,
                                            start_type,
                                            error_control,
                                            bin_path,
                                            load_order_group,
                                            0,
                                            dependencies,
                                            account_name,
                                            account_password)

    if description is not None:
        win32service.ChangeServiceConfig2(
            handle_svc, win32service.SERVICE_CONFIG_DESCRIPTION, description)

    if start_delayed is not None:
        # You can only set delayed start for services that are set to auto start
        # Start type 2 is Auto
        if start_type == 2:
            win32service.ChangeServiceConfig2(
                handle_svc, win32service.SERVICE_CONFIG_DELAYED_AUTO_START_INFO,
                start_delayed)

    win32service.CloseServiceHandle(handle_scm)
    win32service.CloseServiceHandle(handle_svc)

    return info(name)