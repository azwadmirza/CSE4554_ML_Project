def clear_triggers(name, location='\\'):
    r'''
    Remove all triggers from the task.

    :param str name: The name of the task from which to clear all triggers.

    :param str location: A string value representing the location of the task.
        Default is '\\' which is the root for the task scheduler
        (C:\Windows\System32\tasks).

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.clear_trigger <task_name>
    '''
    # Check for existing task
    if name not in list_tasks(location):
        return '{0} not found in {1}'.format(name, location)

    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the triggers from the task
    task_folder = task_service.GetFolder(location)
    task_definition = task_folder.GetTask(name).Definition
    triggers = task_definition.Triggers

    triggers.Clear()

    # Save the Changes
    return _save_task_definition(name=name,
                                 task_folder=task_folder,
                                 task_definition=task_definition,
                                 user_name=task_definition.Principal.UserID,
                                 password=None,
                                 logon_type=task_definition.Principal.LogonType)