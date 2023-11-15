def create_task(name,
                location='\\',
                user_name='System',
                password=None,
                force=False,
                **kwargs):
    r'''
    Create a new task in the designated location. This function has many keyword
    arguments that are not listed here. For additional arguments see:

    - :py:func:`edit_task`
    - :py:func:`add_action`
    - :py:func:`add_trigger`

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

    :param bool force: If the task exists, overwrite the existing task.

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.create_task <task_name> user_name=System force=True action_type=Execute cmd='del /Q /S C:\\Temp' trigger_type=Once start_date=2016-12-1 start_time=01:00
    '''
    # Check for existing task
    if name in list_tasks(location) and not force:
        # Connect to an existing task definition
        return '{0} already exists'.format(name)

    # connect to the task scheduler
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Create a new task definition
    task_definition = task_service.NewTask(0)

    # Modify task settings
    edit_task(task_definition=task_definition,
              user_name=user_name,
              password=password,
              **kwargs)

    # Add Action
    add_action(task_definition=task_definition, **kwargs)

    # Add Trigger
    add_trigger(task_definition=task_definition, **kwargs)

    # get the folder to create the task in
    task_folder = task_service.GetFolder(location)

    # Save the task
    _save_task_definition(name=name,
                          task_folder=task_folder,
                          task_definition=task_definition,
                          user_name=task_definition.Principal.UserID,
                          password=password,
                          logon_type=task_definition.Principal.LogonType)

    # Verify task was created
    if name in list_tasks(location):
        return True
    else:
        return False