def edit_task(name=None,
              location='\\',
              # General Tab
              user_name=None,
              password=None,
              description=None,
              enabled=None,
              hidden=None,
              # Conditions Tab
              run_if_idle=None,
              idle_duration=None,
              idle_wait_timeout=None,
              idle_stop_on_end=None,
              idle_restart=None,
              ac_only=None,
              stop_if_on_batteries=None,
              wake_to_run=None,
              run_if_network=None,
              network_id=None,
              network_name=None,
              # Settings Tab
              allow_demand_start=None,
              start_when_available=None,
              restart_every=None,
              restart_count=3,
              execution_time_limit=None,
              force_stop=None,
              delete_after=None,
              multiple_instances=None,
              **kwargs):
    r'''
    Edit the parameters of a task. Triggers and Actions cannot be edited yet.

    :param str name: The name of the task. This will be displayed in the task
        scheduler.

    :param str location: A string value representing the location in which to
        create the task. Default is '\\' which is the root for the task
        scheduler (C:\Windows\System32\tasks).

    :param str user_name: The user account under which to run the task. To
        specify the 'System' account, use 'System'. The password will be
        ignored.

    :param str password: The password to use for authentication. This should set
        the task to run whether the user is logged in or not, but is currently
        not working.

    .. note::
        The combination of user_name and password determine how the task runs.
        For example, if a username is passed without at password the task will
        only run when the user is logged in. If a password is passed as well
        the task will run whether the user is logged on or not. If you pass
        'System' as the username the task will run as the system account (the
        password parameter is ignored.

    :param str description: A string representing the text that will be
        displayed in the description field in the task scheduler.

    :param bool enabled: A boolean value representing whether or not the task is
        enabled.

    :param bool hidden: A boolean value representing whether or not the task is
        hidden.

    :param bool run_if_idle: Boolean value that indicates that the Task
        Scheduler will run the task only if the computer is in an idle state.

    :param str idle_duration: A value that indicates the amount of time that the
        computer must be in an idle state before the task is run. Valid values
        are:

    - 1 minute
    - 5 minutes
    - 10 minutes
    - 15 minutes
    - 30 minutes
    - 1 hour

    :param str idle_wait_timeout: A value that indicates the amount of time that
        the Task Scheduler will wait for an idle condition to occur. Valid
        values are:

    - Do not wait
    - 1 minute
    - 5 minutes
    - 10 minutes
    - 15 minutes
    - 30 minutes
    - 1 hour
    - 2 hours

    :param bool idle_stop_on_end: Boolean value that indicates that the Task
        Scheduler will terminate the task if the idle condition ends before the
        task is completed.

    :param bool idle_restart: Boolean value that indicates whether the task is
        restarted when the computer cycles into an idle condition more than
        once.

    :param bool ac_only: Boolean value that indicates that the Task Scheduler
        will launch the task only while on AC power.

    :param bool stop_if_on_batteries: Boolean value that indicates that the task
        will be stopped if the computer begins to run on battery power.

    :param bool wake_to_run: Boolean value that indicates that the Task
        Scheduler will wake the computer when it is time to run the task.

    :param bool run_if_network: Boolean value that indicates that the Task
        Scheduler will run the task only when a network is available.

    :param guid network_id: GUID value that identifies a network profile.

    :param str network_name: Sets the name of a network profile. The name is
        used for display purposes.

    :param bool allow_demand_start: Boolean value that indicates that the task
        can be started by using either the Run command or the Context menu.

    :param bool start_when_available: Boolean value that indicates that the Task
        Scheduler can start the task at any time after its scheduled time has
        passed.

    :param restart_every: A value that specifies the interval between task
        restart attempts. Valid values are:

    - False (to disable)
    - 1 minute
    - 5 minutes
    - 10 minutes
    - 15 minutes
    - 30 minutes
    - 1 hour
    - 2 hours

    :param int restart_count: The number of times the Task Scheduler will
        attempt to restart the task. Valid values are integers 1 - 999.

    :param execution_time_limit: The amount of time allowed to complete the
        task. Valid values are:

    - False (to disable)
    - 1 hour
    - 2 hours
    - 4 hours
    - 8 hours
    - 12 hours
    - 1 day
    - 3 days

    :param bool force_stop: Boolean value that indicates that the task may be
        terminated by using TerminateProcess.

    :param delete_after: The amount of time that the Task Scheduler will
        wait before deleting the task after it expires. Requires a trigger with
        an expiration date. Valid values are:

    - False (to disable)
    - Immediately
    - 30 days
    - 90 days
    - 180 days
    - 365 days

    :param str multiple_instances: Sets the policy that defines how the Task
        Scheduler deals with multiple instances of the task. Valid values are:

    - Parallel
    - Queue
    - No New Instance
    - Stop Existing

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.edit_task <task_name> description='This task is awesome'
    '''
    # TODO: Add more detailed return for items changed

    # Check for passed task_definition
    # If not passed, open a task definition for an existing task
    save_definition = False
    if kwargs.get('task_definition', False):
        task_definition = kwargs.get('task_definition')
    else:
        save_definition = True

        # Make sure a name was passed
        if not name:
            return 'Required parameter "name" not passed'

        # Make sure task exists to modify
        if name in list_tasks(location):

            # Connect to the task scheduler
            pythoncom.CoInitialize()
            task_service = win32com.client.Dispatch("Schedule.Service")
            task_service.Connect()

            # get the folder to create the task in
            task_folder = task_service.GetFolder(location)

            # Connect to an existing task definition
            task_definition = task_folder.GetTask(name).Definition

        else:
            # Not found and create_new not set, return not found
            return '{0} not found'.format(name)

    # General Information
    if save_definition:
        task_definition.RegistrationInfo.Author = 'Salt Minion'
        task_definition.RegistrationInfo.Source = "Salt Minion Daemon"

    if description is not None:
        task_definition.RegistrationInfo.Description = description

    # General Information: Security Options
    if user_name:
        # Determine logon type
        if user_name.lower() == 'system':
            logon_type = TASK_LOGON_SERVICE_ACCOUNT
            user_name = 'SYSTEM'
            password = None
        else:
            task_definition.Principal.Id = user_name
            if password:
                logon_type = TASK_LOGON_PASSWORD
            else:
                logon_type = TASK_LOGON_INTERACTIVE_TOKEN

        task_definition.Principal.UserID = user_name
        task_definition.Principal.DisplayName = user_name
        task_definition.Principal.LogonType = logon_type
        task_definition.Principal.RunLevel = TASK_RUNLEVEL_HIGHEST
    else:
        user_name = None
        password = None

    # Settings
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa383480(v=vs.85).aspx
    if enabled is not None:
        task_definition.Settings.Enabled = enabled
    # Settings: General Tab
    if hidden is not None:
        task_definition.Settings.Hidden = hidden

    # Settings: Conditions Tab (Idle)
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa380669(v=vs.85).aspx
    if run_if_idle is not None:
        task_definition.Settings.RunOnlyIfIdle = run_if_idle

    if task_definition.Settings.RunOnlyIfIdle:
        if idle_stop_on_end is not None:
            task_definition.Settings.IdleSettings.StopOnIdleEnd = idle_stop_on_end
        if idle_restart is not None:
            task_definition.Settings.IdleSettings.RestartOnIdle = idle_restart
        if idle_duration is not None:
            if idle_duration in duration:
                task_definition.Settings.IdleSettings.IdleDuration = _lookup_first(duration, idle_duration)
            else:
                return 'Invalid value for "idle_duration"'
        if idle_wait_timeout is not None:
            if idle_wait_timeout in duration:
                task_definition.Settings.IdleSettings.WaitTimeout = _lookup_first(duration, idle_wait_timeout)
            else:
                return 'Invalid value for "idle_wait_timeout"'

    # Settings: Conditions Tab (Power)
    if ac_only is not None:
        task_definition.Settings.DisallowStartIfOnBatteries = ac_only
    if stop_if_on_batteries is not None:
        task_definition.Settings.StopIfGoingOnBatteries = stop_if_on_batteries
    if wake_to_run is not None:
        task_definition.Settings.WakeToRun = wake_to_run

    # Settings: Conditions Tab (Network)
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa382067(v=vs.85).aspx
    if run_if_network is not None:
        task_definition.Settings.RunOnlyIfNetworkAvailable = run_if_network
    if task_definition.Settings.RunOnlyIfNetworkAvailable:
        if network_id:
            task_definition.Settings.NetworkSettings.Id = network_id
        if network_name:
            task_definition.Settings.NetworkSettings.Name = network_name

    # Settings: Settings Tab
    if allow_demand_start is not None:
        task_definition.Settings.AllowDemandStart = allow_demand_start
    if start_when_available is not None:
        task_definition.Settings.StartWhenAvailable = start_when_available
    if restart_every is not None:
        if restart_every is False:
            task_definition.Settings.RestartInterval = ''
        else:
            if restart_every in duration:
                task_definition.Settings.RestartInterval = _lookup_first(duration, restart_every)
            else:
                return 'Invalid value for "restart_every"'
    if task_definition.Settings.RestartInterval:
        if restart_count is not None:
            if restart_count in range(1, 999):
                task_definition.Settings.RestartCount = restart_count
            else:
                return '"restart_count" must be a value between 1 and 999'
    if execution_time_limit is not None:
        if execution_time_limit is False:
            task_definition.Settings.ExecutionTimeLimit = 'PT0S'
        else:
            if execution_time_limit in duration:
                task_definition.Settings.ExecutionTimeLimit = _lookup_first(duration, execution_time_limit)
            else:
                return 'Invalid value for "execution_time_limit"'
    if force_stop is not None:
        task_definition.Settings.AllowHardTerminate = force_stop
    if delete_after is not None:
        # TODO: Check triggers for end_boundary
        if delete_after is False:
            task_definition.Settings.DeleteExpiredTaskAfter = ''
        if delete_after in duration:
            task_definition.Settings.DeleteExpiredTaskAfter = _lookup_first(duration, delete_after)
        else:
            return 'Invalid value for "delete_after"'
    if multiple_instances is not None:
        task_definition.Settings.MultipleInstances = instances[multiple_instances]

    # Save the task
    if save_definition:
        # Save the Changes
        return _save_task_definition(name=name,
                                     task_folder=task_folder,
                                     task_definition=task_definition,
                                     user_name=user_name,
                                     password=password,
                                     logon_type=task_definition.Principal.LogonType)