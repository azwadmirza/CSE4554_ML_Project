def _clear_actions(name, location='\\'):
    r'''
    Remove all actions from the task.

    :param str name: The name of the task from which to clear all actions.

    :param str location: A string value representing the location of the task.
    Default is '\\' which is the root for the task scheduler
    (C:\Windows\System32\tasks).

    :return: True if successful, False if unsuccessful
    :rtype: bool
    '''
    # TODO: The problem is, you have to have at least one action for the task to
    # TODO: be valid, so this will always fail with a 'Required element or
    # TODO: attribute missing' error.
    # TODO: Make this an internal function that clears the functions but doesn't
    # TODO: save it. Then you can add a new function. Maybe for editing an
    # TODO: action.
    # Check for existing task
    if name not in list_tasks(location):
        return '{0} not found in {1}'.format(name, location)

    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the actions from the task
    task_folder = task_service.GetFolder(location)
    task_definition = task_folder.GetTask(name).Definition
    actions = task_definition.Actions

    actions.Clear()

    # Save the Changes
    return _save_task_definition(name=name,
                                 task_folder=task_folder,
                                 task_definition=task_definition,
                                 user_name=task_definition.Principal.UserID,
                                 password=None,
                                 logon_type=task_definition.Principal.LogonType)